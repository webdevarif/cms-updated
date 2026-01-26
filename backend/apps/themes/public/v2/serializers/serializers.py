"""
Public themes serializers.
"""
from rest_framework import serializers
from apps.themes.models import Theme


class ThemePublicSerializer(serializers.ModelSerializer):
    """Public theme information"""

    class Meta:
        model = Theme
        fields = [
            'id', 'name', 'slug', 'description', 'preview_image',
            'is_default', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
