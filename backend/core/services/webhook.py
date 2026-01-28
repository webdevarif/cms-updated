"""
Webhook management services for Digital Farmers CMS.

Shared webhook management service.
"""
import logging

from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class WebhookService:
    """Shared webhook management service"""

    @staticmethod
    def create_webhook(store, name, url, events=None, **extra_fields):
        """
        Centralized webhook creation method
        """
        from apps.webhooks.models import Webhook

        return Webhook.objects.create(
            store=store, name=name, url=url, events=events or [], **extra_fields
        )

    @staticmethod
    def get_webhook(webhook_id=None, **filters):
        """
        Centralized webhook retrieval method
        """
        from apps.webhooks.models import Webhook

        if webhook_id:
            return Webhook.objects.get(id=webhook_id, **filters)
        else:
            return Webhook.objects.get(**filters)

    @staticmethod
    def get_webhook_or_none(webhook_id=None, **filters):
        """
        Centralized webhook retrieval method (safe)
        """
        from apps.webhooks.models import Webhook

        if webhook_id:
            return Webhook.objects.filter(id=webhook_id, **filters).first()
        else:
            return Webhook.objects.filter(**filters).first()

    @staticmethod
    def create_delivery(webhook, store, event_type, **extra_fields):
        """
        Centralized webhook delivery creation method
        """
        from apps.webhooks.models import WebhookDelivery

        return WebhookDelivery.objects.create(
            webhook=webhook, store=store, event_type=event_type, **extra_fields
        )

    @staticmethod
    def get_delivery(delivery_id=None, **filters):
        """
        Centralized webhook delivery retrieval method
        """
        from apps.webhooks.models import WebhookDelivery

        if delivery_id:
            return WebhookDelivery.objects.get(id=delivery_id, **filters)
        else:
            return WebhookDelivery.objects.get(**filters)

    @staticmethod
    def get_delivery_or_none(delivery_id=None, **filters):
        """
        Centralized webhook delivery retrieval method (safe)
        """
        from apps.webhooks.models import WebhookDelivery

        if delivery_id:
            return WebhookDelivery.objects.filter(id=delivery_id, **filters).first()
        else:
            return WebhookDelivery.objects.filter(**filters).first()

    @staticmethod
    def filter_webhooks(store, **filters):
        """
        Centralized webhook filtering method
        """
        from apps.webhooks.models import Webhook

        return Webhook.objects.filter(store=store, **filters)

    @staticmethod
    def filter_deliveries(store, **filters):
        """
        Centralized webhook delivery filtering method
        """
        from apps.webhooks.models import WebhookDelivery

        return WebhookDelivery.objects.filter(store=store, **filters)
