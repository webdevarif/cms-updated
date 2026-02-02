"""
Dashboard mediafile serializers.
"""

from apps.mediafile.serializers import (
    BaseMediaFileSerializer,
    BaseMediaFileUploadSerializer,
    BaseMediaFolderSerializer,
    BaseMediaFolderTreeSerializer,
)
from rest_framework import serializers


class MediafileDashboardSerializer(BaseMediaFileSerializer):
    """Dashboard serializer for MediaFile model"""

    uploaded_by_email = serializers.EmailField(source="uploaded_by.email", read_only=True)

    class Meta(BaseMediaFileSerializer.Meta):
        fields = [
            "id",
            "original_filename",
            "file_extension",
            "file_size",
            "file_size_formatted",
            "mime_type",
            "resource_type",
            "storage_path",
            "imagekit_id",
            "width",
            "height",
            "alt_text",
            "description",
            "metadata",
            "folder",
            "uploaded_by",
            "uploaded_by_email",
            "is_image",
            "is_video",
            "is_document",
            "created_at",
            "updated_at",
        ]


class MediafileUploadDashboardSerializer(BaseMediaFileUploadSerializer):
    """Dashboard serializer for file uploads"""

    class Meta(BaseMediaFileUploadSerializer.Meta):
        fields = ["file", "original_filename", "alt_text", "description", "folder"]


class MediafolderDashboardSerializer(BaseMediaFolderSerializer):
    """Dashboard serializer for MediaFolder model"""

    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    file_count = serializers.SerializerMethodField()

    class Meta(BaseMediaFolderSerializer.Meta):
        fields = [
            "id",
            "name",
            "slug",
            "store",
            "parent",
            "created_by",
            "created_by_email",
            "path",
            "file_count",
            "created_at",
            "updated_at",
        ]

    def get_file_count(self, obj):
        """Get count of files in this folder"""
        from apps.mediafile.models.media_file import MediaFile

        return MediaFile.objects.filter(folder=obj).count()


class MediafolderTreeDashboardSerializer(BaseMediaFolderTreeSerializer):
    """Dashboard serializer for folder tree structure"""

    pass


class BulkMediafileOperationSerializer(serializers.Serializer):
    """Serializer for bulk mediafile operations"""

    file_ids = serializers.ListField(
        child=serializers.IntegerField(), help_text="List of file IDs to operate on"
    )
    folder_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Target folder ID for move operations",
    )


class MediafileAnalyticsSerializer(serializers.Serializer):
    """Serializer for mediafile analytics"""

    total_files = serializers.IntegerField()
    total_size = serializers.IntegerField()
    files_by_type = serializers.DictField()
    files_by_folder = serializers.DictField()
    upload_trend = serializers.ListField(child=serializers.DictField())
    storage_usage = serializers.DictField()


class StorageUsageSerializer(serializers.Serializer):
    """Serializer for storage usage statistics"""

    total_storage = serializers.IntegerField()
    used_storage = serializers.IntegerField()
    available_storage = serializers.IntegerField()
    usage_percentage = serializers.FloatField()
    files_by_type = serializers.DictField()
    largest_files = serializers.ListField(child=serializers.DictField())
