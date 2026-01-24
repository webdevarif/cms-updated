"""
Serializers for cache module.
"""
from rest_framework import serializers
from ..models import CacheEntry


class CacheEntrySerializer(serializers.ModelSerializer):
    """Serializer for CacheEntry"""
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CacheEntry
        fields = [
            'id', 'store', 'key', 'value', 'expires_at',
            'created_at', 'updated_at', 'is_expired'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
