"""
Public mediafile API views.
"""
import logging

from apps.mediafile.models import MediaFile, MediaFolder
from apps.mediafile.services.media_service import MediaService
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import MediafilePublicSerializer, MediafolderPublicSerializer

logger = logging.getLogger(__name__)


class MediafilePublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public mediafile endpoints for read-only access to media files.
    Provides access to public media files and thumbnails.
    """

    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """Filter by store if provided, only return public files"""
        queryset = MediaFile.objects.all()
        store = getattr(self.request, "store", None)
        if store:
            queryset = queryset.filter(store=store)
        # Only return files that are marked as public (if such a field exists)
        # For now, return all files since the model doesn't have a public field
        return queryset.select_related("folder", "uploaded_by")

    @action(detail=True, methods=["get"])
    def thumbnail(self, request, pk=None):
        """Get thumbnail URL for this media file"""
        try:
            media_file = self.get_object()
            if not media_file.is_image:
                return Response(
                    {"error": "Thumbnails are only available for images"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            thumbnail_url = MediaService.get_thumbnail_url(media_file)
            return Response(
                {
                    "thumbnail_url": thumbnail_url,
                    "width": media_file.width,
                    "height": media_file.height,
                }
            )
        except Exception as e:
            logger.error(f"Error getting thumbnail: {e}")
            return Response(
                {"error": "Failed to get thumbnail"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["get"])
    def download_url(self, request, pk=None):
        """Get download URL for this media file"""
        try:
            media_file = self.get_object()
            download_url = MediaService.get_download_url(media_file)
            return Response(
                {
                    "download_url": download_url,
                    "filename": media_file.original_filename,
                    "file_size": media_file.file_size,
                    "mime_type": media_file.mime_type,
                }
            )
        except Exception as e:
            logger.error(f"Error getting download URL: {e}")
            return Response(
                {"error": "Failed to get download URL"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"])
    def transformations(self, request, pk=None):
        """Get available transformations for this media file"""
        try:
            media_file = self.get_object()
            if not media_file.is_image:
                return Response(
                    {"error": "Transformations are only available for images"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            transformations = MediaService.get_available_transformations(media_file)
            return Response({"transformations": transformations})
        except Exception as e:
            logger.error(f"Error getting transformations: {e}")
            return Response(
                {"error": "Failed to get transformations"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MediafolderPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public media folder endpoints for read-only access to folder structure.
    """

    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """Filter by store if provided"""
        queryset = MediaFolder.objects.all()
        store = getattr(self.request, "store", None)
        if store:
            queryset = queryset.filter(store=store)
        return queryset.select_related("parent", "created_by")

    @action(detail=True, methods=["get"])
    def files(self, request, pk=None):
        """Get files in this folder"""
        try:
            folder = self.get_object()
            files = MediaFile.objects.filter(folder=folder).select_related("uploaded_by")

            serializer = MediafilePublicSerializer(files, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error getting folder files: {e}")
            return Response(
                {"error": "Failed to get folder files"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"])
    def tree(self, request, pk=None):
        """Get folder tree structure starting from this folder"""
        try:
            folder = self.get_object()
            tree = MediaService.get_folder_tree(folder)
            return Response(tree)
        except Exception as e:
            logger.error(f"Error getting folder tree: {e}")
            return Response(
                {"error": "Failed to get folder tree"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"])
    def root(self, request):
        """Get root folders for the store"""
        try:
            store = getattr(self.request, "store", None)
            if not store:
                return Response(
                    {"error": "Store not specified"}, status=status.HTTP_400_BAD_REQUEST
                )

            root_folders = MediaFolder.objects.filter(store=store, parent=None).select_related(
                "created_by"
            )

            serializer = MediafolderPublicSerializer(root_folders, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error getting root folders: {e}")
            return Response(
                {"error": "Failed to get root folders"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
