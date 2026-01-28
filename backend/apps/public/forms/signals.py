"""
Signals for forms module.
"""
from apps.forms.models import FormTemplate
from apps.logs.tasks import log_event_async
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=FormTemplate)
def form_created_signal(sender, instance, created, **kwargs):
    """Handle form creation signal"""
    if created:
        log_event_async.delay(
            {
                "event_type": "FORM_CREATED",
                "message": f"Form created: {instance.title}",
                "store": instance.store,
                "entity_type": "FormTemplate",
                "entity_id": instance.id,
                "metadata": {
                    "form_id": instance.form_id,
                    "title": instance.title,
                    "status": instance.status,
                },
            }
        )


@receiver(post_save, sender=FormTemplate)
def form_updated_signal(sender, instance, **kwargs):
    """Handle form update signal"""
    if not kwargs.get("created"):
        log_event_async.delay(
            {
                "event_type": "FORM_UPDATED",
                "message": f"Form updated: {instance.title}",
                "store": instance.store,
                "entity_type": "FormTemplate",
                "entity_id": instance.id,
                "metadata": {
                    "form_id": instance.form_id,
                    "title": instance.title,
                    "status": instance.status,
                },
            }
        )
