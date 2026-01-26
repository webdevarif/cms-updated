"""
Dashboard mediafile serializers.
"""
from apps.mediafile.serializers import BaseMediaFileSerializer, BaseMediaFileUploadSerializer, BaseMediaFolderSerializer, BaseMediaFolderTreeSerializer


class MediafileDashboardSerializer(BaseMediaFileSerializer):
    """Serializer for MediaFile model in dashboard context"""
    uploaded_by_email = serializers.EmailField(source='uploaded_by.email', read_only=True)


class MediafileUploadDashboardSerializer(BaseMediaFileUploadSerializer):
    """Serializer for file uploads in dashboard context"""
    pass


class MediafolderDashboardSerializer(BaseMediaFolderSerializer):
    """Serializer for MediaFolder model in dashboard context"""
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    file_count = serializers.SerializerMethodField()
    
    def get_file_count(self, obj):
        """Get count of files in this folder"""
        from apps.mediafile.models.media_file import MediaFile
        return MediaFile.objects.filter(folder=obj).count()


class MediafolderTreeDashboardSerializer(BaseMediaFolderTreeSerializer):
    """Serializer for folder tree structure in dashboard context"""
    file_count = serializers.SerializerMethodField()
    
    def get_file_count(self, obj):
        """Get count of files in this folder"""
        from apps.mediafile.models.media_file import MediaFile
        return MediaFile.objects.filter(folder=obj).count()
