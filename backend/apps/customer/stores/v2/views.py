"""
Customer stores API.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from core.permissions import IsStoreUser
from apps.stores.models import Store
from .serializers import StoreCustomerSerializer, StoreSettingsCustomerSerializer
from apps.stores.services import StoreService


class StoreCustomerViewSet(viewsets.ModelViewSet):
    """
    Customer store management endpoints for authenticated users.
    Users can manage their own store settings.
    """
    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = StoreCustomerSerializer
    
    def get_queryset(self):
        """Filter by current user's store"""
        return Store.objects.filter(owner=self.request.user)
    
    @extend_schema(
        summary="Get store settings",
        description="Get current user's store settings"
    )
    @action(detail=False, methods=['get'])
    def settings(self, request):
        """Get store settings"""
        store = self.get_queryset().first()
        if not store:
            return Response(
                {'detail': 'No store found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = StoreSettingsSerializer(store)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Update store settings",
        description="Update current user's store settings"
    )
    @action(detail=False, methods=['patch'])
    def update_settings(self, request):
        """Update store settings"""
        store = self.get_queryset().first()
        if not store:
            return Response(
                {'detail': 'No store found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = StoreSettingsSerializer(store, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get store analytics",
        description="Get current user's store analytics"
    )
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get store analytics"""
        store = self.get_queryset().first()
        if not store:
            return Response(
                {'detail': 'No store found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        days = int(request.GET.get('days', 30))
        analytics = StoreService.get_store_analytics(store, days)
        return Response(analytics)
