"""
Celery tasks for notifications.

This module contains async tasks that handle notification delivery, cleanup,
and digest processing. These tasks are called by NotificationService to handle
time-consuming operations asynchronously.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_notification(self, notification_id):
    """
    Async notification sending task.

    Called by NotificationService.create_notification() to send notifications
    asynchronously. This task handles channel delivery and retry logic for failed
    notifications.

    Args:
        notification_id: ID of notification to send

    Returns:
        dict: Notification ID and final status

    Raises:
        Retry: For temporary failures (max 3 retries with 60s backoff)

    Note: This is the primary delivery mechanism for all notifications.
    """
    from .models import Notification
    from .services import NotificationService

    try:
        notification = Notification.objects.get(id=notification_id)
        result = NotificationService.send_notification(notification)

        return {"notification_id": notification_id, "status": result.status}

    except Notification.DoesNotExist:
        logger.error(f"Notification #{notification_id} not found")
        raise

    except Exception as exc:
        logger.error(f"Notification sending failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def cleanup_old_notifications(days=90):
    """
    Clean up old notification records
    """
    from django.utils import timezone

    from .models import Notification

    cutoff = timezone.now() - timezone.timedelta(days=days)
    deleted_count = Notification.objects.filter(created_at__lt=cutoff, status="read").delete()[0]

    logger.info(f"Cleaned up {deleted_count} old notifications")
    return deleted_count


@shared_task
def send_digest_notifications():
    """
    Send digest notifications for users with digest enabled.

    Periodic task that aggregates pending notifications for users who prefer
    digest delivery and sends them as consolidated email notifications.

    This task is typically scheduled to run daily at a specific time.

    Returns:
        None: Logs completion status

    Note: Creates digest notifications and marks individual notifications as delivered.
    """
    from django.utils import timezone

    from .models import Notification, NotificationPreference

    # Get users with digest enabled
    preferences = NotificationPreference.objects.filter(digest_enabled=True).select_related("user")

    for preference in preferences:
        # Get pending notifications
        cutoff = timezone.now() - timezone.timedelta(hours=24)
        notifications = Notification.objects.filter(
            user=preference.user,
            store=preference.store,
            status="pending",
            created_at__gte=cutoff,
        )

        if notifications.exists():
            # Create digest notification
            NotificationService.create_notification(
                store=preference.store,
                notification_type="digest",
                title=f"Your Daily Digest",
                message=f"You have {notifications.count()} new notifications",
                user=preference.user,
                channels=["email"],
                metadata={"notification_count": notifications.count()},
            )

            # Mark as delivered
            notifications.update(status="delivered", delivered_at=timezone.now())

    logger.info("Digest notifications sent")
