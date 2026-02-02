"""
Signals for notifications app.
"""

from apps.analytics.services.event_service import EventService
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification


@receiver(post_save, sender=Notification)
def log_notification_change(sender, instance, created, **kwargs):
    """Log notification changes"""
    if created:
        event_type = "NOTIFICATION_CREATED"
        message = f"Notification created: {instance.title}"
    else:
        event_type = "NOTIFICATION_UPDATED"
        message = f"Notification updated: {instance.title}"

    EventService.log_event(
        event_type=event_type,
        event_name=message,
        properties={
            "user": instance.user.id if instance.user else None,
            "store": instance.store.id if instance.store else None,
            "entity_type": "Notification",
            "entity_id": instance.id,
            "notification_type": instance.notification_type,
            "status": instance.status,
        },
        user=instance.user,
        store=instance.store,
    )
