# Media App Rules - Cloudflare R2 + ImageKit.io

## Directory Structure
```
mediafile/
├── __init__.py
├── apps.py
├── models/
│   ├── __init__.py
│   ├── media_file.py
│   └── media_folder.py
├── services/
│   ├── __init__.py
│   ├── media_service.py
│   └── imagekit_service.py
├── tasks.py
├── admin.py
├── signals.py
├── exceptions.py
└── v2/
    ├── __init__.py
    ├── urls.py
    ├── serializers/
    │   ├── __init__.py
    │   ├── media_file.py
    │   └── media_folder.py
    └── views/
        ├── __init__.py
        ├── media_views.py
        └── folder_views.py
```

## Core Models

### MediaFile
```python
# media/models/media_file.py
import os
from django.db import models
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from django.conf import settings

class MediaFile(models.Model):
    """
    Represents a media file stored in Cloudflare R2 with ImageKit.io processing.
    """
    # File types and size limits (in bytes)
    IMAGE_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    VIDEO_MAX_SIZE = 100 * 1024 * 1024  # 100MB
    DOCUMENT_MAX_SIZE = 20 * 1024 * 1024  # 20MB
    
    RESOURCE_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('other', 'Other')
    ]
    
    # Core fields
    original_filename = models.CharField(max_length=255)
    file_extension = models.CharField(max_length=10)
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    
    # R2 storage path (format: store_{id}/media/{folder_path}/filename.xxx)
    storage_path = models.CharField(max_length=512)
    
    # ImageKit.io specific
    imagekit_id = models.CharField(max_length=255, blank=True, null=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    
    # Metadata
    alt_text = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Relations
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='media_files')
    folder = models.ForeignKey(
        'mediaFile.MediaFolder', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='media_files'
    )
    uploaded_by = models.ForeignKey(
        'accounts.UserAccount', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='uploaded_files'
    )
    
    # Reverse relationships for user media
    # These are defined here for documentation and type hinting
    user_avatars = models.ManyToManyField(
        'accounts.UserAccount',
        related_name='avatar_media',
        blank=True,
        help_text="Users who use this file as their avatar"
    )
    user_cover_photos = models.ManyToManyField(
        'accounts.UserAccount',
        related_name='cover_photo_media',
        blank=True,
        help_text="Users who use this file as their cover photo"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['store', 'resource_type']),
            models.Index(fields=['store', 'folder']),
            models.Index(fields=['created_at']),
            models.Index(fields=['file_size']),
        ]
    
    def __str__(self):
        return self.original_filename
    
    @property
    def file_size_formatted(self):
        """Return human-readable file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} GB"
    
    @property
    def is_image(self):
        return self.resource_type == 'image'
    
    @property
    def is_video(self):
        return self.resource_type == 'video'
    
    @property
    def is_document(self):
        return self.resource_type == 'document'

    def get_absolute_url(self, transformation=None):
        """
        Get the public URL for this media file with optional transformations
        
        Args:
            transformation (str, optional): ImageKit transformation string
            
        Returns:
            str: Public URL with transformations applied
        """
        from .services.media_service import MediaService
        return MediaService().get_media_url(self, transformation)

    def get_thumbnail_url(self, width=200, height=200, crop='fill'):
        """
        Get a thumbnail URL for this media file
        
        Args:
            width (int): Width in pixels
            height (int): Height in pixels
            crop (str): Crop mode (fill, fit, etc.)
            
        Returns:
            str: Thumbnail URL or None if not applicable
        """
        if not self.is_image and not self.is_video:
            return None
            
        transformation = f'tr:w-{width},h-{height},c-{crop}'
        return self.get_absolute_url(transformation)

    def get_presigned_url(self, expires_in=3600):
        """
        Generate a presigned URL for private file access
        
        Args:
            expires_in (int): Expiration time in seconds
            
        Returns:
            str: Presigned URL or None if not applicable
        """
        from .services.media_service import MediaService
        return MediaService().get_presigned_url(self, expires_in)
```

### MediaFolder
```python
# media/models/media_folder.py
from django.db import models
from django.utils.text import slugify

class MediaFolder(models.Model):
    """
    Represents a folder for organizing media files within a store.
    Supports nested folder structure.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='media_folders')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created_by = models.ForeignKey('accounts.UserAccount', on_delete=models.SET_NULL, null=True, related_name='created_folders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('store', 'parent', 'slug')
        ordering = ['name']
        indexes = [
            models.Index(fields=['store']),
            models.Index(fields=['parent']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def path(self):
        """Get full folder path as string"""
        if self.parent:
            return f"{self.parent.path}/{self.slug}"
        return self.slug
```

## Service Layer

### MediaService
```python
# media/services/media_service.py
import os
import mimetypes
import logging
from urllib.parse import urljoin
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
import boto3
from botocore.exceptions import ClientError
import imagekit
from imagekitio import ImageKit

from ..models.media_file import MediaFile
from ..models.media_folder import MediaFolder
from ..exceptions import (
    MediaUploadError,
    InvalidFileTypeError,
    FileTooLargeError,
    StorageError
)

logger = logging.getLogger(__name__)

class MediaService:
    """
    Service class for handling media file operations with Cloudflare R2 and ImageKit.io
    """
    
    # Allowed MIME types and their corresponding resource types
    ALLOWED_MIME_TYPES = {
        'image': [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp', 
            'image/svg+xml', 'image/tiff', 'image/bmp'
        ],
        'video': [
            'video/mp4', 'video/webm', 'video/ogg', 'video/quicktime',
            'video/x-msvideo', 'video/x-ms-wmv', 'video/x-matroska'
        ],
        'document': [
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'text/plain', 'text/csv', 'application/rtf',
            'application/zip', 'application/x-rar-compressed',
            'application/x-7z-compressed', 'application/x-tar',
            'application/x-gzip'
        ]
    }
    
    def __init__(self):
        """Initialize R2 and ImageKit clients"""
        # Initialize R2 client
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name='auto',
            config=boto3.session.Config(signature_version='s3v4')
        )
        
        # Initialize ImageKit
        self.imagekit = ImageKit(
            private_key=settings.IMAGEKIT_PRIVATE_KEY,
            public_key=settings.IMAGEKIT_PUBLIC_KEY,
            url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
        )
    
    def upload_file(self, file_obj, store, user, folder=None, metadata=None):
        """
        Upload a file to R2 and create a MediaFile record
        
        Args:
            file_obj: File object or InMemoryUploadedFile
            store: Store instance
            user: UserAccount instance
            folder: Optional MediaFolder instance
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
            if not file_obj or not hasattr(file_obj, 'name'):
                raise MediaUploadError("Invalid file object")
                
            # Get file metadata
            file_name = file_obj.name
            file_size = file_obj.size
            mime_type = getattr(file_obj, 'content_type', 
                              mimetypes.guess_type(file_name)[0] or 'application/octet-stream')
            
            # Determine resource type and validate
            resource_type = self._get_resource_type(mime_type, file_name)
            if not resource_type:
                raise InvalidFileTypeError(
                    f"File type {mime_type} is not allowed. "
                    f"Allowed types: {', '.join(self.ALLOWED_MIME_TYPES.keys())}"
                )
            
            # Validate file size
            max_size = getattr(MediaFile, f"{resource_type.upper()}_MAX_SIZE")
            if file_size > max_size:
                raise FileTooLargeError(
                    f"{resource_type.capitalize()} exceeds maximum size of "
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
            
            try:
                if hasattr(file_obj, 'temporary_file_path'):
                    # File is stored on disk
                    self.s3_client.upload_file(
                        file_obj.temporary_file_path(),
                        settings.AWS_STORAGE_BUCKET_NAME,
                        r2_key,
                        ExtraArgs={
                            'ContentType': mime_type,
                            'ACL': 'public-read' if resource_type in ['image', 'video'] else 'private'
                        }
                    )
                else:
                    # File is in memory
                    self.s3_client.upload_fileobj(
                        file_obj,
                        settings.AWS_STORAGE_BUCKET_NAME,
                        r2_key,
                        ExtraArgs={
                            'ContentType': mime_type,
                            'ACL': 'public-read' if resource_type in ['image', 'video'] else 'private'
                        }
                    )
            except ClientError as e:
                logger.error(f"Failed to upload to R2: {str(e)}")
                raise StorageError("Failed to upload file to storage")
            
            # Get file dimensions if image
            width, height = None, None
            if resource_type == 'image':
                try:
                    from PIL import Image
                    if hasattr(file_obj, 'temporary_file_path'):
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
            
            # Create MediaFile record
            media_file = MediaFile.objects.create(
                original_filename=file_name,
                file_extension=file_extension.lstrip('.'),
                file_size=file_size,
                mime_type=mime_type,
                resource_type=resource_type,
                storage_path=r2_key,
                width=width,
                height=height,
                store=store,
                folder=folder,
                uploaded_by=user,
                metadata=metadata or {}
            )
            
            # Register with ImageKit for images and videos
            if resource_type in ['image', 'video']:
                try:
                    # Get public URL from R2
                    public_url = f"{settings.AWS_S3_PUBLIC_URL}/{r2_key}"
                    
                    # Upload to ImageKit
                    result = self.imagekit.upload(
                        file=public_url,
                        file_name=safe_filename,
                        options={
                            'folder': folder_path,
                            'is_private_file': False,
                            'use_unique_file_name': False,
                            'response_fields': ['url', 'fileId']
                        }
                    )
                    
                    # Update MediaFile with ImageKit ID
                    media_file.imagekit_id = result['fileId']
                    media_file.save(update_fields=['imagekit_id'])
                    
                except Exception as e:
                    logger.error(f"Failed to register with ImageKit: {str(e)}")
                    # Don't fail the upload, just log the error
            
            # Log the upload
            self._log_media_action(
                action='UPLOAD',
                user=user,
                store=store,
                media_file=media_file,
                metadata={
                    'file_size': file_size,
                    'mime_type': mime_type,
                    'folder': folder.name if folder else None
                }
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
            user: UserAccount performing the deletion
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            store = media_file.store
            
            # Delete from R2
            try:
                self.s3_client.delete_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=media_file.storage_path
                )
            except ClientError as e:
                logger.error(f"Failed to delete from R2: {str(e)}")
                # Continue with DB deletion even if R2 delete fails
            
            # Delete from ImageKit if it exists
            if media_file.imagekit_id:
                try:
                    self.imagekit.delete_file(media_file.imagekit_id)
                except Exception as e:
                    logger.error(f"Failed to delete from ImageKit: {str(e)}")
            
            # Log before deletion (to have the ID)
            self._log_media_action(
                action='DELETE',
                user=user,
                store=store,
                media_file=media_file
            )
            
            # Delete from database
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
        if media_file.resource_type not in ['image', 'video']:
            return self.get_presigned_url(media_file)
            
        # For public files, use ImageKit if available
        if media_file.imagekit_id:
            try:
                url = f"{settings.IMAGEKIT_URL}/{media_file.storage_path}"
                if transformation:
                    url = f"{url}?tr={transformation}"
                return url
            except Exception as e:
                logger.warning(f"Failed to get ImageKit URL: {str(e)}")
                # Fall back to R2 URL
        
        # Fallback to R2 public URL
        return f"{settings.AWS_S3_PUBLIC_URL}/{media_file.storage_path}"
    
    def get_presigned_url(self, media_file, expires_in=3600):
        """
        Generate a presigned URL for private file access
        
        Args:
            media_file: MediaFile instance
            expires_in: Expiration time in seconds
            
        Returns:
            str: Presigned URL or None if not applicable
        """
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': media_file.storage_path,
                    'ResponseContentType': media_file.mime_type,
                    'ResponseContentDisposition': f'attachment; filename="{media_file.original_filename}"'
                },
                ExpiresIn=expires_in
            )
            return response
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            return None
    
    def get_thumbnail_url(self, media_file, width=200, height=200, crop='fill'):
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
        if not media_file or media_file.resource_type not in ['image', 'video']:
            return None
            
        transformation = f'w-{width},h-{height},c-{crop}'
        return self.get_media_url(media_file, transformation)
    
    def _get_resource_type(self, mime_type, file_name):
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
            ext = os.path.splitext(file_name)[1].lower().lstrip('.')
            mime_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
        
        for resource_type, allowed_mimes in self.ALLOWED_MIME_TYPES.items():
            if mime_type in allowed_mimes:
                return resource_type
        
        return None
    
    def _log_media_action(self, action, user, store, media_file, metadata=None):
        """
        Log media-related actions to the activity log
        
        Args:
            action: Action type (UPLOAD, DELETE, etc.)
            user: UserAccount performing the action
            store: Store the action belongs to
            media_file: MediaFile being acted upon
            metadata: Additional metadata to include in the log
        """
        from logs.services.log_service import log_event_async
        
        log_data = {
            'event_type': 'MEDIA_' + action,
            'message': f"Media file {action.lower()}: {media_file.original_filename}",
            'user': user,
            'store': store,
            'entity_type': 'MediaFile',
            'entity_id': media_file.id,
            'metadata': {
                'file_size': media_file.file_size,
                'mime_type': media_file.mime_type,
                'resource_type': media_file.resource_type,
                'folder': media_file.folder.name if media_file.folder else None,
                **(metadata or {})
            }
        }
        
        log_event_async.delay(log_data)
```

### ImageKitService (Optional)
```python
# media/services/imagekit_service.py
from imagekitio import ImageKit
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ImageKitService:
    """
    Service class for advanced ImageKit.io operations
    """
    
    def __init__(self):
        self.client = ImageKit(
            private_key=settings.IMAGEKIT_PRIVATE_KEY,
            public_key=settings.IMAGEKIT_PUBLIC_KEY,
            url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
        )
    
    def get_transformed_url(self, image_url, transformations):
        """
        Get URL for an image with transformations applied
        
        Args:
            image_url: Source image URL
            transformations: List of transformation dicts
                Example: [{"height": 300, "width": 400}]
                
        Returns:
            str: Transformed image URL
        """
        try:
            return self.client.url({
                'path': image_url,
                'transformation': transformations
            })
        except Exception as e:
            logger.error(f"Failed to generate transformed URL: {str(e)}")
            return image_url
    
    def get_video_thumbnail(self, video_url, width=320, height=180):
        """
        Generate a thumbnail for a video
        
        Args:
            video_url: Source video URL
            width: Thumbnail width
            height: Thumbnail height
            
        Returns:
            str: URL to the generated thumbnail
        """
        try:
            return self.client.url({
                'path': video_url,
                'transformation': [
                    {
                        'format': 'jpg',
                        'height': height,
                        'width': width,
                        'crop': 'fill',
                        'quality': '80',
                        'progressive': 'true'
                    }
                ]
            })
        except Exception as e:
            logger.error(f"Failed to generate video thumbnail: {str(e)}")
            return None
    
    def bulk_optimize(self, file_ids, transformations=None):
        """
        Optimize multiple images in bulk
        
        Args:
            file_ids: List of ImageKit file IDs
            transformations: Optional transformations to apply
            
        Returns:
            dict: Result of the bulk operation
        """
        try:
            return self.client.bulk_file_operations(
                file_ids=file_ids,
                transformations=transformations or []
            )
        except Exception as e:
            logger.error(f"Bulk optimize failed: {str(e)}")
            return {'success': False, 'error': str(e)}
```

## Configuration

### Django Settings
```python
# settings/base.py

# Cloudflare R2 Configuration
AWS_ACCESS_KEY_ID = env('R2_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('R2_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('R2_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = env('R2_ENDPOINT_URL')  # e.g., 'https://<account-id>.r2.cloudflarestorage.com'
AWS_S3_PUBLIC_URL = env('R2_PUBLIC_URL')  # e.g., 'https://<bucket>.<account-id>.r2.dev'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_DEFAULT_ACL = None  # Will be set per object
AWS_QUERYSTRING_AUTH = False  # Don't add auth to query strings
AWS_S3_FILE_OVERWRITE = False  # Prevent overwriting files with same name

# ImageKit.io Configuration
IMAGEKIT_PUBLIC_KEY = env('IMAGEKIT_PUBLIC_KEY')
IMAGEKIT_PRIVATE_KEY = env('IMAGEKIT_PRIVATE_KEY')
IMAGEKIT_URL_ENDPOINT = env('IMAGEKIT_URL_ENDPOINT')  # e.g., 'https://ik.imagekit.io/your_imagekit_id'
IMAGEKIT_URL = env('IMAGEKIT_URL', default=IMAGEKIT_URL_ENDPOINT)

# Media settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ...
    'storages',  # For S3/R2 storage
    'imagekit',  # For image processing
    'media',     # Our media app
]

# Default file storage (for media files)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# For serving media files in development
if DEBUG:
    from .dev import *  # noqa
```

### Environment Variables
```bash
# .env
# Cloudflare R2
R2_ACCESS_KEY_ID=your_r2_access_key
R2_SECRET_ACCESS_KEY=your_r2_secret_key
R2_BUCKET_NAME=your-bucket-name
R2_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
R2_PUBLIC_URL=https://<bucket>.<account-id>.r2.dev

# ImageKit.io
IMAGEKIT_PUBLIC_KEY=your_public_key
IMAGEKIT_PRIVATE_KEY=your_private_key
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_imagekit_id
```

## API Views

### MediaFileViewSet
```python
# media/v2/views/media_views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from django.db.models import Q
from django.core.exceptions import ValidationError

from ...models.media_file import MediaFile
from ...models.media_folder import MediaFolder
from ..serializers.media_file import MediaFileSerializer, MediaFileUploadSerializer
from ...services.media_service import MediaService
from ...exceptions import InvalidFileTypeError, FileTooLargeError, StorageError, MediaUploadError
from stores.permissions import IsStoreStaffOrReadOnly

class MediaFileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing media files.
    """
    serializer_class = MediaFileSerializer
    permission_classes = [IsStoreStaffOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['original_filename', 'alt_text', 'description']
    ordering_fields = ['created_at', 'file_size', 'original_filename']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return media files for the current store"""
        store = self.request.store
        queryset = MediaFile.objects.filter(store=store)
        
        # Filter by folder
        folder_id = self.request.query_params.get('folder_id')
        if folder_id:
            if folder_id == 'uncategorized':
                queryset = queryset.filter(folder__isnull=True)
            else:
                try:
                    folder = MediaFolder.objects.get(id=folder_id, store=store)
                    queryset = queryset.filter(folder=folder)
                except (ValueError, MediaFolder.DoesNotExist):
                    queryset = queryset.none()
        
        # Filter by resource type
        resource_type = self.request.query_params.get('type')
        if resource_type in dict(MediaFile.RESOURCE_TYPES):
            queryset = queryset.filter(resource_type=resource_type)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'create':
            return MediaFileUploadSerializer
        return MediaFileSerializer
    
    def perform_create(self, serializer):
        """Handle file upload and create MediaFile instance"""
        file_obj = self.request.FILES.get('file')
        if not file_obj:
            raise ValidationError({"file": ["No file was submitted."]})
        
        folder_id = self.request.data.get('folder')
        folder = None
        if folder_id:
            try:
                folder = MediaFolder.objects.get(id=folder_id, store=self.request.store)
            except (ValueError, MediaFolder.DoesNotExist):
                raise ValidationError({"folder": ["Invalid folder ID."]})
        
        media_service = MediaService()
        try:
            media_file = media_service.upload_file(
                file_obj=file_obj,
                store=self.request.store,
                user=self.request.user,
                folder=folder,
                metadata={
                    'uploaded_via': 'api',
                    'user_agent': self.request.META.get('HTTP_USER_AGENT', ''),
                    'ip_address': self.get_client_ip()
                }
            )
            
            # Set the instance for the serializer
            serializer.instance = media_file
            
        except (InvalidFileTypeError, FileTooLargeError, StorageError) as e:
            raise ValidationError({"file": [str(e)]})
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise ValidationError({"detail": "An error occurred while uploading the file."})
    
    @action(detail=True, methods=['get'])
    def thumbnail(self, request, pk=None):
        """Get a thumbnail URL for the media file"""
        media_file = self.get_object()
        width = request.query_params.get('width', 200)
        height = request.query_params.get('height', 200)
        crop = request.query_params.get('crop', 'fill')
        
        try:
            thumbnail_url = media_file.get_thumbnail_url(
                width=int(width),
                height=int(height),
                crop=crop
            )
            return Response({'url': thumbnail_url})
        except (ValueError, TypeError):
            return Response(
                {"detail": "Invalid width/height parameters"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Get a presigned URL for downloading the file"""
        media_file = self.get_object()
        expires_in = min(int(request.query_params.get('expires_in', 3600)), 86400)  # Max 24 hours
        
        download_url = media_file.get_presigned_url(expires_in=expires_in)
        if not download_url:
            return Response(
                {"detail": "Could not generate download URL"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        return Response({
            'url': download_url,
            'expires_in': expires_in
        })
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """Bulk delete media files"""
        media_ids = request.data.get('ids', [])
        if not isinstance(media_ids, list):
            return Response(
                {"ids": ["Expected a list of media IDs"]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        store = request.store
        media_service = MediaService()
        deleted_count = 0
        
        for media_id in media_ids:
            try:
                media_file = MediaFile.objects.get(id=media_id, store=store)
                if media_service.delete_media(media_file, request.user):
                    deleted_count += 1
            except (MediaFile.DoesNotExist, MediaUploadError):
                continue
        
        return Response({
            'deleted_count': deleted_count,
            'total_count': len(media_ids)
        })
    
    def get_client_ip(self):
        """Get the client's IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return self.request.META.get('REMOTE_ADDR')
```

### MediaFolderViewSet
```python
# media/v2/views/folder_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q

from ...models.media_folder import MediaFolder
from ..serializers.media_folder import MediaFolderSerializer, MediaFolderTreeSerializer
from stores.permissions import IsStoreStaffOrReadOnly

class MediaFolderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing media folders.
    """
    serializer_class = MediaFolderSerializer
    permission_classes = [IsStoreStaffOrReadOnly]
    
    def get_queryset(self):
        """Return folders for the current store"""
        store = self.request.store
        return MediaFolder.objects.filter(store=store).select_related('parent')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'tree':
            return MediaFolderTreeSerializer
        return MediaFolderSerializer
    
    def perform_create(self, serializer):
        """Set the store and created_by fields"""
        serializer.save(
            store=self.request.store,
            created_by=self.request.user
        )
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get folder hierarchy as a tree"""
        store = request.store
        folders = MediaFolder.objects.filter(store=store)
        
        # Get count of files in each folder
        from ...models.media_file import MediaFile
        file_counts = MediaFile.objects.filter(store=store).values('folder').annotate(
            file_count=Count('id')
        )
        file_count_map = {fc['folder']: fc['file_count'] for fc in file_counts if fc['folder']}
        
        # Build tree
        folder_map = {}
        root_folders = []
        
        # First pass: create all folder nodes
        for folder in folders:
            folder_map[folder.id] = {
                'id': folder.id,
                'name': folder.name,
                'slug': folder.slug,
                'parent_id': folder.parent_id,
                'file_count': file_count_map.get(folder.id, 0),
                'children': []
            }
        
        # Second pass: build hierarchy
        for folder_id, folder_data in folder_map.items():
            if folder_data['parent_id'] is None:
                root_folders.append(folder_data)
            else:
                parent = folder_map.get(folder_data['parent_id'])
                if parent:
                    parent['children'].append(folder_data)
        
        # Add uncategorized count
        uncategorized_count = MediaFile.objects.filter(
            store=store,
            folder__isnull=True
        ).count()
        
        return Response({
            'folders': root_folders,
            'uncategorized_count': uncategorized_count
        })
    
    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """Move a folder to a new parent"""
        folder = self.get_object()
        parent_id = request.data.get('parent_id')
        
        if parent_id == str(folder.id):
            return Response(
                {"parent_id": ["A folder cannot be its own parent"]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if parent_id is None:
            folder.parent = None
        else:
            try:
                parent_folder = MediaFolder.objects.get(id=parent_id, store=request.store)
                # Check for circular reference
                if self._is_descendant(parent_folder, folder):
                    return Response(
                        {"parent_id": ["Cannot move folder to its own descendant"]},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                folder.parent = parent_folder
            except MediaFolder.DoesNotExist:
                return Response(
                    {"parent_id": ["Invalid parent folder"]},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        folder.save()
        return Response(self.get_serializer(folder).data)
    
    def _is_descendant(self, parent, child):
        """Check if child is a descendant of parent"""
        if not child.parent:
            return False
        if child.parent_id == parent.id:
            return True
        return self._is_descendant(parent, child.parent)
```

## Serializers

### MediaFileSerializer
```python
# media/v2/serializers/media_file.py
from rest_framework import serializers
from ...models.media_file import MediaFile

class MediaFileSerializer(serializers.ModelSerializer):
    """Serializer for MediaFile model"""
    url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    file_size_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = MediaFile
        fields = [
            'id', 'original_filename', 'file_extension', 'file_size', 'file_size_formatted',
            'mime_type', 'resource_type', 'width', 'height', 'alt_text', 'description',
            'folder', 'created_at', 'updated_at', 'url', 'thumbnail_url'
        ]
        read_only_fields = [
            'id', 'original_filename', 'file_extension', 'file_size', 'file_size_formatted',
            'mime_type', 'resource_type', 'width', 'height', 'created_at', 'updated_at',
            'url', 'thumbnail_url'
        ]
    
    def get_url(self, obj):
        """Get public URL for the media file"""
        return obj.get_absolute_url()
    
    def get_thumbnail_url(self, obj):
        """Get thumbnail URL for the media file"""
        return obj.get_thumbnail_url()
    
    def get_file_size_formatted(self, obj):
        """Get human-readable file size"""
        return obj.file_size_formatted


class MediaFileUploadSerializer(serializers.ModelSerializer):
    """Serializer for file uploads"""
    file = serializers.FileField(write_only=True)
    folder = serializers.PrimaryKeyRelatedField(
        queryset=MediaFolder.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = MediaFile
        fields = ['file', 'folder', 'alt_text', 'description']
        read_only_fields = ['id']
```

### MediaFolderSerializer
```python
# media/v2/serializers/media_folder.py
from rest_framework import serializers
from ...models.media_folder import MediaFolder

class MediaFolderSerializer(serializers.ModelSerializer):
    """Serializer for MediaFolder model"""
    file_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = MediaFolder
        fields = ['id', 'name', 'slug', 'parent', 'file_count', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'file_count', 'created_at', 'updated_at']
    
    def validate_parent(self, value):
        """Validate that parent folder belongs to the same store"""
        if value and value.store != self.context['request'].store:
            raise serializers.ValidationError("Parent folder does not belong to this store.")
        return value


class MediaFolderTreeSerializer(serializers.ModelSerializer):
    """Serializer for folder tree view"""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = MediaFolder
        fields = ['id', 'name', 'slug', 'file_count', 'children']
    
    def get_children(self, obj):
        """Recursively serialize children"""
        serializer = self.__class__(obj.children.all(), many=True, context=self.context)
        return serializer.data
```

## Migration Command

### migrate_media.py
```python
# media/management/commands/migrate_media.py
import os
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
import cloudinary
from cloudinary import uploader, api

from ...models import MediaFile, MediaFolder
from ...services.media_service import MediaService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Migrate media files from Cloudinary to Cloudflare R2 + ImageKit.io'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--store-id',
            type=str,
            help='Store ID to migrate media for (default: all stores)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of files to migrate (default: 100)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making any changes'
        )
    
    def handle(self, *args, **options):
        store_id = options.get('store_id')
        limit = options.get('limit')
        dry_run = options.get('dry_run')
        
        self.stdout.write(self.style.SUCCESS(
            f'Starting media migration for store {store_id or "all"} (dry run: {dry_run})'
        ))
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET
        )
        
        # Get media files to migrate
        queryset = MediaFile.objects.all()
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        
        total_count = queryset.count()
        self.stdout.write(f'Found {total_count} media files to migrate')
        
        if not total_count:
            self.stdout.write(self.style.SUCCESS('No media files to migrate'))
            return
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run - no changes will be made'))
        
        migrated_count = 0
        skipped_count = 0
        error_count = 0
        
        media_service = MediaService()
        
        for media_file in queryset[:limit]:
            try:
                self.stdout.write(f'Processing {media_file.original_filename}... ', ending='')
                
                # Skip if already migrated
                if media_file.storage_path and media_file.storage_path.startswith('store_'):
                    self.stdout.write(self.style.WARNING('Already migrated'))
                    skipped_count += 1
                    continue
                
                # Download from Cloudinary
                try:
                    cloudinary_url = f"v{media_file.version}/{media_file.public_id}.{media_file.format}"
                    temp_file = f'/tmp/{media_file.public_id}.{media_file.format}'
                    
                    if not dry_run:
                        # Download the file
                        with open(temp_file, 'wb') as f:
                            result = cloudinary.utils.cloudinary_url(cloudinary_url)[0]
                            f.write(requests.get(result).content)
                        
                        # Upload to R2 + ImageKit
                        with open(temp_file, 'rb') as f:
                            uploaded_file = SimpleUploadedFile(
                                name=media_file.original_filename,
                                content=f.read(),
                                content_type=media_file.mime_type
                            )
                            
                            # Get folder if exists
                            folder = None
                            if media_file.folder_id:
                                try:
                                    folder = MediaFolder.objects.get(id=media_file.folder_id)
                                except MediaFolder.DoesNotExist:
                                    pass
                            
                            # Upload the file
                            media_service.upload_file(
                                file_obj=uploaded_file,
                                store=media_file.store,
                                user=media_file.uploaded_by,
                                folder=folder,
                                metadata={
                                    'migrated_from_cloudinary': True,
                                    'cloudinary_public_id': media_file.public_id
                                }
                            )
                        
                        # Delete local temp file
                        os.remove(temp_file)
                        
                        # Delete from Cloudinary if migration is successful
                        if not dry_run and settings.CLOUDINARY_DELETE_AFTER_MIGRATE:
                            try:
                                uploader.destroy(media_file.public_id)
                            except Exception as e:
                                logger.error(f"Failed to delete from Cloudinary: {str(e)}")
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
                    error_count += 1
                    continue
                
                migrated_count += 1
                self.stdout.write(self.style.SUCCESS('Done'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Unexpected error: {str(e)}'))
                error_count += 1
                continue
        
        # Print summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('Migration complete!'))
        self.stdout.write(f'Total processed: {migrated_count + skipped_count + error_count}')
        self.stdout.write(f'Successfully migrated: {migrated_count}')
        self.stdout.write(f'Skipped (already migrated): {skipped_count}')
        self.stdout.write(f'Errors: {error_count}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a dry run. No changes were made.'))
```

## API Documentation

### Media Files

#### List Media Files
```
GET /api/v2/media/files/
```

**Query Parameters:**
- `folder_id` - Filter by folder ID (use 'uncategorized' for files without a folder)
- `type` - Filter by resource type (image, video, document, other)
- `search` - Search in filename, alt text, or description
- `ordering` - Sort by field (created_at, file_size, original_filename, -created_at, etc.)

**Response:**
```json
{
  "count": 42,
  "next": "https://api.example.com/api/v2/media/files/?page=2",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "original_filename": "example.jpg",
      "file_extension": "jpg",
      "file_size": 1024000,
      "file_size_formatted": "1.0 MB",
      "mime_type": "image/jpeg",
      "resource_type": "image",
      "width": 1920,
      "height": 1080,
      "alt_text": "Example image",
      "description": "An example image",
      "folder": "550e8400-e29b-41d4-a716-446655440001",
      "created_at": "2023-01-01T12:00:00Z",
      "updated_at": "2023-01-01T12:00:00Z",
      "url": "https://ik.imagekit.io/your_imagekit_id/path/to/file.jpg",
      "thumbnail_url": "https://ik.imagekit.io/your_imagekit_id/tr:w-200,h-200,c-fill/path/to/file.jpg"
    }
  ]
}
```

#### Upload File
```
POST /api/v2/media/files/
Content-Type: multipart/form-data

file: <file>
folder: <folder_id> (optional)
alt_text: "Alternative text" (optional)
description: "Description" (optional)
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "original_filename": "example.jpg",
  "file_extension": "jpg",
  "file_size": 1024000,
  "file_size_formatted": "1.0 MB",
  "mime_type": "image/jpeg",
  "resource_type": "image",
  "width": 1920,
  "height": 1080,
  "alt_text": "Alternative text",
  "description": "Description",
  "folder": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z",
  "url": "https://ik.imagekit.io/your_imagekit_id/path/to/file.jpg",
  "thumbnail_url": "https://ik.imagekit.io/your_imagekit_id/tr:w-200,h-200,c-fill/path/to/file.jpg"
}
```

#### Get Thumbnail
```
GET /api/v2/media/files/{id}/thumbnail/
```

**Query Parameters:**
- `width` - Thumbnail width in pixels (default: 200)
- `height` - Thumbnail height in pixels (default: 200)
- `crop` - Crop mode: fill, fit, etc. (default: fill)

**Response:**
```json
{
  "url": "https://ik.imagekit.io/your_imagekit_id/tr:w-200,h-200,c-fill/path/to/file.jpg"
}
```

#### Download File
```
GET /api/v2/media/files/{id}/download/
```

**Query Parameters:**
- `expires_in` - URL expiration time in seconds (default: 3600, max: 86400)

**Response:**
```json
{
  "url": "https://your-bucket.r2.dev/path/to/file.jpg?X-Amz-Expires=3600&...",
  "expires_in": 3600
}
```

### Folders

#### List Folders (Tree View)
```
GET /api/v2/media/folders/tree/
```

**Response:**
```json
{
  "folders": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Products",
      "slug": "products",
      "file_count": 10,
      "children": [
        {
          "id": "550e8400-e29b-41d4-a716-446655440002",
          "name": "Featured",
          "slug": "featured",
          "file_count": 5,
          "children": []
        }
      ]
    }
  ],
  "uncategorized_count": 3
}
```

#### Move Folder
```
POST /api/v2/media/folders/{id}/move/
Content-Type: application/json

{
  "parent_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

## Cost Analysis

### Cloudflare R2
- **Storage**: $0.015 per GB/month (first 10GB free)
- **Class A Operations**: $0.36 per million requests (first 1M requests/month free)
- **Class B Operations**: $0.01 per million requests (first 10M requests/month free)
- **Egress**: Free (unlimited)

### ImageKit.io
- **Transformations**: $0.50 per 1,000 transformations (first 20GB of transformations free)
- **Storage**: $0.10 per GB/month (first 20GB free)
- **Bandwidth**: $0.10 per GB (first 200GB free)

### Estimated Monthly Cost (Example)
- **Assumptions**:
  - 100GB storage
  - 1M Class A operations
  - 10M Class B operations
  - 1M transformations
  - 1TB bandwidth

- **Cloudflare R2 Cost**:
  - Storage: (100GB - 10GB) * $0.015 = $1.35
  - Class A: (1M - 1M free) * $0.36 = $0.00
  - Class B: (10M - 10M free) * $0.01 = $0.00
  - **Total R2 Cost**: $1.35

- **ImageKit.io Cost**:
  - Transformations: (1M / 1,000) * $0.50 = $500
  - Storage: (100GB - 20GB) * $0.10 = $8.00
  - Bandwidth: (1,000GB - 200GB) * $0.10 = $80.00
  - **Total ImageKit Cost**: $588.00

- **Total Estimated Cost**: $589.35/month

## Allowed AI Actions

1. **Code Generation**
   - Generate model fields and methods
   - Create API views and serializers
   - Write service layer logic
   - Generate migration scripts
   - Create test cases

2. **Documentation**
   - Document API endpoints
   - Write code comments
   - Create usage examples
   - Document configuration steps

3. **Refactoring**
   - Optimize database queries
   - Improve error handling
   - Enhance performance
   - Update code to follow best practices

## Forbidden AI Actions

1. **Security Sensitive**
   - Generate API keys or secrets
   - Bypass authentication/authorization
   - Expose sensitive information

2. **Architectural Changes**
   - Change the database schema without approval
   - Modify core business logic
   - Change storage providers (R2/ImageKit)

3. **Production Operations**
   - Run migrations on production
   - Delete production data
   - Modify production configurations

## Implementation Checklist

### Setup
- [ ] Create Cloudflare R2 bucket
- [ ] Configure CORS for the R2 bucket
- [ ] Set up ImageKit.io account
- [ ] Configure environment variables
- [ ] Install required packages (boto3, imagekitio, etc.)

### Development
- [ ] Implement models (MediaFile, MediaFolder)
- [ ] Create MediaService with R2 + ImageKit integration
- [ ] Implement API views and serializers
- [ ] Add authentication and permissions
- [ ] Write unit tests
- [ ] Document API endpoints

### Migration
- [ ] Test migration with a small subset of files
- [ ] Back up Cloudinary data
- [ ] Run migration script
- [ ] Verify all files were migrated correctly
- [ ] Update any hardcoded Cloudinary URLs in the database

### Deployment
- [ ] Set up monitoring for storage usage
- [ ] Configure backups for R2 bucket
- [ ] Set up alerts for quota limits
- [ ] Document operational procedures

## Security & Privacy Rules

### Access Control
- All non-image/video files (documents) MUST use private ACL on R2
- Use presigned URLs with `expires_in` ≤ 3600 seconds for private file downloads
- Implement IP-based rate limiting for upload endpoints
- Enforce MIME type validation for all uploads
- Restrict file uploads by extension and content type

### Data Protection
- Anonymize IP addresses in metadata for non-authenticated visitors
- Never store passwords, API tokens, or PII in file metadata
- Encrypt sensitive metadata at rest
- Implement secure deletion of files when removed from trash

### File Security
- Scan all uploaded files for malware (integrate ClamAV or VirusTotal API)
- Validate image/video files for potential exploits
- Set appropriate Content-Security-Policy headers for media delivery
- Implement CORS restrictions for media domains

## Performance Rules

### Processing
- Use Celery for async post-upload processing:
  - Thumbnail generation
  - Metadata extraction
  - Virus scanning
  - File optimization
- Process large uploads in chunks (resumable uploads)
- Implement background processing for batch operations

### Caching
- Cache ImageKit URLs aggressively: `Cache-Control: max-age=31536000` for public assets
- Implement CDN caching for frequently accessed media
- Use stale-while-revalidate for dynamic transformations
- Cache folder hierarchies to reduce database load

### Optimization
- Enable gzip/brotli compression for text-based assets
- Use WebP/AVIF formats for web images when supported
- Implement lazy loading for below-the-fold media
- Optimize video delivery with adaptive bitrate streaming

## Cost & Quota Rules

### Monitoring
- Monitor R2 storage usage monthly via Cloudflare dashboard
- Set up alerts for 70%, 85%, and 95% of storage quota
- Track ImageKit transformation and bandwidth usage
- Log and analyze storage growth trends

### Optimization
- Implement automatic cleanup of old/unused files
- Set storage quotas per store/tenant
- Use lifecycle rules to transition old files to cheaper storage
- Compress and optimize images during upload

### Cost Controls
- ImageKit free tier: 20GB transformations + 200GB bandwidth — warn when approaching limits
- Use 'f-auto' for automatic format selection
- Apply 'q-80' quality for non-critical images
- Implement usage-based throttling for high-volume tenants
- Consider cost allocation tags for multi-tenant billing

## Implementation Timeline

### Phase 1: Core Functionality (Week 1-2)
1. Set up R2 bucket and IAM policies
2. Implement basic file upload/download
3. Create folder structure
4. Set up basic permissions

### Phase 2: Advanced Features (Week 3-4)
1. Implement thumbnail generation
2. Add bulk operations
3. Set up monitoring and alerts
4. Implement file scanning

### Phase 3: Optimization (Week 5-6)
1. Add caching layer
2. Implement async processing
3. Optimize delivery
4. Final security review

### Phase 4: Migration (Week 7-8)
1. Test migration with sample data
2. Schedule maintenance window
3. Execute full migration
4. Validate and monitor
