"""
Signals for media app.
"""

from apps.analytics.services.event_service import EventService

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models.media_file import MediaFile
from .models.media_folder import MediaFolder


@receiver(post_save, sender=MediaFile)
def log_media_file_change(sender, instance, created, **kwargs):
    """Log media file changes"""
    if created:
        event_type = "MEDIA_UPLOAD"
        message = f"Media file uploaded: {instance.original_filename}"
    else:
        event_type = "MEDIA_UPDATE"
        message = f"Media file updated: {instance.original_filename}"

    EventService.log_event(
        event_type=event_type,
        event_name=message,
        properties={
            "entity_type": "MediaFile",
            "entity_id": instance.id,
            "file_size": instance.file_size,
            "mime_type": instance.mime_type,
            "resource_type": instance.resource_type,
        },
        user=instance.uploaded_by,
        store=instance.store,
    )


@receiver(post_delete, sender=MediaFile)
def log_media_file_deletion(sender, instance, **kwargs):
    """Log media file deletion"""
    EventService.log_event(
        event_type="MEDIA_DELETE",
        event_name=f"Media file deleted: {instance.original_filename}",
        properties={
            "entity_type": "MediaFile",
            "entity_id": instance.id,
            "file_size": instance.file_size,
            "mime_type": instance.mime_type,
            "resource_type": instance.resource_type,
        },
        store=instance.store,
    )


@receiver(post_save, sender=MediaFolder)
def log_folder_change(sender, instance, created, **kwargs):
    """Log folder changes"""
    if created:
        event_type = "FOLDER_CREATE"
        message = f"Folder created: {instance.name}"
    else:
        event_type = "FOLDER_UPDATE"
        message = f"Folder updated: {instance.name}"

    EventService.log_event(
        event_type=event_type,
        event_name=message,
        properties={
            "entity_type": "MediaFolder",
            "entity_id": instance.id,
            "folder_name": instance.name,
        },
        user=instance.created_by,
        store=instance.store,
    )
