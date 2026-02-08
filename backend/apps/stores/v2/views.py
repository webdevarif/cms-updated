"""
Stores V2 API views.
Consolidated views from public, customer, and dashboard layers.
"""

from apps.stores.models import Store, StoreSettings
from apps.stores.services import StoreService
from core.permissions import IsStoreOwner, IsStoreUser
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django.db import models


class StorePublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public store API - no authentication required.
    Provides read-only access to active stores for discovery.
    """

    permission_classes = [AllowAny]
    queryset = Store.objects.filter(status="active")
    serializer_class = None  # Will be set in get_serializer_class

    def get_serializer_class(self):
        from .serializers import StorePublicSerializer

        return StorePublicSerializer

    def get_queryset(self):
        """Filter by domain or subdomain"""
        queryset = super().get_queryset()

        # Filter by domain if provided
        domain = self.request.GET.get("domain")
        if domain:
            queryset = queryset.filter(domain=domain)

        # Filter by subdomain if provided
        subdomain = self.request.GET.get("subdomain")
        if subdomain:
            queryset = queryset.filter(slug=subdomain)

        return queryset

    @extend_schema(summary="List stores", description="List active stores")
    def list(self, request, *args, **kwargs):
        """List stores"""
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Get store", description="Get store details")
    def retrieve(self, request, *args, **kwargs):
        """Get store details"""
        return super().retrieve(request, *args, **kwargs)


class StoreCustomerViewSet(viewsets.ModelViewSet):
    """
    Customer store API - authenticated users manage their own stores.
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = None  # Will be set in get_serializer_class

    def get_serializer_class(self):
        from .serializers import StoreCustomerSerializer

        return StoreCustomerSerializer

    def get_queryset(self):
        """Filter to user's own stores"""
        return Store.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """Set owner when creating store"""
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def verify_email(self, request, pk=None):
        """Verify store email with token"""
        store = self.get_object()
        token = request.data.get("token")

        if StoreService.verify_store(store, token):
            return Response({"message": "Store verified successfully"})
        return Response({"error": "Invalid verification token"}, status=status.HTTP_400_BAD_REQUEST)


class StoreDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard store API - store owners manage their stores.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = None  # Will be set in get_serializer_class

    def get_serializer_class(self):
        from .serializers import StoreDashboardSerializer, StoreSettingsSerializer

        if self.action == "settings":
            return StoreSettingsSerializer
        return StoreDashboardSerializer

    def get_queryset(self):
        """Filter to user's owned stores"""
        return Store.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """Set owner when creating store"""
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a store"""
        store = self.get_object()
        StoreService.update_store(store, {"status": "active"}, request.user)
        return Response({"message": "Store activated"})

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a store"""
        store = self.get_object()
        StoreService.update_store(store, {"status": "inactive"}, request.user)
        return Response({"message": "Store deactivated"})

    @action(detail=True, methods=["get"])
    def analytics(self, request, pk=None):
        """Get store analytics"""
        store = self.get_object()
        days = int(request.GET.get("days", 30))
        analytics = StoreService.get_store_analytics(store, days)
        return Response(analytics)

    @action(detail=True, methods=["get", "put", "patch"])
    def settings(self, request, pk=None):
        """Manage store settings"""
        store = self.get_object()

        if request.method == "GET":
            settings = store.store_settings
            serializer = self.get_serializer(settings)
            return Response(serializer.data)
        else:
            settings = store.store_settings
            serializer = self.get_serializer(settings, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
