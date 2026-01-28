"""
Customer mediafile serializers.
"""
from apps.mediafile.serializers import (
    BaseMediaFileSerializer,
    BaseMediaFileUploadSerializer,
    BaseMediaFolderSerializer,
)
from rest_framework import serializers


class MediafileCustomerSerializer(BaseMediaFileSerializer):
    """Customer serializer for MediaFile model"""

    class Meta(BaseMediaFileSerializer.Meta):
        fields = [
            "id",
            "original_filename",
            "file_extension",
            "file_size",
            "file_size_formatted",
            "mime_type",
            "resource_type",
            "imagekit_id",
            "width",
            "height",
            "alt_text",
            "description",
            "folder",
            "uploaded_by",
            "is_image",
            "is_video",
            "is_document",
            "created_at",
            "updated_at",
        ]
        # Exclude sensitive fields like storage_path, metadata


class MediafileUploadCustomerSerializer(BaseMediaFileUploadSerializer):
    """Customer serializer for file uploads"""

    class Meta(BaseMediaFileUploadSerializer.Meta):
        fields = ["file", "original_filename", "alt_text", "description", "folder"]


class MediafolderCustomerSerializer(BaseMediaFolderSerializer):
    """Customer serializer for MediaFolder model"""

    file_count = serializers.SerializerMethodField()

    class Meta(BaseMediaFolderSerializer.Meta):
        fields = ["id", "name", "slug", "parent", "path", "file_count", "created_at", "updated_at"]
        # Exclude sensitive fields like store, created_by

    def get_file_count(self, obj):
        """Get count of files in this folder uploaded by the user"""
        from apps.mediafile.models.media_file import MediaFile

        return MediaFile.objects.filter(folder=obj).count()


class BulkMediafileDeleteSerializer(serializers.Serializer):
    """Serializer for bulk deleting media files"""

    file_ids = serializers.ListField(
        child=serializers.IntegerField(), help_text="List of file IDs to delete"
    )
