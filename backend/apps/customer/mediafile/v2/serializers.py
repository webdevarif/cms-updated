"""
Customer mediafile serializers.
"""
from apps.mediafile.serializers import BaseMediaFileSerializer, BaseMediaFileUploadSerializer, BaseMediaFolderSerializer, BaseMediaFolderTreeSerializer


class MediafileCustomerSerializer(BaseMediaFileSerializer):
    """Serializer for MediaFile model in customer context"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove uploaded_by field for customer context (user is always current user)
        if 'uploaded_by' in self.fields:
            del self.fields['uploaded_by']


class MediafileUploadCustomerSerializer(BaseMediaFileUploadSerializer):
    """Serializer for file uploads in customer context"""
    pass


class MediafolderCustomerSerializer(BaseMediaFolderSerializer):
    """Serializer for MediaFolder model in customer context"""
    file_count = serializers.SerializerMethodField()
    
    def get_file_count(self, obj):
        """Get count of files uploaded by current user in this folder"""
        # Note: This will be calculated in the viewset for user-specific counts
        return 0


class MediafolderTreeCustomerSerializer(BaseMediaFolderTreeSerializer):
    """Serializer for folder tree structure in customer context"""
    
    def get_file_count(self, obj):
        """Get count of files in this folder"""
        # Note: This will be calculated in the viewset for user-specific counts
        return 0
