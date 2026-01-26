"""
Customer mediafile API.
"""
import logging
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from django.db.models import Count, Q
from django.core.exceptions import ValidationError

from core.permissions import IsStoreUser
from apps.mediafile.models.media_file import MediaFile
from apps.mediafile.models.media_folder import MediaFolder
from apps.mediafile.services.media_service import MediaService
from apps.mediafile.exceptions import InvalidFileTypeError, FileTooLargeError, StorageError, MediaUploadError

logger = logging.getLogger(__name__)


class MediafileCustomerViewSet(viewsets.ModelViewSet):
    """
    Customer media file management endpoints for authenticated users.
    Users can upload and manage their own media files.
    """
    parser_classes = [MultiPartParser, JSONParser]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['original_filename', 'alt_text', 'description']
    ordering_fields = ['created_at', 'file_size', 'original_filename']
    ordering = ['-created_at']
    permission_classes = [IsStoreUser]
    
    def get_queryset(self):
        """Return media files uploaded by the current user"""
        store = self.request.store
        queryset = MediaFile.objects.filter(store=store, uploaded_by=self.request.user)
        
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
            from apps.mediafile.v2.serializers.media_file import MediaFileUploadSerializer
            return MediaFileUploadSerializer
        from apps.mediafile.v2.serializers.media_file import MediaFileSerializer
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
                    'uploaded_via': 'customer_api',
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
    
    def get_client_ip(self):
        """Get the client's IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return self.request.META.get('REMOTE_ADDR')


class MediafolderCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer media folder endpoints for authenticated users.
    Users can view folder structure but cannot create folders.
    """
    permission_classes = [IsStoreUser]
    
    def get_queryset(self):
        """Return folders for the current store"""
        store = self.request.store
        return MediaFolder.objects.filter(store=store).select_related('parent')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'tree':
            from apps.mediafile.v2.serializers.media_folder import MediaFolderTreeSerializer
            return MediaFolderTreeSerializer
        from apps.mediafile.v2.serializers.media_folder import MediaFolderSerializer
        return MediaFolderSerializer
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get folder hierarchy as a tree"""
        store = request.store
        folders = MediaFolder.objects.filter(store=store)
        
        # Get count of files uploaded by current user in each folder
        file_counts = MediaFile.objects.filter(store=store, uploaded_by=request.user).values('folder').annotate(
            file_count=Count('id')
        )
        file_count_map = {fc['folder']: fc['file_count'] for fc in file_counts if fc['folder']}
        
        # Build tree
        folder_map = {}
        root_folders = []
        
        for folder in folders:
            folder_data = {
                'id': folder.id,
                'name': folder.name,
                'parent_id': folder.parent_id,
                'file_count': file_count_map.get(folder.id, 0),
                'children': []
            }
            folder_map[folder.id] = folder_data
            
            if folder.parent_id:
                folder_map.setdefault(folder.parent_id, {})['children'].append(folder_data)
            else:
                root_folders.append(folder_data)
        
        return Response(root_folders)
