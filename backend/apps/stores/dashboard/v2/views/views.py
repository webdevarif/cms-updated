"""
Dashboard stores API views.
"""

from apps.stores.models import Store, StoreSettings
from apps.stores.services import StoreService
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..serializers.serializers import StoreDashboardSerializer, StoreSettingsSerializer


class StoreDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard store API - store owners manage their stores.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = StoreDashboardSerializer

    def get_queryset(self):
        """Filter to user's owned stores"""
        if getattr(self, "swagger_fake_view", False):
            # Return empty queryset for schema generation
            return Store.objects.none()
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
    def store_settings(self, request, pk=None):
        """Manage store settings"""
        store = self.get_object()

        if request.method == "GET":
            settings = store.store_settings
            serializer = StoreSettingsSerializer(settings)
            return Response(serializer.data)
        else:
            settings = store.store_settings
            serializer = StoreSettingsSerializer(settings, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
