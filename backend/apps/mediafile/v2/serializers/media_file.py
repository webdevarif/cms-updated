"""
Serializers for media files.
"""
from rest_framework import serializers
from ...models.media_file import MediaFile


class MediaFileSerializer(serializers.ModelSerializer):
    """Serializer for MediaFile model"""
    url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    file_size_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = MediaFile
        fields = [
            'id', 'original_filename', 'file_extension', 'file_size', 'file_size_formatted',
            'mime_type', 'resource_type', 'width', 'height', 'alt_text', 'description',
            'folder', 'created_at', 'updated_at', 'url', 'thumbnail_url'
        ]
        read_only_fields = [
            'id', 'original_filename', 'file_extension', 'file_size', 'file_size_formatted',
            'mime_type', 'resource_type', 'width', 'height', 'created_at', 'updated_at',
            'url', 'thumbnail_url'
        ]
    
    def get_url(self, obj):
        """Get public URL for the media file"""
        return obj.get_absolute_url()
    
    def get_thumbnail_url(self, obj):
        """Get thumbnail URL for the media file"""
        return obj.get_thumbnail_url()
    
    def get_file_size_formatted(self, obj):
        """Get human-readable file size"""
        return obj.file_size_formatted


class MediaFileUploadSerializer(serializers.ModelSerializer):
    """Serializer for file uploads"""
    file = serializers.FileField(write_only=True)
    folder = serializers.PrimaryKeyRelatedField(
        queryset=MediaFile.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = MediaFile
        fields = ['file', 'folder', 'alt_text', 'description']
        read_only_fields = ['id']
