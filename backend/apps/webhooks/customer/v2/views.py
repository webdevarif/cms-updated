"""
Customer webhooks API.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from core.permissions import IsStoreUser
from apps.webhooks.models import Webhook, WebhookDelivery
from .serializers import WebhookCustomerSerializer, WebhookDeliveryCustomerSerializer
from apps.webhooks.services import WebhookService


class WebhookCustomerViewSet(viewsets.ModelViewSet):
    """
    Customer webhook management endpoints.
    Provides CRUD operations for store-specific webhooks.
    """
    
    permission_classes = [IsAuthenticated, IsStoreUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description', 'url']
    ordering_fields = ['created_at', 'updated_at', 'name']
    ordering = ['-created_at']
    filterset_fields = ['is_active', 'method']
    
    def get_queryset(self):
        """Filter webhooks by current user's store"""
        return Webhook.objects.filter(store=self.request.store)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        return WebhookCustomerSerializer
    
    def perform_create(self, serializer):
        """Set store when creating webhook"""
        serializer.save(store=self.request.store)
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test webhook delivery"""
        webhook = self.get_object()
        result = WebhookService.test_webhook(webhook)
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def deliveries(self, request, pk=None):
        """Get webhook delivery history"""
        webhook = self.get_object()
        deliveries = webhook.deliveries.all().order_by('-created_at')
        serializer = WebhookDeliveryCustomerSerializer(deliveries, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get webhook status overview"""
        webhooks = self.get_queryset()
        active_count = webhooks.filter(is_active=True).count()
        total_count = webhooks.count()
        
        return Response({
            'total_webhooks': total_count,
            'active_webhooks': active_count,
            'inactive_webhooks': total_count - active_count
        })


class WebhookDeliveryCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer webhook delivery endpoints.
    Provides read-only access to webhook delivery history.
    """
    
    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = WebhookDeliveryCustomerSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['event_type', 'status']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    filterset_fields = ['status', 'webhook']
    
    def get_queryset(self):
        """Filter deliveries by current user's store"""
        return WebhookDelivery.objects.filter(webhook__store=self.request.store).select_related('webhook')
