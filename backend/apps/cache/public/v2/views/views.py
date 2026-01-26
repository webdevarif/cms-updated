"""
Public cache API views - read-only access to cache statistics.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.cache.models import CacheStats
from .serializers import CacheStatsSerializer


class CacheStatsPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public cache statistics API - read-only access to general cache performance.
    """
    permission_classes = [permissions.AllowAny]
    queryset = CacheStats.objects.filter(interval='daily').order_by('-period_start')[:30]
    serializer_class = CacheStatsSerializer

    @extend_schema(
        summary="Get cache statistics",
        description="Get public cache performance statistics"
    )
    def list(self, request, *args, **kwargs):
        """List cache statistics"""
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get overall cache performance summary"""
        # Get latest stats
        latest_stats = CacheStats.objects.filter(
            interval='daily'
        ).order_by('-period_start').first()

        if not latest_stats:
            return Response({
                'total_keys': 0,
                'hit_ratio': 0,
                'memory_usage': 0,
                'avg_response_time': 0
            })

        return Response({
            'total_keys': latest_stats.total_keys,
            'hit_ratio': round(latest_stats.hit_ratio, 2),
            'memory_usage': round(latest_stats.memory_usage_percent, 2),
            'avg_response_time': float(latest_stats.avg_response_time_ms),
            'total_hits': latest_stats.total_hits,
            'total_misses': latest_stats.total_misses
        })
