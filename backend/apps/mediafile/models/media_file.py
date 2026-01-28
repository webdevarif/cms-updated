"""
MediaFile model for media management.
"""
import os

from core.models import TenantModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class MediaFile(TenantModel):
    """
    Store-scoped media file stored in Cloudflare R2 with ImageKit.io processing.
    """

    # File types and size limits (in bytes)
    IMAGE_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    VIDEO_MAX_SIZE = 100 * 1024 * 1024  # 100MB
    DOCUMENT_MAX_SIZE = 20 * 1024 * 1024  # 20MB

    RESOURCE_TYPES = [
        ("image", "Image"),
        ("video", "Video"),
        ("document", "Document"),
        ("other", "Other"),
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
    folder = models.ForeignKey(
        "mediafile.MediaFolder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="media_files",
    )
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="uploaded_files"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = "mediafiles_media_file"
        indexes = [
            models.Index(fields=["store", "resource_type"]),
            models.Index(fields=["store", "folder"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["file_size"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return self.original_filename

    @property
    def file_size_formatted(self):
        """Return human-readable file size"""
        size = self.file_size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} GB"

    @property
    def is_image(self):
        return self.resource_type == "image"

    @property
    def is_video(self):
        return self.resource_type == "video"

    @property
    def is_document(self):
        return self.resource_type == "document"

    def get_absolute_url(self, transformation=None):
        """
        Get the public URL for this media file with optional transformations

        Args:
            transformation (str, optional): ImageKit transformation string

        Returns:
            str: Public URL with transformations applied
        """
        from ..services.media_service import MediaService

        return MediaService().get_media_url(self, transformation)

    def get_thumbnail_url(self, width=200, height=200, crop="fill"):
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

        transformation = f"tr:w-{width},h-{height},c-{crop}"
        return self.get_absolute_url(transformation)

    def get_presigned_url(self, expires_in=3600):
        """
        Generate a presigned URL for private file access

        Args:
            expires_in (int): Expiration time in seconds

        Returns:
            str: Presigned URL or None if not applicable
        """
        from ..services.media_service import MediaService

        return MediaService().get_presigned_url(self, expires_in)
