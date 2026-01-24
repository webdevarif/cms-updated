"""
Signals for automatic model change logging.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .tasks import log_event_async


@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    """Log model save events"""
    # Skip logging models and system models
    if sender._meta.app_label in ['logs', 'sessions', 'admin', 'contenttypes']:
        return
    
    event_type = 'CONTENT_CREATE' if created else 'CONTENT_UPDATE'
    
    log_data = {
        'event_type': event_type,
        'level': 'INFO',
        'message': f"{'Created' if created else 'Updated'} {sender.__name__} #{instance.pk}",
        'entity_type': sender.__name__,
        'entity_id': instance.pk,
        'metadata': {
            'created': created,
            'changed_fields': getattr(instance, '_changed_fields', {}),
        }
    }
    
    # Add store if model has it
    if hasattr(instance, 'store'):
        log_data['store'] = instance.store
    
    log_event_async.delay(log_data)


@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    """Log model delete events"""
    if sender._meta.app_label in ['logs', 'sessions', 'admin', 'contenttypes']:
        return
    
    log_data = {
        'event_type': 'CONTENT_DELETE',
        'level': 'WARNING',
        'message': f"Deleted {sender.__name__} #{instance.pk}",
        'entity_type': sender.__name__,
        'entity_id': instance.pk,
        'metadata': {}
    }
    
    if hasattr(instance, 'store'):
        log_data['store'] = instance.store
    
    log_event_async.delay(log_data)
