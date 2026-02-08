"""
MediaService for handling media file operations with Cloudflare R2 and ImageKit.io.
"""

import logging
import mimetypes
import os
from urllib.parse import urljoin

from apps.mediafile.models import MediaFile, MediaFolder

from django.conf import settings
from django.utils.text import slugify

from ..exceptions import FileTooLargeError, InvalidFileTypeError, MediaUploadError, StorageError

logger = logging.getLogger(__name__)


class MediaService:
    """
    Service class for handling media file operations with Cloudflare R2 and ImageKit.io
    """

    # Allowed MIME types and their corresponding resource types
    ALLOWED_MIME_TYPES = {
        "image": [
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "image/svg+xml",
            "image/tiff",
            "image/bmp",
        ],
        "video": [
            "video/mp4",
            "video/webm",
            "video/ogg",
            "video/quicktime",
            "video/x-msvideo",
            "video/x-ms-wmv",
            "video/x-matroska",
        ],
        "document": [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "text/plain",
            "text/csv",
            "application/rtf",
            "application/zip",
            "application/x-rar-compressed",
            "application/x-7z-compressed",
            "application/x-tar",
            "application/x-gzip",
        ],
    }

    def __init__(self):
        """Initialize R2 and ImageKit clients"""
        try:
            import boto3

            self.s3_client = boto3.client(
                "s3",
                endpoint_url=getattr(settings, "AWS_S3_ENDPOINT_URL", None),
                aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None),
                aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None),
                region_name="auto",
                config=boto3.session.Config(signature_version="s3v4"),
            )
        except ImportError:
            logger.warning("boto3 not installed, R2 storage will not work")
            self.s3_client = None

        try:
            from imagekitio import ImageKit

            self.imagekit = ImageKit(
                private_key=getattr(settings, "IMAGEKIT_PRIVATE_KEY", None),
                public_key=getattr(settings, "IMAGEKIT_PUBLIC_KEY", None),
                url_endpoint=getattr(settings, "IMAGEKIT_URL_ENDPOINT", None),
            )
        except ImportError:
            logger.warning("imagekitio not installed, ImageKit features will not work")
            self.imagekit = None

    def upload_file(
        self,
        store,
        file_obj,
        uploaded_by=None,
        folder=None,
        resource_type=None,
        alt_text="",
        description="",
        metadata=None,
    ):
        """
        Upload a file to R2 and create a MediaFile record

        Args:
            store: Store instance
            file_obj: File object or InMemoryUploadedFile
            uploaded_by: User instance (optional)
            folder: Optional MediaFolder instance
            resource_type: Optional resource type override
            alt_text: Alt text for images
            description: File description
            metadata: Optional dict of metadata

        Returns:
            MediaFile: Created media file instance

        Raises:
            InvalidFileTypeError: If file type is not allowed
            FileTooLargeError: If file exceeds size limits
            StorageError: If upload to R2 fails
            MediaUploadError: For other upload errors
        """
        try:
            # Validate file
            if not file_obj or not hasattr(file_obj, "name"):
                raise MediaUploadError("Invalid file object")

            # Get file metadata
            file_name = file_obj.name
            file_size = file_obj.size
            mime_type = getattr(
                file_obj,
                "content_type",
                mimetypes.guess_type(file_name)[0] or "application/octet-stream",
            )

            # Determine resource type and validate
            if resource_type:
                determined_type = resource_type
            else:
                determined_type = self._get_resource_type(mime_type, file_name)

            if not determined_type:
                raise InvalidFileTypeError(
                    f"File type {mime_type} is not allowed. "
                    f"Allowed types: {', '.join(self.ALLOWED_MIME_TYPES.keys())}"
                )

            # Validate file size
            max_size = getattr(MediaFile, f"{determined_type.upper()}_MAX_SIZE")
            if file_size > max_size:
                raise FileTooLargeError(
                    f"{determined_type.capitalize()} exceeds maximum size of "
                    f"{max_size / (1024 * 1024):.1f}MB"
                )

            # Generate storage path
            file_extension = os.path.splitext(file_name)[1].lower()
            base_filename = os.path.splitext(os.path.basename(file_name))[0]
            safe_filename = f"{slugify(base_filename)}{file_extension}"

            # Create folder path
            folder_path = f"store_{store.id}/media"
            if folder:
                folder_path = f"{folder_path}/{folder.path}"

            # Upload to R2
            r2_key = f"{folder_path}/{safe_filename}"

            if self.s3_client:
                try:
                    if hasattr(file_obj, "temporary_file_path"):
                        # File is stored on disk
                        self.s3_client.upload_file(
                            file_obj.temporary_file_path(),
                            getattr(settings, "AWS_STORAGE_BUCKET_NAME", ""),
                            r2_key,
                            ExtraArgs={
                                "ContentType": mime_type,
                                "ACL": (
                                    "public-read"
                                    if determined_type in ["image", "video"]
                                    else "private"
                                ),
                            },
                        )
                    else:
                        # File is in memory
                        self.s3_client.upload_fileobj(
                            file_obj,
                            getattr(settings, "AWS_STORAGE_BUCKET_NAME", ""),
                            r2_key,
                            ExtraArgs={
                                "ContentType": mime_type,
                                "ACL": (
                                    "public-read"
                                    if determined_type in ["image", "video"]
                                    else "private"
                                ),
                            },
                        )
                except Exception as e:
                    logger.error(f"Failed to upload to R2: {str(e)}")
                    raise StorageError("Failed to upload file to storage")

            # Get file dimensions if image
            width, height = None, None
            if determined_type == "image":
                try:
                    from PIL import Image

                    if hasattr(file_obj, "temporary_file_path"):
                        with Image.open(file_obj.temporary_file_path()) as img:
                            width, height = img.size
                    else:
                        # For in-memory files, we need to seek to start
                        file_obj.seek(0)
                        with Image.open(file_obj) as img:
                            width, height = img.size
                        # Reset file pointer for potential reuse
                        file_obj.seek(0)
                except Exception as e:
                    logger.warning(f"Could not get image dimensions: {str(e)}")

            # Upload to ImageKit if it's an image
            imagekit_id = None
            if determined_type == "image" and self.imagekit:
                try:
                    # Reset file pointer for ImageKit upload
                    file_obj.seek(0)
                    result = self.imagekit.upload_file(
                        file=file_obj,
                        file_name=safe_filename,
                        use_unique_file_name=False,
                    )
                    imagekit_id = result.file_id
                except Exception as e:
                    logger.warning(f"Failed to upload to ImageKit: {str(e)}")

            # Create MediaFile record directly
            media_file = MediaFile.objects.create(
                original_filename=file_name,
                file_extension=file_extension.lstrip("."),
                file_size=file_size,
                mime_type=mime_type,
                resource_type=determined_type,
                storage_path=r2_key,
                imagekit_id=imagekit_id,
                width=width,
                height=height,
                alt_text=alt_text,
                description=description,
                metadata=metadata or {},
                store=store,
                folder=folder,
                uploaded_by=uploaded_by,
            )

            # Log the upload
            self._log_media_action(
                action="UPLOAD",
                user=uploaded_by,
                store=store,
                media_file=media_file,
                metadata={
                    "file_size": file_size,
                    "mime_type": mime_type,
                    "folder": folder.name if folder else None,
                },
            )

            return media_file

        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            if not isinstance(e, (InvalidFileTypeError, FileTooLargeError, StorageError)):
                raise MediaUploadError(f"Failed to upload file: {str(e)}")
            raise

    def delete_media(self, media_file, user):
        """
        Delete a media file from storage and database

        Args:
            media_file: MediaFile instance to delete
            user: User performing the deletion

        Returns:
            bool: True if deletion was successful
        """
        try:
            store = media_file.store

            # Delete from R2
            if self.s3_client:
                try:
                    self.s3_client.delete_object(
                        Bucket=getattr(settings, "AWS_STORAGE_BUCKET_NAME", ""),
                        Key=media_file.storage_path,
                    )
                except Exception as e:
                    logger.error(f"Failed to delete from R2: {str(e)}")
                    # Continue with DB deletion even if R2 delete fails

            # Delete from ImageKit if it exists
            if media_file.imagekit_id and self.imagekit:
                try:
                    self.imagekit.delete_file(media_file.imagekit_id)
                except Exception as e:
                    logger.error(f"Failed to delete from ImageKit: {str(e)}")

            # Log before deletion (to have the ID)
            self._log_media_action(action="DELETE", user=user, store=store, media_file=media_file)

            # Delete from database directly
            media_file.delete()

            return True

        except Exception as e:
            logger.error(f"Error deleting media file {media_file.id}: {str(e)}")
            raise MediaUploadError(f"Failed to delete media file: {str(e)}")

    def get_media_url(self, media_file, transformation=None):
        """
        Get URL for a media file with optional transformations

        Args:
            media_file: MediaFile instance
            transformation: Optional transformation string for ImageKit

        Returns:
            str: Public URL to the media file
        """
        if not media_file:
            return None

        # For private files, generate a presigned URL
        if media_file.resource_type not in ["image", "video"]:
            return self.get_presigned_url(media_file)

        # For public files, use ImageKit if available
        if media_file.imagekit_id and self.imagekit:
            try:
                url = f"{getattr(settings, 'IMAGEKIT_URL', '')}/{media_file.storage_path}"
                if transformation:
                    url = f"{url}?tr={transformation}"
                return url
            except Exception as e:
                logger.warning(f"Failed to get ImageKit URL: {str(e)}")
                # Fall back to R2 URL

        # Fallback to R2 public URL
        return f"{getattr(settings, 'AWS_S3_PUBLIC_URL', '')}/{media_file.storage_path}"

    def get_presigned_url(self, media_file, expires_in=3600):
        """
        Generate a presigned URL for private file access

        Args:
            media_file: MediaFile instance
            expires_in: Expiration time in seconds

        Returns:
            str: Presigned URL or None if not applicable
        """
        if not self.s3_client:
            return None

        try:
            response = self.s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": getattr(settings, "AWS_STORAGE_BUCKET_NAME", ""),
                    "Key": media_file.storage_path,
                    "ResponseContentType": media_file.mime_type,
                    "ResponseContentDisposition": f'attachment; filename="{media_file.original_filename}"',
                },
                ExpiresIn=expires_in,
            )
            return response
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            return None

    def get_thumbnail_url(self, media_file, width=200, height=200, crop="fill"):
        """
        Get a thumbnail URL for a media file

        Args:
            media_file: MediaFile instance
            width: Thumbnail width in pixels
            height: Thumbnail height in pixels
            crop: Crop mode (fill, fit, etc.)

        Returns:
            str: Thumbnail URL or None if not applicable
        """
        if not media_file or media_file.resource_type not in ["image", "video"]:
            return None

        transformation = f"w-{width},h-{height},c-{crop}"
        return self.get_media_url(media_file, transformation)

    def _determine_resource_type(self, mime_type, file_name):
        """
        Determine resource type from MIME type and file name

        Args:
            mime_type: MIME type string
            file_name: Original file name

        Returns:
            str: Resource type (image, video, document, other) or None if not allowed
        """
        if not mime_type:
            # Try to determine from file extension as fallback
            ext = os.path.splitext(file_name)[1].lower().lstrip(".")
            mime_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"

        for resource_type, allowed_mimes in self.ALLOWED_MIME_TYPES.items():
            if mime_type in allowed_mimes:
                return resource_type

        return None

    def _get_resource_type(self, mime_type, file_name):
        """Alias for _determine_resource_type for backward compatibility"""
        return self._determine_resource_type(mime_type, file_name)

    @staticmethod
    def validate_file_upload(file_obj, store, folder=None):
        """
        Validate file upload before processing

        Args:
            file_obj: File object to validate
            store: Store instance
            folder: Optional folder instance

        Returns:
            dict: Validation result with errors if any
        """
        errors = {}

        if not file_obj or not hasattr(file_obj, "name"):
            errors["file"] = "Invalid file object"
            return {"valid": False, "errors": errors}

        # Get file metadata
        file_name = file_obj.name
        file_size = file_obj.size
        mime_type = getattr(
            file_obj,
            "content_type",
            mimetypes.guess_type(file_name)[0] or "application/octet-stream",
        )

        # Validate file size
        if file_size <= 0:
            errors["file_size"] = "File is empty"

        # Check store quota
        current_usage = (
            MediaFile.objects.filter(store=store).aggregate(total=models.Sum("file_size"))["total"]
            or 0
        )

        max_storage = getattr(settings, "MAX_STORE_STORAGE", 5 * 1024 * 1024 * 1024)  # 5GB default
        if current_usage + file_size > max_storage:
            errors[
                "quota"
            ] = f"Storage quota exceeded. Available: {max_storage - current_usage} bytes"

        # Validate file type
        media_service = MediaService()
        resource_type = media_service._determine_resource_type(mime_type, file_name)
        if not resource_type:
            errors["file_type"] = f"File type {mime_type} is not allowed"

        # Validate folder permissions
        if folder and folder.store != store:
            errors["folder"] = "Folder does not belong to this store"

        # Validate filename
        if len(file_name) > 255:
            errors["filename"] = "Filename too long (max 255 characters)"

        # Check for duplicate files in same folder
        if folder:
            existing_files = MediaFile.objects.filter(
                store=store, folder=folder, original_filename=file_name
            )
        else:
            existing_files = MediaFile.objects.filter(
                store=store, folder__isnull=True, original_filename=file_name
            )

        if existing_files.exists():
            errors["duplicate"] = "File with this name already exists in this location"

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "resource_type": resource_type,
        }

    @staticmethod
    def bulk_upload_files(store, files_data, uploaded_by=None):
        """
        Upload multiple files in bulk

        Args:
            store: Store instance
            files_data: List of tuples (file_obj, optional_folder, metadata)
            uploaded_by: User uploading the files

        Returns:
            dict: Results with uploaded files and any errors
        """
        results = {"uploaded": [], "errors": []}
        media_service = MediaService()

        for i, (file_obj, folder, metadata) in enumerate(files_data):
            try:
                # Validate each file
                validation = MediaService.validate_file_upload(file_obj, store, folder)
                if not validation["valid"]:
                    results["errors"].append(
                        {
                            "index": i,
                            "filename": file_obj.name,
                            "errors": validation["errors"],
                        }
                    )
                    continue

                # Upload the file
                media_file = media_service.upload_file(
                    store=store,
                    file_obj=file_obj,
                    uploaded_by=uploaded_by,
                    folder=folder,
                    **(metadata or {}),
                )
                results["uploaded"].append(media_file)

            except Exception as e:
                results["errors"].append({"index": i, "filename": file_obj.name, "error": str(e)})

        return results

    @staticmethod
    def get_media_files_by_type(store, resource_type, folder=None):
        """
        Get media files filtered by type

        Args:
            store: Store instance
            resource_type: Resource type (image, video, document)
            folder: Optional folder to filter by

        Returns:
            QuerySet: Filtered media files
        """
        filters = {"store": store, "resource_type": resource_type}

        if folder:
            filters["folder"] = folder
        else:
            filters["folder__isnull"] = True

        return MediaFile.objects.filter(**filters).order_by("-created_at")

    @staticmethod
    def search_media_files(store, query, resource_type=None, folder=None):
        """
        Search media files by filename, alt text, or description

        Args:
            store: Store instance
            query: Search query string
            resource_type: Optional resource type filter
            folder: Optional folder filter

        Returns:
            QuerySet: Search results
        """
        filters = {"store": store}

        if resource_type:
            filters["resource_type"] = resource_type

        if folder:
            filters["folder"] = folder
        else:
            filters["folder__isnull"] = True

        from django.db.models import Q

        return (
            MediaFile.objects.filter(**filters)
            .filter(
                Q(original_filename__icontains=query)
                | Q(alt_text__icontains=query)
                | Q(description__icontains=query)
            )
            .order_by("-created_at")
        )

    @staticmethod
    def get_storage_usage(store):
        """
        Get storage usage statistics for a store

        Args:
            store: Store instance

        Returns:
            dict: Storage usage data
        """
        from django.db.models import Count, Sum

        files = MediaFile.objects.filter(store=store)

        # Total usage
        total_usage = files.aggregate(total_size=Sum("file_size"), total_files=Count("id"))

        # Usage by type
        usage_by_type = (
            files.values("resource_type")
            .annotate(size=Sum("file_size"), count=Count("id"))
            .order_by("-size")
        )

        # Usage by folder
        usage_by_folder = (
            files.values("folder__name")
            .annotate(size=Sum("file_size"), count=Count("id"))
            .order_by("-size")
        )

        # Largest files
        largest_files = files.order_by("-file_size")[:10]

        max_storage = getattr(settings, "MAX_STORE_STORAGE", 5 * 1024 * 1024 * 1024)

        return {
            "total_size": total_usage["total_size"] or 0,
            "total_files": total_usage["total_files"] or 0,
            "max_storage": max_storage,
            "usage_percentage": round((total_usage["total_size"] or 0) / max_storage * 100, 2),
            "usage_by_type": list(usage_by_type),
            "usage_by_folder": list(usage_by_folder),
            "largest_files": [
                {
                    "id": f.id,
                    "filename": f.original_filename,
                    "size": f.file_size,
                    "resource_type": f.resource_type,
                }
                for f in largest_files
            ],
        }

    @staticmethod
    def optimize_images(store, quality=80, max_width=1920, max_height=1080):
        """
        Optimize all images in a store to reduce file size

        Args:
            store: Store instance
            quality: JPEG quality (1-100)
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels

        Returns:
            dict: Optimization results
        """
        images = MediaFile.objects.filter(store=store, resource_type="image")
        results = {"optimized": 0, "errors": 0, "total_size_saved": 0}

        for image in images:
            try:
                # This would integrate with ImageKit or similar service
                # For now, just log what would be optimized
                logger.info(
                    f"Would optimize image {image.original_filename} "
                    f"({image.file_size} bytes) to quality {quality}"
                )
                results["optimized"] += 1

            except Exception as e:
                logger.error(f"Failed to optimize image {image.id}: {str(e)}")
                results["errors"] += 1

        return results

    @staticmethod
    def generate_presigned_upload_url(store, filename, resource_type, folder=None, expires_in=3600):
        """
        Generate a presigned URL for direct upload to storage

        Args:
            store: Store instance
            filename: Desired filename
            resource_type: Resource type
            folder: Optional folder
            expires_in: URL expiration time in seconds

        Returns:
            dict: Presigned URL and upload info
        """
        media_service = MediaService()

        if not media_service.s3_client:
            raise ValueError("S3 client not available")

        # Generate safe filename
        file_extension = os.path.splitext(filename)[1].lower()
        base_filename = os.path.splitext(os.path.basename(filename))[0]
        safe_filename = (
            f"{slugify(base_filename)}_{timezone.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
        )

        # Create folder path
        folder_path = f"store_{store.id}/media"
        if folder:
            folder_path = f"{folder_path}/{folder.path}"

        r2_key = f"{folder_path}/{safe_filename}"

        # Generate presigned URL
        response = media_service.s3_client.generate_presigned_post(
            Bucket=getattr(settings, "AWS_STORAGE_BUCKET_NAME", ""),
            Key=r2_key,
            ExpiresIn=expires_in,
            Conditions=[
                {"acl": ("public-read" if resource_type in ["image", "video"] else "private")},
                [
                    "content-length-range",
                    1,
                    getattr(MediaFile, f"{resource_type.upper()}_MAX_SIZE"),
                ],
            ],
        )

        return {
            "url": response["url"],
            "fields": response["fields"],
            "key": r2_key,
            "filename": safe_filename,
            "expires_in": expires_in,
        }

    def _log_media_action(self, action, user, store, media_file, metadata=None):
        """
        Log media-related actions to the activity log

        Args:
            action: Action type (UPLOAD, DELETE, etc.)
            user: User performing the action
            store: Store the action belongs to
            media_file: MediaFile being acted upon
            metadata: Additional metadata to include in the log
        """
        from apps.analytics.services.event_service import EventService

        EventService.log_event(
            event_type=f"MEDIA_{action}",
            event_name=f"Media file {action}: {media_file.name}",
            properties={
                "user": user.id if user else None,
                "store": store.id if store else None,
                "media_file_id": media_file.id,
                "media_type": media_file.media_type,
                "file_size": media_file.file_size,
                "action": action,
                "metadata": metadata,
            },
            user=user,
            store=store,
        )

    def upload_from_request(
        self,
        store,
        file_obj,
        uploaded_by=None,
        folder_name=None,
        alt_text="",
        description="",
        metadata=None,
    ):
        """
        Centralized helper to upload files from request data.

        This method consolidates the logic from core/media_utils.py upload_to_mediafile.

        Args:
            store: Store instance
            file_obj: UploadedFile instance
            uploaded_by: User instance (optional)
            folder_name: Folder name to organize files (optional)
            alt_text: Alt text for images (optional)
            description: File description (optional)
            metadata: Additional metadata (optional)

        Returns:
            MediaFile: Created media file instance
        """
        try:
            # Get or create folder
            folder = None
            if folder_name:
                folder, created = MediaFolder.objects.get_or_create(
                    store=store,
                    name=folder_name,
                    defaults={
                        "created_by": uploaded_by,
                        "slug": folder_name.lower().replace(" ", "-"),
                    },
                )

            # Determine resource type
            resource_type = self._determine_resource_type(file_obj.content_type)

            # Upload via existing upload_file method
            media_file = self.upload_file(
                store=store,
                file_obj=file_obj,
                uploaded_by=uploaded_by,
                folder=folder,
                resource_type=resource_type,
                alt_text=alt_text,
                description=description,
                metadata=metadata or {},
            )

            logger.info(f"Uploaded media file: {media_file.original_filename} for store {store.id}")
            return media_file

        except Exception as e:
            logger.error(f"Failed to upload media file: {e}")
            raise

    def get_media_url(self, media_file, transformation=None):
        """
        Get public URL for a MediaFile with optional transformations.

        This method consolidates the logic from core/media_utils.py get_mediafile_url.

        Args:
            media_file: MediaFile instance
            transformation: ImageKit transformation string (optional)

        Returns:
            str: Public URL
        """
        if not media_file:
            return None

        try:
            return self.get_file_url(media_file, transformation)
        except Exception as e:
            logger.error(f"Failed to get media URL: {e}")
            return None

    def get_thumbnail_url(self, media_file, width=200, height=200, crop="fill"):
        """
        Get thumbnail URL for a MediaFile.

        This method consolidates the logic from core/media_utils.py get_mediafile_thumbnail.

        Args:
            media_file: MediaFile instance
            width: Thumbnail width
            height: Thumbnail height
            crop: Crop mode

        Returns:
            str: Thumbnail URL or None
        """
        if not media_file or not media_file.is_image:
            return None

        try:
            return self.get_file_url(media_file, f"w-{width},h-{height},c-{crop},q-80,pr-true")
        except Exception as e:
            logger.error(f"Failed to get thumbnail URL: {e}")
            return None
