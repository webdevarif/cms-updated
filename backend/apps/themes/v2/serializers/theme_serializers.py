"""Theme serializers."""
from rest_framework import serializers


class ThemePublicSerializer(serializers.ModelSerializer):
    """Public theme serializer"""
    
    class Meta:
        from ..models import Theme
        model = Theme
        fields = ['id', 'name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ThemeSerializer(serializers.ModelSerializer):
    """Theme serializer"""
    
    class Meta:
        from ..models import Theme
        model = Theme
        fields = ['id', 'store', 'name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ThemeCreateSerializer(serializers.ModelSerializer):
    """Theme create serializer"""
    
    class Meta:
        from ..models import Theme
        model = Theme
        fields = ['name', 'is_active']
