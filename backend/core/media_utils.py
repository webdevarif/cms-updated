"""
Core media utilities for centralized media handling.
"""
import logging
from django.core.files.uploadedfile import UploadedFile
from apps.mediafile.services.media_service import MediaService
from apps.mediafile.models import MediaFolder

logger = logging.getLogger(__name__)


def upload_to_mediafile(
    store,
    file_obj: UploadedFile,
    uploaded_by=None,
    folder_name: str = None,
    alt_text: str = "",
    description: str = "",
    metadata: dict = None
) -> MediaFile:
    """
    Centralized helper to upload files via MediaService.
    
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
        service = MediaService()
        
        # Get or create folder
        folder = None
        if folder_name:
            folder, created = MediaFolder.objects.get_or_create(
                store=store,
                name=folder_name,
                defaults={
                    'created_by': uploaded_by,
                    'slug': folder_name.lower().replace(' ', '-')
                }
            )
        
        # Determine resource type
        resource_type = service._determine_resource_type(file_obj.content_type)
        
        # Upload via MediaService
        media_file = service.upload_file(
            store=store,
            file_obj=file_obj,
            uploaded_by=uploaded_by,
            folder=folder,
            resource_type=resource_type,
            alt_text=alt_text,
            description=description,
            metadata=metadata or {}
        )
        
        logger.info(f"Uploaded media file: {media_file.original_filename} for store {store.id}")
        return media_file
        
    except Exception as e:
        logger.error(f"Failed to upload media file: {e}")
        raise


def get_mediafile_url(media_file: MediaFile, transformation: str = None) -> str:
    """
    Get public URL for a MediaFile with optional transformations.
    
    Args:
        media_file: MediaFile instance
        transformation: ImageKit transformation string (optional)
    
    Returns:
        str: Public URL
    """
    if not media_file:
        return None
    
    try:
        service = MediaService()
        return service.get_media_url(media_file, transformation)
    except Exception as e:
        logger.error(f"Failed to get media URL: {e}")
        return None


def get_mediafile_thumbnail(media_file: MediaFile, width: int = 200, height: int = 200, crop: str = 'fill') -> str:
    """
    Get thumbnail URL for a MediaFile.
    
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
        service = MediaService()
        return service.get_thumbnail_url(media_file, width, height, crop)
    except Exception as e:
        logger.error(f"Failed to get thumbnail URL: {e}")
        return None
