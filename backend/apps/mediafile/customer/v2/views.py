"""
Customer mediafile API views.
"""

import logging

from apps.mediafile.exceptions import (
    FileTooLargeError,
    InvalidFileTypeError,
    MediaUploadError,
    StorageError,
)
from apps.mediafile.models import MediaFile, MediaFolder
from apps.mediafile.services.media_service import MediaService
from core.permissions import IsStoreUser
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response

from django.core.exceptions import ValidationError
from django.db.models import Count, Q

from .serializers import (
    MediafileCustomerSerializer,
    MediafileUploadCustomerSerializer,
    MediafolderCustomerSerializer,
)

logger = logging.getLogger(__name__)


class MediafileCustomerViewSet(viewsets.ModelViewSet):
    """
    Customer media file management endpoints.
    Authenticated users can upload, list, and manage their own media files.
    """

    parser_classes = [MultiPartParser, JSONParser]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["original_filename", "alt_text", "description"]
    ordering_fields = ["created_at", "file_size", "original_filename"]
    permission_classes = [permissions.IsAuthenticated, IsStoreUser]

    def get_queryset(self):
        """Filter by store and uploaded_by user"""
        queryset = MediaFile.objects.all()
        store = getattr(self.request, "store", None)
        if store:
            queryset = queryset.filter(store=store, uploaded_by=self.request.user)
        return queryset.select_related("folder", "uploaded_by")

    @action(detail=False, methods=["post"])
    def upload(self, request):
        """Upload a new media file"""
        try:
            file_obj = request.FILES.get("file")
            if not file_obj:
                return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

            # Use MediaService to handle upload
            media_file = MediaService.upload_file(
                file_obj=file_obj,
                store=getattr(request, "store", None),
                user=request.user,
                alt_text=request.data.get("alt_text", ""),
                description=request.data.get("description", ""),
                folder_id=request.data.get("folder_id"),
            )

            serializer = MediafileCustomerSerializer(media_file)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except InvalidFileTypeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except FileTooLargeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except StorageError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except MediaUploadError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in upload: {e}")
            return Response(
                {"error": "Upload failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def regenerate_thumbnails(self, request, pk=None):
        """Regenerate thumbnails for this media file"""
        try:
            media_file = self.get_object()
            MediaService.regenerate_thumbnails(media_file)
            return Response(
                {"message": "Thumbnails regenerated successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error regenerating thumbnails: {e}")
            return Response(
                {"error": "Failed to regenerate thumbnails"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def bulk_delete(self, request, pk=None):
        """Bulk delete media files"""
        try:
            file_ids = request.data.get("file_ids", [])
            if not file_ids:
                return Response(
                    {"error": "No file IDs provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Only allow deletion of user's own files
            deleted_count = MediaFile.objects.filter(
                id__in=file_ids,
                store=getattr(request, "store", None),
                uploaded_by=request.user,
            ).delete()[0]

            return Response({"message": f"Deleted {deleted_count} files successfully"})
        except Exception as e:
            logger.error(f"Error in bulk delete: {e}")
            return Response(
                {"error": "Failed to delete files"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def my_files(self, request):
        """Get files uploaded by the current user"""
        queryset = self.get_queryset()
        serializer = MediafileCustomerSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def usage_stats(self, request):
        """Get usage statistics for the user"""
        try:
            store = getattr(request, "store", None)
            if not store:
                return Response(
                    {"error": "Store not specified"}, status=status.HTTP_400_BAD_REQUEST
                )

            stats = MediaService.get_user_usage_stats(request.user, store)
            return Response(stats)
        except Exception as e:
            logger.error(f"Error getting usage stats: {e}")
            return Response(
                {"error": "Failed to get usage statistics"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MediafolderCustomerViewSet(viewsets.ModelViewSet):
    """
    Customer media folder management endpoints.
    Authenticated users can create and manage their own folders.
    """

    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    permission_classes = [permissions.IsAuthenticated, IsStoreOwner]

    def get_queryset(self):
        """Filter by store and created_by user"""
        queryset = MediaFolder.objects.all()
        store = getattr(self.request, "store", None)
        if store:
            queryset = queryset.filter(store=store, created_by=self.request.user)
        return queryset.select_related("parent", "created_by")

    def perform_create(self, serializer):
        """Set store and created_by from request"""
        store = getattr(self.request, "store", None)
        if store:
            serializer.save(store=store, created_by=self.request.user)

    @action(detail=True, methods=["get"])
    def files(self, request, pk=None):
        """Get files in this folder uploaded by the user"""
        try:
            folder = self.get_object()
            files = MediaFile.objects.filter(
                folder=folder, uploaded_by=request.user
            ).select_related("uploaded_by")

            serializer = MediafileCustomerSerializer(files, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error getting folder files: {e}")
            return Response(
                {"error": "Failed to get folder files"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"])
    def tree(self, request, pk=None):
        """Get folder tree structure for user's folders"""
        try:
            folder = self.get_object()
            tree = MediaService.get_user_folder_tree(folder, request.user)
            return Response(tree)
        except Exception as e:
            logger.error(f"Error getting folder tree: {e}")
            return Response(
                {"error": "Failed to get folder tree"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def my_folders(self, request):
        """Get folders created by the current user"""
        queryset = self.get_queryset()
        serializer = MediafolderCustomerSerializer(queryset, many=True)
        return Response(serializer.data)
