"""
Admin configuration for webhooks module.
"""
from django.contrib import admin

from .models import Webhook, WebhookDelivery, WebhookEvent


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    """Admin for Webhook"""

    list_display = ["name", "url", "is_active", "created_at", "updated_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "url"]


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    """Admin for WebhookEvent"""

    list_display = ["event_type", "category"]
    list_filter = ["category"]


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    """Admin for WebhookDelivery"""

    list_display = ["webhook", "event_type", "status", "attempt_number"]
    list_filter = ["status", "event_type"]
    readonly_fields = ["triggered_at", "delivered_at", "duration_ms"]
