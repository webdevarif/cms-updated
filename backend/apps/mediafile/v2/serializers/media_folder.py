"""
Serializers for media folders.
"""
from rest_framework import serializers
from ...models.media_folder import MediaFolder


class MediaFolderSerializer(serializers.ModelSerializer):
    """Serializer for MediaFolder model"""
    file_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = MediaFolder
        fields = ['id', 'name', 'slug', 'parent', 'file_count', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'file_count', 'created_at', 'updated_at']
    
    def validate_parent(self, value):
        """Validate that parent folder belongs to the same store"""
        if value and value.store != self.context['request'].store:
            raise serializers.ValidationError("Parent folder does not belong to this store.")
        return value


class MediaFolderTreeSerializer(serializers.ModelSerializer):
    """Serializer for folder tree view"""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = MediaFolder
        fields = ['id', 'name', 'slug', 'file_count', 'children']
    
    def get_children(self, obj):
        """Recursively serialize children"""
        serializer = self.__class__(obj.children.all(), many=True, context=self.context)
        return serializer.data
