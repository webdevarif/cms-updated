"""
In-app channel for notifications.

This channel handles in-app notifications that are stored in the database
and exposed via REST API for notification history. In-app notifications can
optionally be pushed in real-time via WebSocket consumers.
"""

import logging

from django.utils import timezone

from .base import BaseChannel

logger = logging.getLogger(__name__)


class InAppChannel(BaseChannel):
    """
    In-app notification channel.

    This channel stores notifications in the database for in-app display.
    Notifications are exposed via REST API for history and can optionally be
    pushed in real-time via WebSocket consumers.

    Delivery flow:
    1. Notification is stored in Notification model (already done by service)
    2. Channel marks notification as delivered
    3. Optional: WebSocket consumer pushes notification to connected clients
    4. Users can view notification history via REST API
    """

    @staticmethod
    def send(notification):
        """
        Store notification for in-app display and mark as delivered.

        In-app notifications are stored in the database by NotificationService
        before channel delivery. This method marks the notification as delivered
        and optionally triggers real-time push via WebSocket.

        Args:
            notification: Notification instance to deliver

        Returns:
            bool: Always True for in-app notifications

        Note: Real-time delivery is handled separately by WebSocket consumers.
        """
        # Mark notification as delivered for in-app display
        notification.status = "delivered"
        notification.delivered_at = timezone.now()
        notification.save(update_fields=["status", "delivered_at"])

        logger.info(f"In-app notification #{notification.id} delivered")
        return True

    @staticmethod
    def validate_config(notification):
        """
        Validate in-app configuration.

        In-app notifications don't require additional configuration,
        so this method always returns True.

        Args:
            notification: Notification instance to validate

        Returns:
            bool: Always True for in-app notifications
        """
        return True  # Always valid
