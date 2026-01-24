"""Color scheme serializers."""
from rest_framework import serializers


class ColorSchemePublicSerializer(serializers.ModelSerializer):
    """Public color scheme serializer"""
    
    class Meta:
        from ..models import ColorScheme
        model = ColorScheme
        fields = ['id', 'name', 'key', 'colors', 'dark_colors', 'is_default']
        read_only_fields = ['id']


class ColorSchemeSerializer(serializers.ModelSerializer):
    """Color scheme serializer"""
    
    class Meta:
        from ..models import ColorScheme
        model = ColorScheme
        fields = ['id', 'theme', 'store', 'name', 'key', 'colors', 'dark_colors', 'is_default']
        read_only_fields = ['id']
