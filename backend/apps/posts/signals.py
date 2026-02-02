"""
Signals for posts app.
"""

from apps.analytics.services.event_service import EventService
from apps.notifications.services import NotificationService
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Post, Taxonomy, Term

# from apps.translations.services import TranslationService


@receiver(post_save, sender=Post)
def create_post_translation_keys(sender, instance, created, **kwargs):
    """Create translation keys for post fields"""
    if created:
        # Create translation keys for translatable fields
        fields_to_translate = ["title", "content", "excerpt"]

        for field in fields_to_translate:
            field_value = getattr(instance, field)
            if field_value:
                key = f"posts.{field}.{instance.id}"
                TranslationService.get_or_create_translation_key(
                    key=key,
                    namespace="posts",
                    content_type="html" if field in ["content"] else "plain",
                    description=f"Post {field.replace('_', ' ').title()} for post: {instance.title}",
                )


@receiver(post_save, sender=Post)
def log_post_change(sender, instance, created, **kwargs):
    """Log post changes"""
    if created:
        event_type = "POST_CREATED"
        message = f"Post created: {instance.title}"
    else:
        event_type = "POST_UPDATED"
        message = f"Post updated: {instance.title}"

    EventService.log_event(
        event_type=event_type,
        event_name=message,
        properties={
            "entity_type": "Post",
            "entity_id": instance.id,
            "post_type": instance.post_type.slug,
            "status": instance.status,
        },
        user=instance.author,
        store=instance.store,
    )


@receiver(post_delete, sender=Post)
def log_post_deletion(sender, instance, **kwargs):
    """Log post deletion"""
    EventService.log_event(
        event_type="POST_DELETED",
        event_name=f"Post deleted: {instance.title}",
        properties={
            "entity_type": "Post",
            "entity_id": instance.id,
            "post_title": instance.title,
        },
        store=instance.store,
    )


@receiver(post_save, sender=Taxonomy)
def log_taxonomy_change(sender, instance, created, **kwargs):
    """Log taxonomy changes"""
    if created:
        event_type = "TAXONOMY_CREATED"
        message = f"Taxonomy created: {instance.name}"
    else:
        event_type = "TAXONOMY_UPDATED"
        message = f"Taxonomy updated: {instance.name}"

    EventService.log_event(
        event_type=event_type,
        event_name=message,
        properties={
            "entity_type": "Taxonomy",
            "entity_id": instance.id,
            "taxonomy_type": instance.taxonomy_type,
        },
        store=instance.store,
    )


@receiver(post_save, sender=Term)
def log_term_change(sender, instance, created, **kwargs):
    """Log term changes"""
    if created:
        event_type = "TERM_CREATED"
        message = f"Term created: {instance.name}"
    else:
        event_type = "TERM_UPDATED"
        message = f"Term updated: {instance.name}"

    EventService.log_event(
        event_type=event_type,
        event_name=message,
        properties={
            "entity_type": "Term",
            "entity_id": instance.id,
            "taxonomy": instance.taxonomy.name,
        },
        store=instance.store,
    )


@receiver(post_save, sender=Post)
def notify_post_published(sender, instance, created, **kwargs):
    """Send notification when post is published"""
    # Only notify when status changes to published
    if not created and instance.status == "published":
        NotificationService.notify_user(
            user=instance.author,
            notification_type="post.published",
            context={
                "title": f"Post Published: {instance.title}",
                "message": f'Your post "{instance.title}" has been published',
                "post_id": instance.id,
                "post_type": instance.post_type.slug,
                "published_at": (
                    instance.published_at.isoformat() if instance.published_at else None
                ),
            },
            store=instance.store,
        )
