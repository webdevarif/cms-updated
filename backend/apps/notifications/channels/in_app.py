"""
In-app channel for notifications.
"""
import logging

from django.utils import timezone

from .base import BaseChannel

logger = logging.getLogger(__name__)


class InAppChannel(BaseChannel):
    """In-app notification channel"""

    @staticmethod
    def send(notification):
        """Store notification for in-app display"""
        # In-app notifications are stored in the database
        # No additional action needed
        notification.status = "delivered"
        notification.delivered_at = timezone.now()
        notification.save(update_fields=["status", "delivered_at"])

        logger.info(f"In-app notification #{notification.id} delivered")

    @staticmethod
    def validate_config(notification):
        """Validate in-app configuration"""
        return True  # Always valid
