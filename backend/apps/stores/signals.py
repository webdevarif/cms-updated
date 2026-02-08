"""
Signals for stores app.
"""

from apps.analytics.services.event_service import EventService

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Store, StoreSettings


@receiver(post_save, sender=Store)
def log_store_change(sender, instance, created, **kwargs):
    """Log store changes"""
    if created:
        event_type = "CONTENT_CREATE"
        message = f"Store created: {instance.name}"
    else:
        event_type = "CONTENT_UPDATE"
        message = f"Store updated: {instance.name}"

    EventService.log_event(
        event_type=event_type,
        event_name=message,
        properties={
            "entity_type": "Store",
            "entity_id": instance.id,
            "created": created,
        },
        store=instance,
    )


@receiver(post_delete, sender=Store)
def log_store_deletion(sender, instance, **kwargs):
    """Log store deletion"""
    EventService.log_event(
        event_type="CONTENT_DELETE",
        event_name=f"Store deleted: {instance.name}",
        properties={
            "entity_type": "Store",
            "entity_id": instance.id,
            "store_name": instance.name,
        },
        store=instance,
    )
