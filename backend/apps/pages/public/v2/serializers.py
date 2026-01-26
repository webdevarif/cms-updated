"""
Public pages serializers - read-only interface for published pages.
Architectural + real implementation for public pages interface.
"""
from rest_framework import serializers
from apps.pages.models.pages import Post, PostType, Taxonomy, Term


class PagePublicSerializer(serializers.ModelSerializer):
    """Public page serializer with limited fields for read-only access."""
    
    url = serializers.SerializerMethodField()
    featured_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 
            'featured_image', 'meta_title', 'meta_description', 
            'meta_keywords', 'url', 'created_at', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_url(self, obj):
        """Generate absolute URL for the page."""
        if hasattr(obj, 'get_absolute_url'):
            return obj.get_absolute_url()
        return f"/pages/{obj.slug}/"
    
    def get_featured_image(self, obj):
        """Return featured image URL or null."""
        if obj.featured_image:
            return obj.featured_image.url
        return None


class PagePublicListSerializer(serializers.ModelSerializer):
    """Simplified public page serializer for list views."""
    
    featured_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 
            'featured_image', 'meta_title', 'meta_description', 
            'created_at', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_featured_image(self, obj):
        """Return featured image URL or null."""
        if obj.featured_image:
            return obj.featured_image.url
        return None
