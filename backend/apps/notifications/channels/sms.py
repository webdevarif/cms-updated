"""
SMS channel for notifications.
"""
import logging

from .base import BaseChannel

logger = logging.getLogger(__name__)


class SMSChannel(BaseChannel):
    """SMS notification channel"""

    @staticmethod
    def send(notification):
        """Send notification via SMS"""
        if not notification.user or not hasattr(notification.user, "phone"):
            logger.warning(f"No phone number for notification #{notification.id}")
            return

        from ..models import NotificationTemplate

        # Get template
        template = NotificationTemplate.objects.filter(
            store=notification.store, notification_type=notification.notification_type
        ).first()

        if template:
            rendered = template.render(notification.metadata)
            message = rendered.get("sms", notification.message)
        else:
            message = notification.message

        # Send via SMS service (implementation depends on provider)
        # This is a placeholder for actual SMS service integration
        logger.info(f"SMS notification sent to {notification.user.phone}")

    @staticmethod
    def validate_config(notification):
        """Validate SMS configuration"""
        return notification.user and hasattr(notification.user, "phone")
