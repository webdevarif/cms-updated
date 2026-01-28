"""
Public mediafile serializers.
"""
from apps.mediafile.serializers import BaseMediaFileSerializer, BaseMediaFolderSerializer
from rest_framework import serializers


class MediafilePublicSerializer(BaseMediaFileSerializer):
    """Public read-only serializer for MediaFile model"""

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
            "is_image",
            "is_video",
            "is_document",
            "created_at",
        ]
        # Exclude sensitive fields like storage_path, metadata, uploaded_by


class MediafolderPublicSerializer(BaseMediaFolderSerializer):
    """Public read-only serializer for MediaFolder model"""

    file_count = serializers.SerializerMethodField()

    class Meta(BaseMediaFolderSerializer.Meta):
        fields = ["id", "name", "slug", "path", "file_count", "created_at"]
        # Exclude sensitive fields like store, parent, created_by

    def get_file_count(self, obj):
        """Get count of files in this folder"""
        from apps.mediafile.models.media_file import MediaFile

        return MediaFile.objects.filter(folder=obj).count()
