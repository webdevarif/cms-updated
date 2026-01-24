"""
Signals for notifications app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from apps.logs.tasks import log_event_async


@receiver(post_save, sender=Notification)
def log_notification_change(sender, instance, created, **kwargs):
    """Log notification changes"""
    if created:
        event_type = 'NOTIFICATION_CREATED'
        message = f"Notification created: {instance.title}"
    else:
        event_type = 'NOTIFICATION_UPDATED'
        message = f"Notification updated: {instance.title}"
    
    log_event_async.delay({
        'event_type': event_type,
        'message': message,
        'store': instance.store,
        'user': instance.user,
        'entity_type': 'Notification',
        'entity_id': instance.id,
        'metadata': {
            'notification_type': instance.notification_type,
            'status': instance.status
        }
    })
