"""
API views for cache module.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from rest_framework import viewsets
from core.permissions import IsStoreOwner
from ..models import CacheEntry
from .serializers import CacheEntrySerializer


class CacheViewSet(viewsets.ModelViewSet):
    """
    Cache management endpoints
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = CacheEntrySerializer
    
    def get_queryset(self):
        return CacheEntry.objects.filter(store=self.request.store)
    
    @extend_schema(
        summary="Get Cache Value",
        description="Get value from cache by key",
        responses={200: None}
    )
    @action(detail=False, methods=['get'])
    def get(self, request):
        """Get value from cache"""
        from ..services import CacheService
        
        key = request.query_params.get('key')
        if not key:
            return Response(
                {'error': 'key parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        value = CacheService.get(key, request.store)
        if value is None:
            return Response({'value': None})
        
        return Response({'value': value})
    
    @extend_schema(
        summary="Set Cache Value",
        description="Set value in cache",
        request=None,
        responses={200: None}
    )
    @action(detail=False, methods=['post'])
    def set(self, request):
        """Set value in cache"""
        from ..services import CacheService
        
        key = request.data.get('key')
        value = request.data.get('value')
        ttl = request.data.get('ttl')
        
        if not key or value is None:
            return Response(
                {'error': 'key and value required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cache_entry = CacheService.set(key, value, request.store, ttl)
        serializer = self.get_serializer(cache_entry)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Delete Cache Value",
        description="Delete value from cache by key",
        responses={200: None}
    )
    @action(detail=False, methods=['delete'])
    def delete(self, request):
        """Delete value from cache"""
        from ..services import CacheService
        
        key = request.query_params.get('key')
        if not key:
            return Response(
                {'error': 'key parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted = CacheService.delete(key, request.store)
        return Response({'deleted': deleted})
    
    @extend_schema(
        summary="Clear Cache",
        description="Clear all cache entries for store",
        responses={200: None}
    )
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear all cache entries"""
        from ..services import CacheService
        
        count = CacheService.clear(request.store)
        return Response({'cleared': count})
