"""
Public mediafile serializers.
"""
from apps.mediafile.serializers import BaseMediaFileSerializer, BaseMediaFolderSerializer, BaseMediaFolderTreeSerializer


class MediafilePublicSerializer(BaseMediaFileSerializer):
    """Serializer for MediaFile model in public context"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove uploaded_by field for public context
        if 'uploaded_by' in self.fields:
            del self.fields['uploaded_by']


class MediafolderPublicSerializer(BaseMediaFolderSerializer):
    """Serializer for MediaFolder model in public context"""
    file_count = serializers.SerializerMethodField()
    
    def get_file_count(self, obj):
        """Get count of public files in this folder"""
        from apps.mediafile.models.media_file import MediaFile
        return MediaFile.objects.filter(folder=obj, is_public=True).count()


class MediafolderTreePublicSerializer(BaseMediaFolderTreeSerializer):
    """Serializer for folder tree structure in public context"""
    file_count = serializers.SerializerMethodField()
    
    def get_file_count(self, obj):
        """Get count of public files in this folder"""
        from apps.mediafile.models.media_file import MediaFile
        return MediaFile.objects.filter(folder=obj, is_public=True).count()
