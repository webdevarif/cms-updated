"""
Base serializers for mediafile app.
"""

from apps.mediafile.models.media_file import MediaFile
from apps.mediafile.models.media_folder import MediaFolder
from rest_framework import serializers


class BaseMediaFileSerializer(serializers.ModelSerializer):
    """Base serializer for MediaFile model"""

    file_size_formatted = serializers.ReadOnlyField()
    is_image = serializers.ReadOnlyField()
    is_video = serializers.ReadOnlyField()
    is_document = serializers.ReadOnlyField()

    class Meta:
        model = MediaFile
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
            "is_image",
            "is_video",
            "is_document",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "file_size",
            "file_size_formatted",
            "mime_type",
            "resource_type",
            "storage_path",
            "imagekit_id",
            "width",
            "height",
            "uploaded_by",
            "is_image",
            "is_video",
            "is_document",
            "created_at",
            "updated_at",
        ]


class BaseMediaFileUploadSerializer(serializers.ModelSerializer):
    """Base serializer for file uploads"""

    file = serializers.FileField(write_only=True)

    class Meta:
        model = MediaFile
        fields = ["file", "original_filename", "alt_text", "description", "folder"]

    def create(self, validated_data):
        """Handle file upload through service"""
        file_obj = validated_data.pop("file")
        # Import here to avoid circular import
        from apps.mediafile.services.media_service import MediaService

        return MediaService.upload_file(
            file_obj=file_obj,
            store=validated_data.get("store"),
            user=validated_data.get("user"),
            alt_text=validated_data.get("alt_text", ""),
            description=validated_data.get("description", ""),
            folder_id=validated_data.get("folder_id"),
        )


class BaseMediaFolderSerializer(serializers.ModelSerializer):
    """Base serializer for MediaFolder model"""

    path = serializers.ReadOnlyField()

    class Meta:
        model = MediaFolder
        fields = [
            "id",
            "name",
            "slug",
            "store",
            "parent",
            "created_by",
            "path",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "store",
            "created_by",
            "path",
            "created_at",
            "updated_at",
        ]


class BaseMediaFolderTreeSerializer(serializers.Serializer):
    """Serializer for folder tree structure"""

    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    path = serializers.CharField()
    file_count = serializers.IntegerField()
    children = serializers.ListField(child=serializers.DictField())
