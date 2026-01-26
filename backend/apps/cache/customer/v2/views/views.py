"""
Customer cache API views - manage own cache keys.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from core.permissions import IsStoreUser
from apps.cache.models import Cache
from apps.cache.services import CacheService
from .serializers import CacheSerializer


class CacheCustomerViewSet(viewsets.ModelViewSet):
    """
    Customer cache API - manage cache keys for own store.
    """
    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = CacheSerializer

    def get_queryset(self):
        """Filter to store's cache entries"""
        return Cache.objects.filter(store=self.request.store)

    @action(detail=False, methods=['post'])
    def set_key(self, request):
        """Set a cache key"""
        key = request.data.get('key')
        value = request.data.get('value')
        ttl = request.data.get('ttl', 3600)  # Default 1 hour

        if not key or value is None:
            return Response(
                {'error': 'Key and value are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            CacheService.set(
                key=key,
                value=value,
                store=self.request.store,
                ttl=ttl,
                user=request.user
            )
            return Response({'message': f'Cache key "{key}" set successfully'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def get_key(self, request):
        """Get a cache key"""
        key = request.query_params.get('key')

        if not key:
            return Response(
                {'error': 'Key parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            value = CacheService.get(key, self.request.store)
            if value is not None:
                return Response({'key': key, 'value': value})
            else:
                return Response(
                    {'error': 'Cache key not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['delete'])
    def delete_key(self, request):
        """Delete a cache key"""
        key = request.data.get('key')

        if not key:
            return Response(
                {'error': 'Key is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            CacheService.invalidate_key(key, self.request.store)
            return Response({'message': f'Cache key "{key}" deleted successfully'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
