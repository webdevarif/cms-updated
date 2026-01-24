"""
Views for media file management.
"""
import logging
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from django.core.exceptions import ValidationError

from ...models.media_file import MediaFile
from ...models.media_folder import MediaFolder
from ...services.media_service import MediaService
from ...exceptions import InvalidFileTypeError, FileTooLargeError, StorageError, MediaUploadError

logger = logging.getLogger(__name__)


class MediaFileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing media files.
    """
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
            from ..serializers.media_file import MediaFileUploadSerializer
            return MediaFileUploadSerializer
        from ..serializers.media_file import MediaFileSerializer
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
