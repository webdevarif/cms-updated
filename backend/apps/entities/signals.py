"""
Signals for entities app.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import EntityInteraction
from apps.logs.tasks import log_event_async


@receiver(post_save, sender=EntityInteraction)
def log_entity_interaction_change(sender, instance, created, **kwargs):
    """Log entity interaction changes"""
    if created:
        event_type = 'ENTITY_INTERACTION_CREATED'
        message = f"Entity interaction created: {instance.action.name}"
    else:
        event_type = 'ENTITY_INTERACTION_UPDATED'
        message = f"Entity interaction updated: {instance.action.name}"
    
    log_event_async.delay({
        'event_type': event_type,
        'message': message,
        'store': instance.store,
        'user': instance.user,
        'entity_type': 'EntityInteraction',
        'entity_id': instance.id,
        'metadata': {
            'action_slug': instance.action.slug,
            'content_type': instance.content_type.model,
            'object_id': instance.object_id
        }
    })
