"""
Dashboard cache API views - full cache administration and monitoring.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from core.permissions import IsStoreOwner
from apps.cache.models import Cache, CacheStats
from apps.cache.services import CacheService
from .serializers import CacheSerializer, CacheStatsSerializer


class CacheDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard cache API - full cache administration.
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = CacheSerializer

    def get_queryset(self):
        """Filter to store's cache entries"""
        return Cache.objects.filter(store=self.request.store)

    @action(detail=False, methods=['post'])
    def clear_all(self, request):
        """Clear all cache entries for the store"""
        try:
            count = CacheService.clear_store_cache(self.request.store)
            return Response({
                'message': f'Successfully cleared {count} cache entries'
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def invalidate_by_tags(self, request):
        """Invalidate cache entries by tags"""
        tags = request.data.get('tags', [])
        if not tags:
            return Response(
                {'error': 'Tags list is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            total_invalidated = 0
            for tag in tags:
                count = CacheService.invalidate_by_tag(tag, self.request.store)
                total_invalidated += count

            return Response({
                'message': f'Invalidated {total_invalidated} cache entries with tags: {tags}'
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def performance_stats(self, request):
        """Get detailed cache performance statistics"""
        try:
            stats = CacheService.get_performance_stats(self.request.store)
            return Response(stats)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CacheStatsDashboardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Dashboard cache statistics API - detailed monitoring.
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = CacheStatsSerializer

    def get_queryset(self):
        """Filter to store's cache statistics"""
        return CacheStats.objects.filter(store=self.request.store).order_by('-period_start')

    @action(detail=False, methods=['get'])
    def realtime_stats(self, request):
        """Get real-time cache statistics"""
        try:
            stats = CacheService.get_realtime_stats(self.request.store)
            return Response(stats)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
