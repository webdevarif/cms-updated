"""
Signals for entities app.
"""

from apps.analytics.services.event_service import EventService
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import EntityInteraction


@receiver(post_save, sender=EntityInteraction)
def log_entity_interaction_change(sender, instance, created, **kwargs):
    """
    Log entity interaction changes to EventService.

    Logs every created or updated entity interaction with metadata.
    """
    if created:
        event_type = "ENTITY_INTERACTION_CREATED"
        message = f"Entity interaction created: {instance.action.name}"
    else:
        event_type = "ENTITY_INTERACTION_UPDATED"
        message = f"Entity interaction updated: {instance.action.name}"

    EventService.log_event(
        event_type=event_type,
        event_name=message,
        properties={
            "entity_type": "EntityInteraction",
            "entity_id": instance.id,
            "action_slug": instance.action.slug,
            "content_type": instance.content_type.model,
            "object_id": instance.object_id,
        },
        user=instance.user,
        store=instance.store,
    )


@receiver(post_delete, sender=EntityInteraction)
def log_entity_interaction_deletion(sender, instance, **kwargs):
    """
    Log entity interaction deletions to EventService.

    Logs every deleted entity interaction with metadata.
    """
    EventService.log_event(
        event_type="ENTITY_INTERACTION_DELETED",
        event_name=f"Entity interaction deleted: {instance.action.name}",
        properties={
            "entity_type": "EntityInteraction",
            "entity_id": instance.id,
            "action_slug": instance.action.slug,
            "content_type": instance.content_type.model,
            "object_id": instance.object_id,
        },
        user=instance.user,
        store=instance.store,
    )
