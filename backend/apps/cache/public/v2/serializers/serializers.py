"""
Public cache serializers - read-only cache statistics.
"""
from rest_framework import serializers
from apps.cache.models import CacheStats


class CacheStatsSerializer(serializers.ModelSerializer):
    """Public cache statistics serializer"""

    hit_ratio = serializers.SerializerMethodField()
    memory_usage = serializers.SerializerMethodField()

    class Meta:
        model = CacheStats
        fields = [
            'store', 'interval', 'period_start', 'total_keys',
            'total_hits', 'total_misses', 'hit_ratio', 'memory_usage',
            'avg_response_time_ms', 'created_at'
        ]

    def get_hit_ratio(self, obj):
        """Calculate and return hit ratio"""
        return round(obj.hit_ratio, 2)

    def get_memory_usage(self, obj):
        """Calculate and return memory usage percentage"""
        return round(obj.memory_usage_percent, 2)
