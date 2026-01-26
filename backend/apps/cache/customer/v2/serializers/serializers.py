"""
Customer cache serializers - manage own cache keys.
"""
from rest_framework import serializers
from apps.cache.models import Cache


class CacheSerializer(serializers.ModelSerializer):
    """Customer cache serializer"""

    hit_ratio = serializers.SerializerMethodField()

    class Meta:
        model = Cache
        fields = [
            'id', 'key', 'cache_type', 'content_type', 'object_id',
            'tags', 'size_bytes', 'hits', 'misses', 'hit_ratio',
            'expires_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'hits', 'misses']

    def get_hit_ratio(self, obj):
        """Calculate and return hit ratio"""
        return round(obj.hit_ratio, 2)
