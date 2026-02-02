"""
Tests for webhook services.
"""

import json
from unittest.mock import MagicMock, patch

import requests
from apps.stores.models import Store
from apps.webhooks.models import Webhook, WebhookDelivery
from apps.webhooks.services import WebhookService
from django.test import TestCase
from django.utils import timezone


class WebhookServiceTest(TestCase):
    def setUp(self):
        from core.services.store import StoreService

        self.store = StoreService.create_store(name="Test Store", slug="test-store")
        from core.services.webhook import WebhookService

        self.webhook = WebhookService.create_webhook(
            store=self.store,
            name="Test Webhook",
            url="https://example.com/webhook",
            events=["order.created"],
        )

    def test_trigger_webhook_success(self):
        """Test successful webhook triggering"""
        event_data = {
            "id": "123",
            "order_number": "ORD-001",
            "status": "created",
            "total": 99.99,
        }

        delivery = WebhookService.trigger_webhook(
            webhook=self.webhook,
            event_type="order.created",
            event_data=event_data,
            store=self.store,
        )

        self.assertIsNotNone(delivery)
        self.assertEqual(delivery.event_type, "order.created")
        self.assertEqual(delivery.status, "pending")
        self.assertEqual(delivery.store, self.store)
        self.assertEqual(delivery.payload, event_data)

    def test_trigger_webhook_not_subscribed(self):
        """Test webhook not triggered for unsubscribed event"""
        event_data = {"id": "123"}

        delivery = WebhookService.trigger_webhook(
            webhook=self.webhook,
            event_type="product.created",  # Not in webhook.events
            event_data=event_data,
            store=self.store,
        )

        self.assertIsNone(delivery)

    def test_generate_signature(self):
        """Test signature generation"""
        payload = {"test": "data"}
        signature = self.webhook.generate_signature(payload)

        self.assertTrue(signature.startswith("sha256="))
        self.assertEqual(len(signature), 71)  # sha256= + 64 char hex

    def test_is_event_subscribed(self):
        """Test event subscription checking"""
        # Subscribed event
        self.assertTrue(self.webhook.is_event_subscribed("order.created"))

        # Not subscribed event
        self.assertFalse(self.webhook.is_event_subscribed("product.created"))

    def test_is_event_subscribed_with_filter(self):
        """Test event subscription with filtering"""
        self.webhook.event_filter = {"status": ["completed", "refunded"]}
        self.webhook.save()

        # Matching filter
        event_data = {"status": "completed"}
        self.assertTrue(self.webhook.is_event_subscribed("order.created", event_data))

        # Non-matching filter
        event_data = {"status": "pending"}
        self.assertFalse(self.webhook.is_event_subscribed("order.created", event_data))

    @patch("apps.webhooks.services.requests.request")
    def test_deliver_webhook_sync_success(self, mock_request):
        """Test successful synchronous webhook delivery"""
        # Create delivery
        from core.services.webhook import WebhookService

        delivery = WebhookService.create_delivery(
            webhook=self.webhook,
            store=self.store,
            event_type="order.created",
            event_id="123",
            payload={"test": "data"},
            status="pending",
        )

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = WebhookService.deliver_webhook_sync(delivery)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.response_status, 200)
        self.assertIsNotNone(result.delivered_at)
        self.assertIsNotNone(result.duration_ms)

    @patch("apps.webhooks.services.requests.request")
    def test_deliver_webhook_sync_failure(self, mock_request):
        """Test failed webhook delivery"""
        # Create delivery
        from core.services.webhook import WebhookService

        delivery = WebhookService.create_delivery(
            webhook=self.webhook,
            store=self.store,
            event_type="order.created",
            event_id="123",
            payload={"test": "data"},
            status="pending",
        )

        # Mock failed response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.headers = {}
        mock_request.return_value = mock_response

        result = WebhookService.deliver_webhook_sync(delivery)

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.response_status, 500)
        self.assertEqual(result.error_message, "HTTP 500")

    @patch("apps.webhooks.services.requests.request")
    def test_deliver_webhook_sync_timeout(self, mock_request):
        """Test webhook delivery timeout"""
        # Create delivery
        from core.services.webhook import WebhookService

        delivery = WebhookService.create_delivery(
            webhook=self.webhook,
            store=self.store,
            event_type="order.created",
            event_id="123",
            payload={"test": "data"},
            status="pending",
        )

        # Mock timeout
        mock_request.side_effect = requests.exceptions.Timeout()

        result = WebhookService.deliver_webhook_sync(delivery)

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.error_code, "TIMEOUT")

    def test_schedule_retry(self):
        """Test retry scheduling"""
        from core.services.webhook import WebhookService

        delivery = WebhookService.create_delivery(
            webhook=self.webhook,
            store=self.store,
            event_type="order.created",
            event_id="123",
            payload={"test": "data"},
            status="failed",
            attempt_number=1,
        )

        with patch("apps.webhooks.services.deliver_webhook") as mock_task:
            WebhookService.schedule_retry(delivery)

            # Check delivery was updated
            delivery.refresh_from_db()
            self.assertEqual(delivery.status, "retrying")
            self.assertEqual(delivery.attempt_number, 2)
            self.assertIsNotNone(delivery.next_retry_at)

            # Check task was scheduled
            mock_task.apply_async.assert_called_once()
            args, kwargs = mock_task.apply_async.call_args
            self.assertEqual(args[0], [delivery.id])
            self.assertEqual(kwargs["eta"], delivery.next_retry_at)
