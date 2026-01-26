"""
Dashboard test API.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.permissions import IsStoreOwner
from apps.webhooks.models import Webhook, WebhookDelivery
from .serializers import TestDashboardSerializer, TestResultsSummarySerializer, TestDeliveryDashboardSerializer
from apps.webhooks.services import WebhookService


class TestDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard test management endpoints for store owners and admins.
    """
    permission_classes = [IsStoreOwner]
    serializer_class = TestDashboardSerializer
    
    def get_queryset(self):
        """Filter by current user's stores"""
        return Webhook.objects.filter(store=self.request.store)
    
    @extend_schema(
        summary="Run Tests",
        description="Run test suite",
        responses={200: dict}
    )
    @action(detail=False, methods=['post'])
    def run_tests(self, request):
        """Run all tests for current store"""
        store = self.request.store
        
        # Get all test results for the store
        test_results = []
        
        # Test webhook functionality
        webhooks = Webhook.objects.filter(store=store)
        for webhook in webhooks:
            test_result = self._test_webhook(webhook)
            test_results.append(test_result)
        
        # Test webhook delivery functionality
        deliveries = WebhookDelivery.objects.filter(store=store).order_by('-triggered_at')[:10]
        for delivery in deliveries:
            test_result = self._test_webhook_delivery(delivery)
            test_results.append(test_result)
        
        return Response({
            'test_results': test_results,
            'total_tests': len(test_results),
            'passed': sum(1 for result in test_results if result.get('passed', False))
            'failed': sum(1 for result in test_results if not result.get('passed', False))
        })
    
    def _test_webhook(self, webhook):
        """Test individual webhook"""
        try:
            from apps.webhooks.services import WebhookService
            delivery = WebhookService.trigger_webhook(
                webhook=webhook,
                event_type='test',
                event_data={'test': True, 'timestamp': timezone.now().isoformat()},
                store=webhook.store
            )
            return {
                'webhook_id': webhook.id,
                'status': 'success',
                'message': 'Test webhook sent successfully'
            }
        except Exception as e:
            return {
                'webhook_id': webhook.id,
                'status': 'failed',
                'error': str(e)
            }
    
    def _test_webhook_delivery(self, delivery):
        """Test individual webhook delivery"""
        try:
            from apps.webhooks.services import WebhookService
            WebhookService.schedule_retry(delivery)
            return {
                'webhook_id': delivery.webhook.id,
                'status': 'retry_scheduled',
                'message': 'Retry scheduled'
            }
        except Exception as e:
            return {
                'webhook_id': delivery.webhook.id,
                'status': 'failed',
                'error': str(e)
            }


class TestDeliveryDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard test delivery tracking endpoints for store owners and admins.
    """
    permission_classes = [IsStoreOwner]
    serializer_class = TestDeliveryDashboardSerializer
    
    def get_queryset(self):
        """Filter by current user's store"""
        return WebhookDelivery.objects.filter(store=self.request.store).order_by('-triggered_at')
    
    @extend_schema(
        summary="Retry Failed Delivery",
        description="Retry a failed webhook delivery",
        responses={200: TestDeliveryDashboardSerializer}
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
        
        serializer = TestDeliveryDashboardSerializer(delivery)
        return Response(serializer.data, status=status.HTTP_200_OK)
