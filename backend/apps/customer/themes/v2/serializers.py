"""
Customer themes serializers.
"""
from rest_framework import serializers
from apps.themes.models import Theme, Template


class ThemeCustomerSerializer(serializers.ModelSerializer):
    """Serializer for Theme model in customer context"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Theme
        fields = [
            'id', 'name', 'description', 'logo', 'is_active',
            'status_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TemplateCustomerSerializer(serializers.ModelSerializer):
    """Serializer for Template model in customer context"""
    template_role_display = serializers.CharField(source='get_template_role_display', read_only=True)
    
    class Meta:
        model = Template
        fields = [
            'id', 'theme', 'name', 'key', 'template_role', 'description', 'content', 'variables',
            'is_default', 'is_active', 'template_role_display'
        ]
        read_only_fields = ['id', 'theme']
