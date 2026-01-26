"""
Public mediafile API.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from rest_framework.permissions import AllowAny

from apps.mediafile.models.media_file import MediaFile
from apps.mediafile.models.media_folder import MediaFolder


class MediafilePublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public media file endpoints for browsing public media.
    Read-only access to publicly available media files.
    """
    permission_classes = [AllowAny]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['original_filename', 'alt_text', 'description']
    ordering_fields = ['created_at', 'file_size', 'original_filename']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return public media files for the current store"""
        store = self.request.store
        queryset = MediaFile.objects.filter(store=store, is_public=True)
        
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
        """Return appropriate serializer class"""
        from apps.mediafile.v2.serializers.media_file import MediaFileSerializer
        return MediaFileSerializer
    
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


class MediafolderPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public media folder endpoints for browsing folder structure.
    Read-only access to folder hierarchy.
    """
    permission_classes = [AllowAny]
    
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
        
        # Get count of public files in each folder
        file_counts = MediaFile.objects.filter(store=store, is_public=True).values('folder').annotate(
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
