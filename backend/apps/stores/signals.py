"""
Signals for stores app.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Store, StoreSettings
from apps.logs.tasks import log_event_async


@receiver(post_save, sender=Store)
def log_store_change(sender, instance, created, **kwargs):
    """Log store changes"""
    if created:
        event_type = 'CONTENT_CREATE'
        message = f"Store created: {instance.name}"
    else:
        event_type = 'CONTENT_UPDATE'
        message = f"Store updated: {instance.name}"
    
    log_event_async.delay({
        'event_type': event_type,
        'message': message,
        'store': instance,
        'entity_type': 'Store',
        'entity_id': instance.id,
        'metadata': {'created': created}
    })


@receiver(post_delete, sender=Store)
def log_store_deletion(sender, instance, **kwargs):
    """Log store deletion"""
    log_event_async.delay({
        'event_type': 'CONTENT_DELETE',
        'message': f"Store deleted: {instance.name}",
        'entity_type': 'Store',
        'entity_id': instance.id,
        'metadata': {'store_name': instance.name}
    })
