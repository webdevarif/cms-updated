"""
Dashboard cache serializers - full cache administration and monitoring.
"""
from apps.cache.models import Cache, CacheStats
from rest_framework import serializers


class CacheSerializer(serializers.ModelSerializer):
    """Dashboard cache serializer"""

    hit_ratio = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = Cache
        fields = [
            "id",
            "key",
            "cache_type",
            "store",
            "content_type",
            "object_id",
            "tags",
            "size_bytes",
            "hits",
            "misses",
            "hit_ratio",
            "is_expired",
            "expires_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_hit_ratio(self, obj):
        """Calculate and return hit ratio"""
        return round(obj.hit_ratio, 2)

    def get_is_expired(self, obj):
        """Check if cache entry is expired"""
        return obj.is_expired


class CacheStatsSerializer(serializers.ModelSerializer):
    """Dashboard cache statistics serializer"""

    hit_ratio = serializers.SerializerMethodField()
    memory_usage = serializers.SerializerMethodField()

    class Meta:
        model = CacheStats
        fields = [
            "store",
            "interval",
            "period_start",
            "total_keys",
            "total_size_bytes",
            "expired_keys",
            "total_hits",
            "total_misses",
            "hit_ratio",
            "avg_response_time_ms",
            "memory_usage",
            "cpu_usage_percent",
            "connections_active",
            "created_at",
        ]

    def get_hit_ratio(self, obj):
        """Calculate and return hit ratio"""
        return round(obj.hit_ratio, 2)

    def get_memory_usage(self, obj):
        """Calculate and return memory usage percentage"""
        return round(obj.memory_usage_percent, 2)
