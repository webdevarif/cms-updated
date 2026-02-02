"""
Signals for webhooks module.
"""

import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from .services import WebhookService

logger = logging.getLogger(__name__)


def trigger_webhooks_for_event(store, event_type, event_data):
    """
    Helper function to trigger webhooks for a specific event
    """
    try:
        from .models import Webhook

        webhooks = Webhook.objects.filter(store=store, is_active=True)

        for webhook in webhooks:
            WebhookService.trigger_webhook(
                webhook=webhook,
                event_type=event_type,
                event_data=event_data,
                store=store,
            )

    except Exception as exc:
        logger.error(f"Failed to trigger webhook for {event_type}: {exc}")


@receiver(post_save, sender="ecommerce.Order")
def trigger_order_webhooks(sender, instance, created, **kwargs):
    """Trigger webhooks on order creation/update"""
    if created:
        event_type = "order.created"
    else:
        event_type = "order.updated"

    event_data = {
        "id": str(instance.id),
        "order_number": instance.order_number,
        "status": instance.status,
        "total": float(instance.total) if instance.total else None,
        "subtotal": (
            float(instance.subtotal)
            if hasattr(instance, "subtotal") and instance.subtotal
            else None
        ),
        "tax": (float(instance.tax) if hasattr(instance, "tax") and instance.tax else None),
        "shipping": (
            float(instance.shipping)
            if hasattr(instance, "shipping") and instance.shipping
            else None
        ),
        "currency": getattr(instance, "currency", "USD"),
        "customer_email": getattr(instance, "customer_email", ""),
        "created_at": (
            instance.created_at.isoformat() if hasattr(instance, "created_at") else None
        ),
        "updated_at": (
            instance.updated_at.isoformat() if hasattr(instance, "updated_at") else None
        ),
    }

    trigger_webhooks_for_event(instance.store, event_type, event_data)


@receiver(post_save, sender="ecommerce.Product")
def trigger_product_webhooks(sender, instance, created, **kwargs):
    """Trigger webhooks on product creation/update"""
    if created:
        event_type = "product.created"
    else:
        event_type = "product.updated"

    event_data = {
        "id": str(instance.id),
        "title": getattr(instance, "title", ""),
        "description": getattr(instance, "description", ""),
        "price": (float(instance.price) if hasattr(instance, "price") and instance.price else None),
        "compare_at_price": (
            float(instance.compare_at_price)
            if hasattr(instance, "compare_at_price") and instance.compare_at_price
            else None
        ),
        "sku": getattr(instance, "sku", ""),
        "barcode": getattr(instance, "barcode", ""),
        "track_inventory": getattr(instance, "track_inventory", False),
        "inventory_quantity": getattr(instance, "inventory_quantity", 0),
        "weight": (
            float(instance.weight) if hasattr(instance, "weight") and instance.weight else None
        ),
        "status": getattr(instance, "status", "active"),
        "created_at": (
            instance.created_at.isoformat() if hasattr(instance, "created_at") else None
        ),
        "updated_at": (
            instance.updated_at.isoformat() if hasattr(instance, "updated_at") else None
        ),
    }

    trigger_webhooks_for_event(instance.store, event_type, event_data)


@receiver(post_delete, sender="ecommerce.Product")
def trigger_product_deleted_webhooks(sender, instance, **kwargs):
    """Trigger webhooks on product deletion"""
    event_type = "product.deleted"

    event_data = {
        "id": str(instance.id),
        "title": getattr(instance, "title", ""),
        "sku": getattr(instance, "sku", ""),
        "deleted_at": timezone.now().isoformat(),
    }

    trigger_webhooks_for_event(instance.store, event_type, event_data)


@receiver(post_save, sender="posts.Post")
def trigger_post_webhooks(sender, instance, created, **kwargs):
    """Trigger webhooks on post creation/update"""
    if created:
        event_type = "post.created"
    else:
        event_type = "post.updated"

    event_data = {
        "id": str(instance.id),
        "title": getattr(instance, "title", ""),
        "content": getattr(instance, "content", ""),
        "excerpt": getattr(instance, "excerpt", ""),
        "slug": getattr(instance, "slug", ""),
        "status": getattr(instance, "status", "draft"),
        "author": (
            getattr(instance.author, "email", "")
            if hasattr(instance, "author") and instance.author
            else ""
        ),
        "published_at": (
            instance.published_at.isoformat()
            if hasattr(instance, "published_at") and instance.published_at
            else None
        ),
        "created_at": (
            instance.created_at.isoformat() if hasattr(instance, "created_at") else None
        ),
        "updated_at": (
            instance.updated_at.isoformat() if hasattr(instance, "updated_at") else None
        ),
    }

    trigger_webhooks_for_event(instance.store, event_type, event_data)


@receiver(post_save, sender="posts.Post")
def trigger_post_published_webhooks(sender, instance, **kwargs):
    """Trigger webhooks when post is published"""
    # Check if this is a publish event (status changed to published)
    if hasattr(instance, "status") and instance.status == "published":
        # Only trigger if it wasn't published before
        try:
            from core.services.webhook import WebhookService

            old_instance = WebhookService.get_webhook(pk=instance.pk)
            if old_instance.status != "published":
                event_type = "post.published"

                event_data = {
                    "id": str(instance.id),
                    "title": getattr(instance, "title", ""),
                    "slug": getattr(instance, "slug", ""),
                    "author": (
                        getattr(instance.author, "email", "")
                        if hasattr(instance, "author") and instance.author
                        else ""
                    ),
                    "published_at": (
                        instance.published_at.isoformat()
                        if hasattr(instance, "published_at") and instance.published_at
                        else timezone.now().isoformat()
                    ),
                }

                trigger_webhooks_for_event(instance.store, event_type, event_data)
        except sender.DoesNotExist:
            pass  # New post, handled by create event


@receiver(post_delete, sender="posts.Post")
def trigger_post_deleted_webhooks(sender, instance, **kwargs):
    """Trigger webhooks on post deletion"""
    event_type = "post.deleted"

    event_data = {
        "id": str(instance.id),
        "title": getattr(instance, "title", ""),
        "slug": getattr(instance, "slug", ""),
        "deleted_at": timezone.now().isoformat(),
    }

    trigger_webhooks_for_event(instance.store, event_type, event_data)


@receiver(post_save, sender="forms.FormSubmission")
def trigger_form_submission_webhooks(sender, instance, created, **kwargs):
    """Trigger webhooks on form submission"""
    if created:
        event_type = "form.submitted"

        event_data = {
            "id": str(instance.id),
            "form_name": (
                getattr(instance.form, "name", "")
                if hasattr(instance, "form") and instance.form
                else ""
            ),
            "form_id": (
                str(instance.form.id) if hasattr(instance, "form") and instance.form else ""
            ),
            "submitted_at": (
                instance.created_at.isoformat()
                if hasattr(instance, "created_at")
                else timezone.now().isoformat()
            ),
            "data": getattr(instance, "data", {}),
            "ip_address": getattr(instance, "ip_address", ""),
            "user_agent": getattr(instance, "user_agent", ""),
        }

        trigger_webhooks_for_event(instance.store, event_type, event_data)


@receiver(post_save, sender="accounts.User")
def trigger_user_webhooks(sender, instance, created, **kwargs):
    """Trigger webhooks on user creation/update"""
    if created:
        event_type = "user.created"
    else:
        event_type = "user.updated"

    event_data = {
        "id": str(instance.id),
        "email": getattr(instance, "email", ""),
        "first_name": getattr(instance, "first_name", ""),
        "last_name": getattr(instance, "last_name", ""),
        "is_active": getattr(instance, "is_active", True),
        "date_joined": (
            instance.date_joined.isoformat() if hasattr(instance, "date_joined") else None
        ),
        "last_login": (
            instance.last_login.isoformat()
            if hasattr(instance, "last_login") and instance.last_login
            else None
        ),
    }

    # For user events, trigger on all stores (global event)
    try:
        from apps.stores.models import Store

        from .models import Webhook

        stores = Store.objects.all()
        for store in stores:
            trigger_webhooks_for_event(store, event_type, event_data)

    except Exception as exc:
        logger.error(f"Failed to trigger user webhook for {event_type}: {exc}")


@receiver(post_save, sender="notifications.Notification")
def trigger_notification_webhooks(sender, instance, created, **kwargs):
    """Trigger webhooks on notification creation"""
    if created:
        event_type = "notification.created"

        event_data = {
            "id": str(instance.id),
            "title": getattr(instance, "title", ""),
            "message": getattr(instance, "message", ""),
            "type": getattr(instance, "type", "info"),
            "recipient_email": (
                getattr(instance.recipient, "email", "")
                if hasattr(instance, "recipient") and instance.recipient
                else ""
            ),
            "created_at": (
                instance.created_at.isoformat()
                if hasattr(instance, "created_at")
                else timezone.now().isoformat()
            ),
        }

        # Get store from notification or recipient
        store = getattr(instance, "store", None)
        if not store and hasattr(instance, "recipient") and instance.recipient:
            store = getattr(instance.recipient, "store", None)

        if store:
            trigger_webhooks_for_event(store, event_type, event_data)
