"""
API views for webhooks module.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.throttling import ScopedRateThrottle
from django.utils import timezone

from core.permissions import IsStoreOwner
from ..models import Webhook, WebhookDelivery
from .serializers import WebhookSerializer, WebhookDeliverySerializer


class WebhookThrottle(ScopedRateThrottle):
    """Custom throttle for webhook endpoints"""
    scope = 'webhook'


class WebhookDeliveryThrottle(ScopedRateThrottle):
    """Custom throttle for webhook delivery endpoints"""
    scope = 'webhook_delivery'


class WebhookViewSet(viewsets.ModelViewSet):
    """
    Webhook management endpoints
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = WebhookSerializer
    throttle_classes = [WebhookThrottle]
    
    def get_queryset(self):
        return Webhook.objects.filter(store=self.request.store)
    
    @extend_schema(
        summary="Test Webhook",
        description="Send test payload to webhook endpoint",
        responses={200: WebhookDeliverySerializer}
    )
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Send test event to webhook"""
        webhook = self.get_object()
        
        from ..services import WebhookService
        delivery = WebhookService.trigger_webhook(
            webhook=webhook,
            event_type='test',
            event_data={'test': True, 'timestamp': timezone.now().isoformat()},
            store=webhook.store
        )
        
        serializer = WebhookDeliverySerializer(delivery)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Regenerate Secret",
        description="Generate new webhook secret",
        responses={200: WebhookSerializer}
    )
    @action(detail=True, methods=['post'])
    def regenerate_secret(self, request, pk=None):
        """Regenerate webhook secret"""
        import secrets
        
        webhook = self.get_object()
        webhook.secret = secrets.token_urlsafe()
        webhook.save(update_fields=['secret'])
        
        serializer = self.get_serializer(webhook)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WebhookDeliveryViewSet(viewsets.ModelViewSet):
    """
    Webhook delivery tracking endpoints
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = WebhookDeliverySerializer
    throttle_classes = [WebhookDeliveryThrottle]
    
    def get_queryset(self):
        return WebhookDelivery.objects.filter(store=self.request.store)
    
    @extend_schema(
        summary="Retry Failed Delivery",
        description="Retry a failed webhook delivery",
        responses={200: WebhookDeliverySerializer}
    )
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed webhook delivery"""
        delivery = self.get_object()
        
        if delivery.status not in ['failed', 'retrying']:
            return Response(
                {'error': 'Only failed or retrying deliveries can be retried'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from ..services import WebhookService
        WebhookService.schedule_retry(delivery)
        
        serializer = self.get_serializer(delivery)
        return Response(serializer.data, status=status.HTTP_200_OK)
