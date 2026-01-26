"""
Dashboard mediafile API views.
"""
import logging
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from django.core.exceptions import ValidationError
from django.db.models import Count, Q, Sum

from core.permissions import IsStoreOwner
from apps.mediafile.models import MediaFile, MediaFolder
from apps.mediafile.services.media_service import MediaService
from apps.mediafile.exceptions import InvalidFileTypeError, FileTooLargeError, StorageError, MediaUploadError
from .serializers import (
    MediafileDashboardSerializer, 
    MediafileUploadDashboardSerializer, 
    MediafolderDashboardSerializer, 
    MediafolderTreeDashboardSerializer,
    BulkMediafileOperationSerializer
)

logger = logging.getLogger(__name__)


class MediafileDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard media file management endpoints for store owners and admins.
    Provides full CRUD access to all media files in the store.
    """
    parser_classes = [MultiPartParser, JSONParser]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['original_filename', 'alt_text', 'description']
    ordering_fields = ['created_at', 'file_size', 'original_filename']
    permission_classes = [permissions.IsAuthenticated, IsStoreOwner]
    
    def get_queryset(self):
        """Filter by store"""
        queryset = MediaFile.objects.all()
        store = getattr(self.request, 'store', None)
        if store:
            queryset = queryset.filter(store=store)
        return queryset.select_related('folder', 'uploaded_by')
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Upload a new media file"""
        try:
            file_obj = request.FILES.get('file')
            if not file_obj:
                return Response(
                    {'error': 'No file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Use MediaService to handle upload
            media_file = MediaService.upload_file(
                file_obj=file_obj,
                store=getattr(request, 'store', None),
                user=request.user,
                alt_text=request.data.get('alt_text', ''),
                description=request.data.get('description', ''),
                folder_id=request.data.get('folder_id')
            )
            
            serializer = MediafileDashboardSerializer(media_file)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except InvalidFileTypeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except FileTooLargeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except StorageError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except MediaUploadError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in upload: {e}")
            return Response(
                {'error': 'Upload failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def regenerate_thumbnails(self, request, pk=None):
        """Regenerate thumbnails for this media file"""
        try:
            media_file = self.get_object()
            MediaService.regenerate_thumbnails(media_file)
            return Response(
                {'message': 'Thumbnails regenerated successfully'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error regenerating thumbnails: {e}")
            return Response(
                {'error': 'Failed to regenerate thumbnails'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """Bulk upload multiple files"""
        try:
            files = request.FILES.getlist('files')
            if not files:
                return Response(
                    {'error': 'No files provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            uploaded_files = []
            errors = []
            
            for file_obj in files:
                try:
                    media_file = MediaService.upload_file(
                        file_obj=file_obj,
                        store=getattr(request, 'store', None),
                        user=request.user,
                        alt_text=request.data.get('alt_text', ''),
                        description=request.data.get('description', ''),
                        folder_id=request.data.get('folder_id')
                    )
                    uploaded_files.append(media_file)
                except Exception as e:
                    errors.append({
                        'filename': file_obj.name,
                        'error': str(e)
                    })
            
            serializer = MediafileDashboardSerializer(uploaded_files, many=True)
            return Response({
                'uploaded': serializer.data,
                'errors': errors
            })
        except Exception as e:
            logger.error(f"Error in bulk upload: {e}")
            return Response(
                {'error': 'Bulk upload failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """Bulk delete media files"""
        try:
            serializer = BulkMediafileOperationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            file_ids = serializer.validated_data['file_ids']
            store = getattr(request, 'store', None)
            
            if store:
                deleted_count = MediaFile.objects.filter(
                    id__in=file_ids,
                    store=store
                ).delete()[0]
            else:
                deleted_count = 0
            
            return Response({
                'message': f'Deleted {deleted_count} files successfully'
            })
        except Exception as e:
            logger.error(f"Error in bulk delete: {e}")
            return Response(
                {'error': 'Failed to delete files'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def bulk_move(self, request):
        """Bulk move files to a different folder"""
        try:
            serializer = BulkMediafileOperationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            file_ids = serializer.validated_data['file_ids']
            folder_id = serializer.validated_data.get('folder_id')
            store = getattr(request, 'store', None)
            
            if store:
                updated_count = MediaFile.objects.filter(
                    id__in=file_ids,
                    store=store
                ).update(folder_id=folder_id)
            else:
                updated_count = 0
            
            return Response({
                'message': f'Moved {updated_count} files successfully'
            })
        except Exception as e:
            logger.error(f"Error in bulk move: {e}")
            return Response(
                {'error': 'Failed to move files'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get media file analytics for the store"""
        try:
            store = getattr(request, 'store', None)
            if not store:
                return Response(
                    {'error': 'Store not specified'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            analytics = MediaService.get_store_analytics(store)
            return Response(analytics)
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return Response(
                {'error': 'Failed to get analytics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def usage_stats(self, request):
        """Get storage usage statistics"""
        try:
            store = getattr(request, 'store', None)
            if not store:
                return Response(
                    {'error': 'Store not specified'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            stats = MediaService.get_storage_usage(store)
            return Response(stats)
        except Exception as e:
            logger.error(f"Error getting usage stats: {e}")
            return Response(
                {'error': 'Failed to get usage statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MediafolderDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard media folder management endpoints.
    """
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    permission_classes = [permissions.IsAuthenticated, IsStoreOwner]
    
    def get_queryset(self):
        """Filter by store"""
        queryset = MediaFolder.objects.all()
        store = getattr(self.request, 'store', None)
        if store:
            queryset = queryset.filter(store=store)
        return queryset.select_related('parent', 'created_by')
    
    def perform_create(self, serializer):
        """Set store and created_by from request"""
        store = getattr(self.request, 'store', None)
        if store:
            serializer.save(store=store, created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def tree(self, request, pk=None):
        """Get folder tree structure"""
        try:
            folder = self.get_object()
            tree = MediaService.get_folder_tree(folder)
            return Response(tree)
        except Exception as e:
            logger.error(f"Error getting folder tree: {e}")
            return Response(
                {'error': 'Failed to get folder tree'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def bulk_delete(self, request, pk=None):
        """Bulk delete folders and their contents"""
        try:
            folder = self.get_object()
            deleted_count = MediaService.delete_folder_contents(folder)
            return Response({
                'message': f'Deleted {deleted_count} items successfully'
            })
        except Exception as e:
            logger.error(f"Error in bulk delete folder: {e}")
            return Response(
                {'error': 'Failed to delete folder'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def root_folders(self, request):
        """Get root folders for the store"""
        try:
            store = getattr(self.request, 'store', None)
            if not store:
                return Response(
                    {'error': 'Store not specified'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            root_folders = MediaFolder.objects.filter(
                store=store,
                parent=None
            ).select_related('created_by')
            
            serializer = MediafolderDashboardSerializer(root_folders, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error getting root folders: {e}")
            return Response(
                {'error': 'Failed to get root folders'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


