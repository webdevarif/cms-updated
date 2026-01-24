"""
Views for stores API v2.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema
from core.permissions import IsStoreOwner
from ..models import Store
from .serializers import StorePublicSerializer, StoreSerializer, StoreCreateSerializer
from .services import StoreService


class StorePublicViewSet(viewsets.ReadOnlyModelViewSet):
    """Public store API - no authentication required"""
    
    permission_classes = [AllowAny]
    queryset = Store.objects.filter(status='active')
    serializer_class = StorePublicSerializer
    
    def get_queryset(self):
        """Filter by domain or subdomain"""
        queryset = super().get_queryset()
        
        # Filter by domain if provided
        domain = self.request.GET.get('domain')
        if domain:
            queryset = queryset.filter(domain=domain)
        
        return queryset
    
    @extend_schema(
        summary="Get store by slug",
        description="Get public store details by slug",
        tags=["Stores Public"]
    )
    def retrieve(self, request, *args, **kwargs):
        """Get store details"""
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="List active stores",
        description="List all active stores",
        tags=["Stores Public"]
    )
    def list(self, request, *args, **kwargs):
        """List stores"""
        return super().list(request, *args, **kwargs)


class StoreViewSet(viewsets.ModelViewSet):
    """Store management API for dashboard"""
    
    permission_classes = [IsAuthenticated, IsStoreOwner]
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    
    def get_queryset(self):
        """Filter by current user's stores"""
        return super().get_queryset().filter(owner=self.request.user)
    
    @extend_schema(
        summary="Create store",
        description="Create new store",
        request=StoreCreateSerializer,
        responses={201: StoreSerializer},
        tags=["Stores Dashboard"]
    )
    def create(self, request, *args, **kwargs):
        """Create new store"""
        serializer = StoreCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        store = StoreService.create_store(
            owner=request.user,
            store_data=serializer.validated_data
        )
        
        return Response(
            StoreSerializer(store).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Update store",
        description="Update store details",
        tags=["Stores Dashboard"]
    )
    def update(self, request, *args, **kwargs):
        """Update store"""
        store = self.get_object()
        updated_store = StoreService.update_store(
            store=store,
            update_data=request.data,
            user=request.user
        )
        
        return Response(StoreSerializer(updated_store).data)
    
    @extend_schema(
        summary="Store analytics",
        description="Get store analytics data",
        tags=["Stores Dashboard"]
    )
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get store analytics"""
        store = self.get_object()
        days = int(request.GET.get('days', 30))
        
        analytics = StoreService.get_store_analytics(store, days)
        return Response(analytics)
