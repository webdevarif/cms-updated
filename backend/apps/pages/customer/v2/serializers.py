"""
Customer pages serializers - authenticated user manages own pages.
Architectural + real implementation for customer pages interface.
"""
from rest_framework import serializers
from apps.pages.models.pages import Post, PostType


class PageCustomerSerializer(serializers.ModelSerializer):
    """Customer page serializer for managing own pages."""
    
    featured_image = serializers.SerializerMethodField()
    post_type_name = serializers.CharField(source='post_type.name', read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'status',
            'featured_image', 'post_type', 'post_type_name',
            'meta_title', 'meta_description', 'meta_keywords',
            'created_at', 'updated_at', 'author'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'post_type_name']
    
    def get_featured_image(self, obj):
        """Return featured image URL or null."""
        if obj.featured_image:
            return obj.featured_image.url
        return None
    
    def create(self, validated_data):
        """Create page with current user as author."""
        # Set default post type to 'page' if not provided
        if 'post_type' not in validated_data:
            page_type = PostType.objects.filter(slug='page').first()
            if page_type:
                validated_data['post_type'] = page_type
        
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class PageCustomerListSerializer(serializers.ModelSerializer):
    """Simplified customer page serializer for list views."""
    
    featured_image = serializers.SerializerMethodField()
    post_type_name = serializers.CharField(source='post_type.name', read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'status', 'excerpt',
            'featured_image', 'post_type_name', 'created_at', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_featured_image(self, obj):
        """Return featured image URL or null."""
        if obj.featured_image:
            return obj.featured_image.url
        return None
