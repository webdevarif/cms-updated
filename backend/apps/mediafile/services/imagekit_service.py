"""
ImageKitService for advanced ImageKit.io operations.
"""
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ImageKitService:
    """
    Service class for advanced ImageKit.io operations
    """
    
    def __init__(self):
        try:
            from imagekitio import ImageKit
            self.client = ImageKit(
                private_key=getattr(settings, 'IMAGEKIT_PRIVATE_KEY', None),
                public_key=getattr(settings, 'IMAGEKIT_PUBLIC_KEY', None),
                url_endpoint=getattr(settings, 'IMAGEKIT_URL_ENDPOINT', None)
            )
        except ImportError:
            logger.warning("imagekitio not installed, ImageKit features will not work")
            self.client = None
    
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
        if not self.client:
            return image_url
            
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
        if not self.client:
            return None
            
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
        if not self.client:
            return {'success': False, 'error': 'ImageKit not configured'}
            
        try:
            return self.client.bulk_file_operations(
                file_ids=file_ids,
                transformations=transformations or []
            )
        except Exception as e:
            logger.error(f"Bulk optimize failed: {str(e)}")
            return {'success': False, 'error': str(e)}
