"""
Dashboard stores API.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from core.permissions import IsStoreOwner
from apps.stores.models import Store
from .serializers import StoreDashboardSerializer, StoreCreateDashboardSerializer
from apps.stores.services import StoreService


class StoreDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard store management endpoints for store owners and admins.
    Provides full CRUD access to stores with analytics and management actions.
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    queryset = Store.objects.all()
    serializer_class = StoreDashboardSerializer
    
    def get_queryset(self):
        """Filter by current user's stores"""
        return super().get_queryset().filter(owner=self.request.user)
    
    @extend_schema(
        summary="Create store",
        description="Create new store",
        request=StoreCreateDashboardSerializer,
        responses={201: StoreDashboardSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Create new store"""
        serializer = StoreCreateDashboardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        store = StoreService.create_store(
            owner=request.user,
            store_data=serializer.validated_data
        )
        
        return Response(
            StoreDashboardSerializer(store).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Update store",
        description="Update store details"
    )
    def update(self, request, *args, **kwargs):
        """Update store"""
        store = self.get_object()
        updated_store = StoreService.update_store(
            store=store,
            update_data=request.data,
            user=request.user
        )
        
        return Response(StoreDashboardSerializer(updated_store).data)
    
    @extend_schema(
        summary="Store analytics",
        description="Get store analytics data"
    )
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get store analytics"""
        store = self.get_object()
        days = int(request.GET.get('days', 30))
        
        analytics = StoreService.get_store_analytics(store, days)
        return Response(analytics)
    
    @extend_schema(
        summary="Suspend store",
        description="Suspend a store"
    )
    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """Suspend store"""
        store = self.get_object()
        StoreService.suspend_store(store, request.user)
        
        return Response({
            'status': 'suspended',
            'message': f'Store {store.name} has been suspended'
        })
    
    @extend_schema(
        summary="Activate store",
        description="Activate a suspended store"
    )
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate store"""
        store = self.get_object()
        StoreService.activate_store(store, request.user)
        
        return Response({
            'status': 'active',
            'message': f'Store {store.name} has been activated'
        })
    
    @extend_schema(
        summary="Bootstrap store",
        description="Initialize store with default data"
    )
    @action(detail=True, methods=['post'])
    def bootstrap(self, request, pk=None):
        """Bootstrap store with default data"""
        store = self.get_object()
        result = StoreService.bootstrap_store(store, request.user)
        
        return Response({
            'status': 'bootstrapped',
            'message': f'Store {store.name} has been bootstrapped',
            'created_items': result
        })
