"""
Dashboard webhooks API.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.throttling import ScopedRateThrottle
from django.utils import timezone

from core.permissions import IsStoreOwner
from apps.webhooks.models import Webhook, WebhookDelivery
from .serializers import WebhookDashboardSerializer, WebhookDeliveryDashboardSerializer


class WebhookThrottle(ScopedRateThrottle):
    """Custom throttle for webhook endpoints"""
    scope = 'webhook'


class WebhookDeliveryThrottle(ScopedRateThrottle):
    """Custom throttle for webhook delivery endpoints"""
    scope = 'webhook_delivery'


class WebhookDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard webhook management endpoints for store owners and admins.
    Provides full CRUD access to webhooks with management actions.
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = WebhookDashboardSerializer
    throttle_classes = [WebhookThrottle]
    
    def get_queryset(self):
        return Webhook.objects.filter(store=self.request.store)
    
    @extend_schema(
        summary="Test Webhook",
        description="Send test payload to webhook endpoint",
        responses={200: WebhookDeliveryDashboardSerializer}
    )
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Send test event to webhook"""
        webhook = self.get_object()
        
        from apps.webhooks.services import WebhookService
        delivery = WebhookService.trigger_webhook(
            webhook=webhook,
            event_type='test',
            event_data={'test': True, 'timestamp': timezone.now().isoformat()},
            store=webhook.store
        )
        
        serializer = WebhookDeliveryDashboardSerializer(delivery)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Regenerate Secret",
        description="Generate new webhook secret",
        responses={200: WebhookDashboardSerializer}
    )
    @action(detail=True, methods=['post'])
    def regenerate_secret(self, request, pk=None):
        """Regenerate webhook secret"""
        import secrets
        
        webhook = self.get_object()
        webhook.secret = secrets.token_urlsafe()
        webhook.save(update_fields=['secret'])
        
        serializer = WebhookDashboardSerializer(webhook)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Toggle Active Status",
        description="Enable or disable webhook"
    )
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle webhook active status"""
        webhook = self.get_object()
        webhook.is_active = not webhook.is_active
        webhook.save(update_fields=['is_active'])
        
        return Response({
            'status': 'toggled',
            'is_active': webhook.is_active,
            'message': f'Webhook {webhook.name} is now {"active" if webhook.is_active else "inactive"}'
        })
    
    @extend_schema(
        summary="Webhook Analytics",
        description="Get webhook delivery analytics"
    )
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get webhook analytics"""
        webhook = self.get_object()
        days = int(request.GET.get('days', 30))
        
        from apps.webhooks.services import WebhookService
        analytics = WebhookService.get_webhook_analytics(webhook, days)
        return Response(analytics)


class WebhookDeliveryDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard webhook delivery tracking endpoints for store owners and admins.
    Provides access to delivery logs and retry functionality.
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = WebhookDeliveryDashboardSerializer
    throttle_classes = [WebhookDeliveryThrottle]
    
    def get_queryset(self):
        return WebhookDelivery.objects.filter(store=self.request.store)
    
    @extend_schema(
        summary="Retry Failed Delivery",
        description="Retry a failed webhook delivery",
        responses={200: WebhookDeliveryDashboardSerializer}
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
        
        from apps.webhooks.services import WebhookService
        WebhookService.schedule_retry(delivery)
        
        serializer = WebhookDeliveryDashboardSerializer(delivery)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Bulk Retry Failed",
        description="Retry multiple failed deliveries"
    )
    @action(detail=False, methods=['post'])
    def bulk_retry(self, request):
        """Bulk retry failed deliveries"""
        delivery_ids = request.data.get('delivery_ids', [])
        if not isinstance(delivery_ids, list):
            return Response(
                {'error': 'delivery_ids must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        store = self.request.store
        from apps.webhooks.services import WebhookService
        
        retried_count = 0
        for delivery_id in delivery_ids:
            try:
                delivery = WebhookDelivery.objects.get(id=delivery_id, store=store)
                if delivery.status in ['failed', 'retrying']:
                    WebhookService.schedule_retry(delivery)
                    retried_count += 1
            except WebhookDelivery.DoesNotExist:
                continue
        
        return Response({
            'retried_count': retried_count,
            'total_count': len(delivery_ids)
        })
