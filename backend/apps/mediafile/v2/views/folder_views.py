"""
Views for media folder management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q

from ...models.media_folder import MediaFolder
from ...v2.serializers.media_folder import MediaFolderSerializer, MediaFolderTreeSerializer


class MediaFolderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing media folders.
    """
    serializer_class = MediaFolderSerializer
    
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
