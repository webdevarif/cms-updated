"""
Public stores API.
"""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.db import models
from drf_spectacular.utils import extend_schema

from apps.stores.models import Store
from .serializers import StorePublicSerializer


class StorePublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public store API - no authentication required.
    Provides read-only access to active stores for discovery.
    """
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
    
    @extend_schema(
        summary="Discover stores",
        description="Discover stores with search and filtering",
        tags=["Stores Public"]
    )
    @action(detail=False, methods=['get'])
    def discover(self, request):
        """Discover stores with advanced filtering"""
        queryset = self.get_queryset()
        
        # Search by name or description
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(description__icontains=search)
            )
        
        # Filter by store type
        store_type = request.GET.get('store_type')
        if store_type:
            queryset = queryset.filter(store_type=store_type)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
