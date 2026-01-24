"""Template serializers."""
from rest_framework import serializers


class TemplatePublicSerializer(serializers.ModelSerializer):
    """Public template serializer"""
    
    class Meta:
        from ..models import Template
        model = Template
        fields = ['id', 'name', 'key', 'template_role', 'description', 'content', 'variables']
        read_only_fields = ['id']


class TemplateSerializer(serializers.ModelSerializer):
    """Template serializer"""
    
    class Meta:
        from ..models import Template
        model = Template
        fields = ['id', 'theme', 'store', 'name', 'key', 'template_role', 'description', 'content', 
                  'custom_css', 'custom_js', 'meta_title', 'meta_description', 'meta_keywords',
                  'is_default', 'is_active', 'is_system', 'layout', 'variables', 'requires',
                  'preview_image', 'preview_data', 'cache_duration', 'minify_html']
        read_only_fields = ['id']


class TemplateCreateSerializer(serializers.ModelSerializer):
    """Template create serializer"""
    
    class Meta:
        from ..models import Template
        model = Template
        fields = ['name', 'key', 'template_role', 'description', 'content', 'custom_css', 'custom_js',
                  'meta_title', 'meta_description', 'meta_keywords', 'is_default', 'is_active',
                  'layout', 'variables', 'requires', 'preview_image', 'preview_data', 'cache_duration', 'minify_html']
