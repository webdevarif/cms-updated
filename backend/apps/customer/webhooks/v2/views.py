"""
Customer webhooks API.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.utils import timezone
from datetime import timedelta
from rest_framework.throttling import ScopedRateThrottle

from core.permissions import IsStoreUser
from apps.webhooks.models import Webhook, WebhookDelivery
from .serializers import WebhookCustomerSerializer, WebhookDeliveryCustomerSerializer
from apps.webhooks.v2.services import WebhookService


class WebhookCustomerThrottle(ScopedRateThrottle):
    """Custom throttle for customer webhook endpoints"""
    scope = 'customer_webhook'


class WebhookCustomerViewSet(viewsets.ModelViewSet):
    """
    Customer webhook management endpoints for authenticated users.
    Users can list and register their own webhooks.
    """
    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = WebhookCustomerSerializer
    throttle_classes = [WebhookCustomerThrottle]
    
    def get_queryset(self):
        """Filter by current user's store"""
        return Webhook.objects.filter(store=self.request.store)
    
    @extend_schema(
        summary="Test Webhook",
        description="Send test payload to webhook endpoint",
        responses={200: WebhookDeliveryCustomerSerializer}
    )
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Send test event to webhook"""
        webhook = self.get_object()
        
        from apps.webhooks.services import WebhookService
        delivery = WebhookService.trigger_webhook(
            webhook=webhook,
            event_type='test',
            event_data={'test': True, 'user_id': request.user.id},
            store=webhook.store
        )
        
        serializer = WebhookDeliveryCustomerSerializer(delivery)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Get Delivery Logs",
        description="Get delivery logs for this webhook"
    )
    @action(detail=True, methods=['get'])
    def deliveries(self, request, pk=None):
        """Get delivery logs for webhook"""
        webhook = self.get_object()
        deliveries = WebhookDelivery.objects.filter(
            webhook=webhook,
            store=self.request.store
        ).order_by('-triggered_at')[:50]  # Limit to last 50
        
        serializer = WebhookDeliveryCustomerSerializer(deliveries, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Webhook Status",
        description="Get webhook status and health"
    )
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get webhook status"""
        webhook = self.get_object()
        
        # Get recent delivery stats
        recent_deliveries = WebhookDelivery.objects.filter(
            webhook=webhook,
            store=self.request.store,
            triggered_at__gte=timezone.now() - timedelta(days=7)
        )
        
        status_data = {
            'webhook_id': webhook.id,
            'name': webhook.name,
            'is_active': webhook.is_active,
            'last_triggered_at': webhook.last_triggered_at,
            'recent_deliveries': {
                'total': recent_deliveries.count(),
                'successful': recent_deliveries.filter(status='delivered').count(),
                'failed': recent_deliveries.filter(status='failed').count(),
                'pending': recent_deliveries.filter(status='pending').count()
            }
        }
        
        return Response(status_data)


class WebhookDeliveryCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer webhook delivery tracking endpoints for authenticated users.
    Users can view their own webhook delivery logs.
    """
    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = WebhookDeliveryCustomerSerializer
    
    def get_queryset(self):
        """Filter by current user's store"""
        return WebhookDelivery.objects.filter(store=self.request.store).order_by('-triggered_at')
