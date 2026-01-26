"""
Dashboard themes serializers.
"""
from rest_framework import serializers
from apps.themes.models import Theme, Template


class ThemeDashboardSerializer(serializers.ModelSerializer):
    """Serializer for Theme model in dashboard context"""
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Theme
        fields = [
            'id', 'store', 'name', 'is_active', 'created_by', 'owner_email',
            'status_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'owner_email', 'created_at', 'updated_at']


class ThemeCreateDashboardSerializer(serializers.ModelSerializer):
    """Theme creation serializer in dashboard context"""
    
    class Meta:
        model = Theme
        fields = ['name', 'is_active']


class TemplateDashboardSerializer(serializers.ModelSerializer):
    """Serializer for Template model in dashboard context"""
    theme_name = serializers.CharField(source='theme.name', read_only=True)
    template_role_display = serializers.CharField(source='get_template_role_display', read_only=True)
    
    class Meta:
        model = Template
        fields = [
            'id', 'theme', 'store', 'name', 'key', 'template_role', 'description', 'content', 
            'custom_css', 'custom_js', 'meta_title', 'meta_description', 'meta_keywords',
            'is_default', 'is_active', 'is_system', 'layout', 'variables', 'requires',
            'preview_image', 'preview_data', 'cache_duration', 'minify_html',
            'theme_name', 'template_role_display'
        ]
        read_only_fields = ['id', 'theme', 'theme_name', 'template_role_display']


class TemplateCreateDashboardSerializer(serializers.ModelSerializer):
    """Template creation serializer in dashboard context"""
    
    class Meta:
        model = Template
        fields = [
            'name', 'key', 'template_role', 'description', 'content', 'custom_css', 'custom_js',
            'meta_title', 'meta_description', 'meta_keywords', 'is_default', 'is_active',
            'layout', 'variables', 'requires', 'preview_image', 'preview_data', 'cache_duration', 'minify_html'
        ]
