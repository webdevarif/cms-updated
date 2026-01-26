"""
Shared serializers for mediafile app.
"""
from rest_framework import serializers
from .models.media_file import MediaFile
from .models.media_folder import MediaFolder


class BaseMediaFileSerializer(serializers.ModelSerializer):
    """Base serializer for MediaFile model"""
    url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    file_size_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = MediaFile
        fields = [
            'id', 'original_filename', 'file_extension', 'file_size', 'file_size_formatted',
            'mime_type', 'resource_type', 'width', 'height', 'alt_text', 'description',
            'folder', 'uploaded_by', 'created_at', 'updated_at', 'url', 'thumbnail_url'
        ]
        read_only_fields = [
            'id', 'original_filename', 'file_extension', 'file_size', 'file_size_formatted',
            'mime_type', 'resource_type', 'width', 'height', 'uploaded_by', 'created_at', 'updated_at',
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


class BaseMediaFileUploadSerializer(serializers.ModelSerializer):
    """Base serializer for file uploads"""
    file = serializers.FileField(write_only=True)
    folder = serializers.PrimaryKeyRelatedField(
        queryset=MediaFolder.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = MediaFile
        fields = ['file', 'folder', 'alt_text', 'description']
        read_only_fields = ['id']


class BaseMediaFolderSerializer(serializers.ModelSerializer):
    """Base serializer for MediaFolder model"""
    
    class Meta:
        model = MediaFolder
        fields = [
            'id', 'name', 'parent', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class BaseMediaFolderTreeSerializer(serializers.ModelSerializer):
    """Base serializer for folder tree structure"""
    file_count = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = MediaFolder
        fields = ['id', 'name', 'parent_id', 'file_count', 'children']
    
    def get_children(self, obj):
        """Get child folders"""
        children = MediaFolder.objects.filter(parent=obj)
        return BaseMediaFolderTreeSerializer(children, many=True).data
