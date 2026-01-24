"""
Integration tests for webhook events.
"""
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch
from apps.stores.models import Store
from apps.webhooks.models import Webhook, WebhookDelivery
from apps.webhooks.signals import trigger_webhooks_for_event


class WebhookIntegrationTest(TestCase):
    def setUp(self):
        from core.services.store import StoreService
        
        self.store = StoreService.create_store(name='Test Store', slug='test-store')
        from core.services.webhook import WebhookService
        
        self.webhook = WebhookService.create_webhook(
            store=self.store,
            name='Test Webhook',
            url='https://example.com/webhook',
            events=['order.created', 'product.created', 'post.created']
        )
    
    @patch('apps.webhooks.services.deliver_webhook')
    def test_order_created_webhook(self, mock_deliver):
        """Test webhook triggered on order creation"""
        event_data = {
            'id': '123',
            'order_number': 'ORD-001',
            'status': 'created',
            'total': 99.99,
            'customer_email': 'test@example.com'
        }
        
        trigger_webhooks_for_event(self.store, 'order.created', event_data)
        
        # Check delivery was created
        from core.services.webhook import WebhookService
        
        delivery = WebhookService.get_delivery(
            webhook=self.webhook,
            event_type='order.created'
        )
        self.assertEqual(delivery.status, 'pending')
        self.assertEqual(delivery.payload, event_data)
        
        # Check async task was called
        mock_deliver.delay.assert_called_once_with(delivery.id)
    
    @patch('apps.webhooks.services.deliver_webhook')
    def test_product_created_webhook(self, mock_deliver):
        """Test webhook triggered on product creation"""
        event_data = {
            'id': '456',
            'title': 'Test Product',
            'price': 29.99,
            'sku': 'PROD-001'
        }
        
        trigger_webhooks_for_event(self.store, 'product.created', event_data)
        
        # Check delivery was created
        delivery = WebhookDelivery.objects.get(
            webhook=self.webhook,
            event_type='product.created'
        )
        self.assertEqual(delivery.status, 'pending')
        self.assertEqual(delivery.payload, event_data)
        
        # Check async task was called
        mock_deliver.delay.assert_called_once_with(delivery.id)
    
    @patch('apps.webhooks.services.deliver_webhook')
    def test_post_created_webhook(self, mock_deliver):
        """Test webhook triggered on post creation"""
        event_data = {
            'id': '789',
            'title': 'Test Post',
            'content': 'Test content',
            'status': 'published'
        }
        
        trigger_webhooks_for_event(self.store, 'post.created', event_data)
        
        # Check delivery was created
        delivery = WebhookDelivery.objects.get(
            webhook=self.webhook,
            event_type='post.created'
        )
        self.assertEqual(delivery.status, 'pending')
        self.assertEqual(delivery.payload, event_data)
        
        # Check async task was called
        mock_deliver.delay.assert_called_once_with(delivery.id)
    
    def test_webhook_not_triggered_for_unsubscribed_event(self):
        """Test webhook not triggered for unsubscribed event"""
        event_data = {'id': '123'}
        
        trigger_webhooks_for_event(self.store, 'user.created', event_data)
        
        # Check no delivery was created
        self.assertFalse(
            WebhookDelivery.objects.filter(
                webhook=self.webhook,
                event_type='user.created'
            ).exists()
        )
    
    def test_webhook_not_triggered_for_inactive_webhook(self):
        """Test webhook not triggered when inactive"""
        self.webhook.is_active = False
        self.webhook.save()
        
        event_data = {'id': '123'}
        
        trigger_webhooks_for_event(self.store, 'order.created', event_data)
        
        # Check no delivery was created
        self.assertFalse(
            WebhookDelivery.objects.filter(
                webhook=self.webhook,
                event_type='order.created'
            ).exists()
        )
    
    def test_multiple_webhooks_triggered(self):
        """Test multiple webhooks triggered for same event"""
        # Create second webhook
        from core.services.webhook import WebhookService
        
        webhook2 = WebhookService.create_webhook(
            store=self.store,
            name='Second Webhook',
            url='https://example.com/webhook2',
            events=['order.created']
        )
        
        event_data = {'id': '123'}
        
        trigger_webhooks_for_event(self.store, 'order.created', event_data)
        
        # Check deliveries were created for both webhooks
        deliveries = WebhookDelivery.objects.filter(
            event_type='order.created'
        )
        self.assertEqual(deliveries.count(), 2)
        
        webhook_ids = {d.webhook_id for d in deliveries}
        self.assertIn(self.webhook.id, webhook_ids)
        self.assertIn(webhook2.id, webhook_ids)
    
    def test_webhook_event_filtering(self):
        """Test webhook event filtering"""
        self.webhook.event_filter = {
            'status': ['completed', 'refunded']
        }
        self.webhook.save()
        
        # Matching event
        event_data = {'status': 'completed'}
        trigger_webhooks_for_event(self.store, 'order.created', event_data)
        
        self.assertTrue(
            WebhookDelivery.objects.filter(
                webhook=self.webhook,
                event_type='order.created'
            ).exists()
        )
        
        # Non-matching event
        WebhookDelivery.objects.all().delete()
        event_data = {'status': 'pending'}
        trigger_webhooks_for_event(self.store, 'order.created', event_data)
        
        self.assertFalse(
            WebhookDelivery.objects.filter(
                webhook=self.webhook,
                event_type='order.created'
            ).exists()
        )
