"""
Webhooks models.
"""

import secrets

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Webhook(models.Model):
    """
    Store-scoped webhook configuration for external integrations
    """

    # Store scoping
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE)

    # Core fields
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Endpoint configuration
    url = models.URLField(max_length=2048)
    method = models.CharField(
        max_length=10, choices=[("POST", "POST"), ("PUT", "PUT")], default="POST"
    )

    # Security
    secret = models.CharField(max_length=255, default=secrets.token_urlsafe)
    verify_ssl = models.BooleanField(default=True)

    # Event configuration
    event_types = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "webhooks"
        db_table = "webhooks_webhook"
        unique_together = [["store", "url"]]
        indexes = [
            models.Index(fields=["store", "is_active"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.url})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_active = None

        if not is_new:
            from core.services.webhook import WebhookService

            old_instance = WebhookService.get_webhook(pk=self.pk)
            old_active = old_instance.is_active

        super().save(*args, **kwargs)

        from apps.analytics.services.event_service import EventService

        if is_new:
            EventService.log_event(
                event_type="USER_ACTION",
                event_name=f"Webhook created: {self.name}",
                properties={
                    "entity_type": "Webhook",
                    "entity_id": self.id,
                    "name": self.name,
                    "url": self.url,
                    "method": self.method,
                    "events": self.event_types,
                    "is_active": self.is_active,
                },
                user=self.created_by,
                store=self.store,
            )
        elif old_active != self.is_active:
            EventService.log_event(
                event_type="USER_ACTION",
                event_name=f"Webhook status changed: {self.name} from {old_active} to {self.is_active}",
                properties={
                    "entity_type": "Webhook",
                    "entity_id": self.id,
                    "name": self.name,
                    "old_active": old_active,
                    "new_active": self.is_active,
                },
                user=self.created_by,
                store=self.store,
            )

    def generate_signature(self, payload):
        """Generate HMAC signature for payload"""
        import hashlib
        import hmac
        import json

        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self.secret.encode("utf-8"), payload_str.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        return f"sha256={signature}"

    def is_event_subscribed(self, event_type, event_data=None):
        """Check if webhook should be triggered for this event"""
        # Check if event type is in subscribed events
        if event_type not in self.events:
            return False

        # Apply advanced filtering if configured
        if self.event_filter:
            return self._apply_event_filter(event_type, event_data)

        return True

    def _apply_event_filter(self, event_type, event_data):
        """Apply advanced event filtering rules"""
        for key, value in self.event_filter.items():
            if key in event_data:
                if isinstance(value, list):
                    if event_data[key] not in value:
                        return False
                elif event_data[key] != value:
                    return False
        return True


class WebhookEvent(models.Model):
    """
    Represents an event that can trigger webhooks
    """

    # Store scoping
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE)

    event_type = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)

    CATEGORY_CHOICES = [
        ("content", "Content"),
        ("ecommerce", "Ecommerce"),
        ("user", "User"),
        ("system", "System"),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="system")

    # Event schema
    schema = models.JSONField(default=dict)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "webhooks"
        db_table = "webhooks_event"
        unique_together = [["store", "event_type"]]
        indexes = [
            models.Index(fields=["store", "category"]),
            models.Index(fields=["store", "event_type"]),
            models.Index(fields=["category", "event_type"]),
        ]
        ordering = ["store", "category", "event_type"]

    def __str__(self):
        return f"{self.event_type} ({self.category})"


class WebhookDelivery(models.Model):
    """
    Tracks individual webhook delivery attempts
    """

    # Store scoping
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE)

    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name="deliveries")

    # Event details
    event_type = models.CharField(max_length=100)
    event_id = models.CharField(max_length=100, blank=True)

    # Payload
    payload = models.JSONField(default=dict)

    # Delivery details
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("retrying", "Retrying"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Response details
    response_status = models.PositiveIntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    response_headers = models.JSONField(default=dict, blank=True)

    # Retry tracking
    attempt_number = models.PositiveSmallIntegerField(default=1)
    next_retry_at = models.DateTimeField(null=True, blank=True)

    # Timing
    triggered_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    # Error details
    error_message = models.TextField(blank=True)
    error_code = models.CharField(max_length=50, blank=True)

    class Meta:
        app_label = "webhooks"
        db_table = "webhooks_delivery"
        indexes = [
            models.Index(fields=["store", "webhook", "status"]),
            models.Index(fields=["store", "event_type"]),
            models.Index(fields=["store", "triggered_at"]),
            models.Index(fields=["store", "next_retry_at"]),
            models.Index(fields=["webhook", "status"]),
            models.Index(fields=["event_type"]),
            models.Index(fields=["triggered_at"]),
            models.Index(fields=["next_retry_at"]),
        ]
        ordering = ["-triggered_at"]

    def __str__(self):
        return f"Delivery #{self.id} - {self.event_type} ({self.status})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None

        if not is_new:
            from core.services.webhook import WebhookService

            old_instance = WebhookService.get_delivery(pk=self.pk)
            old_status = old_instance.status

        super().save(*args, **kwargs)

        from apps.analytics.services.event_service import EventService

        if is_new:
            EventService.log_event(
                event_type="USER_ACTION",
                event_name=f"Webhook delivery created: {self.webhook.name} - {self.event_type}",
                properties={
                    "entity_type": "WebhookDelivery",
                    "entity_id": self.id,
                    "webhook_name": self.webhook.name,
                    "event_type": self.event_type,
                    "event_id": self.event_id,
                    "status": self.status,
                    "attempt_number": self.attempt_number,
                },
                store=self.store,
            )
        elif old_status != self.status:
            EventService.log_event(
                event_type="USER_ACTION",
                event_name=f"Webhook delivery status changed: {self.webhook.name} - {self.event_type} from {old_status} to {self.status}",
                properties={
                    "entity_type": "WebhookDelivery",
                    "entity_id": self.id,
                    "webhook_name": self.webhook.name,
                    "event_type": self.event_type,
                    "event_id": self.event_id,
                    "old_status": old_status,
                    "new_status": self.status,
                },
                store=self.store,
            )
