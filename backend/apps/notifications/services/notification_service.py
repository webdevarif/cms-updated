"""
Services for notifications app.
"""

import logging

from apps.notifications.models import (
    Notification,
    NotificationChannel,
    NotificationPreference,
    NotificationStatus,
    NotificationTemplate,
    NotificationType,
)
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Single orchestrator for all notification operations.

    This service is the primary entry point for creating and managing notifications.
    It handles notification creation, channel selection, user preferences, and delegates
    to Celery tasks and channel implementations for actual delivery.

    Core responsibilities:
    - Creating notifications with proper store scoping and metadata
    - Selecting appropriate channels based on user preferences
    - Triggering async delivery via Celery tasks
    - Providing convenient helper methods for common notification patterns

    All other apps should use this service as the only entry point for notifications.
    """

    @staticmethod
    @transaction.atomic
    def create_notification(
        store,
        notification_type,
        title,
        message,
        user=None,
        channels=None,
        metadata=None,
    ):
        """
        Create a new notification and trigger async delivery.

        Args:
            store: Store instance for scoping
            notification_type: Type of notification (e.g., 'order.created')
            title: Notification title
            message: Notification message content
            user: Recipient user (optional for role/store notifications)
            channels: List of channels to send through (default: ['in_app'])
            metadata: Additional context data for templates

        Returns:
            Notification: Created notification instance

        Note: This method triggers async delivery via Celery task.
        """
        if channels is None:
            channels = ["in_app"]
        notification = Notification.objects.create(
            store=store,
            notification_type=notification_type,
            title=title,
            message=message,
            user=user,
            channels=channels,
            metadata=metadata or {},
        )

        # Trigger async sending
        from .tasks import send_notification

        send_notification.delay(notification.id)

        return notification

    @staticmethod
    def notify_user(user, notification_type, context, store=None):
        """
        Notify a specific user respecting their preferences.

        Args:
            user: User instance to notify
            notification_type: Type of notification (e.g., 'order.created')
            context: Dict with notification data (title, message, etc.)
            store: Store instance (auto-detected if not provided)

        Returns:
            Notification: Created notification instance

        Note: Respects user's channel preferences and applies appropriate filtering.
        """
        if not store:
            store = user.storemembership_set.first().store

        # Get user preferences
        from .models import NotificationPreference

        preference = NotificationPreference.objects.filter(
            store=store, user=user, notification_type=notification_type
        ).first()

        # Default channels if no preference
        channels = ["email", "in_app"]
        if preference:
            channels = [channel for channel in channels if preference.is_channel_enabled(channel)]

        return NotificationService.create_notification(
            store=store,
            notification_type=notification_type,
            title=context.get("title", f'{notification_type.replace(".", " ").title()}'),
            message=context.get("message", ""),
            user=user,
            channels=channels,
            metadata=context,
        )

    @staticmethod
    def notify_staff(store, notification_type, context):
        """
        Notify all staff users (owners and staff) in a store.

        Args:
            store: Store instance
            notification_type: Type of notification
            context: Dict with notification data

        Returns:
            List[Notification]: Created notification instances for all staff users

        Note: Respects individual staff user preferences for each notification.
        """
        from django.contrib.auth import get_user_model

        User = get_user_model()

        staff_users = User.objects.filter(
            storemembership__store=store, storemembership__role__in=["owner", "staff"]
        )

        notifications = []
        for user in staff_users:
            notification = NotificationService.notify_user(
                user=user,
                notification_type=notification_type,
                context=context,
                store=store,
            )
            notifications.append(notification)

        return notifications

    @staticmethod
    def create_post_published_notification(post, user=None):
        """
        Create notification for post publish event with proper logging
        """
        from apps.analytics.services.event_service import EventService

        # Create notification
        notification = NotificationService.create_notification(
            user=user,
            notification_type="post_published",
            title=f"New post published: {post.title}",
            message=f"A new post '{post.title}' has been published",
            data={
                "post_id": post.id,
                "post_title": post.title,
                "post_url": post.get_absolute_url(),
                "author": post.author.get_display_name() if post.author else "Unknown",
                "published_at": (post.published_at.isoformat() if post.published_at else None),
            },
            store=post.store,
        )

        # Log POST_PUBLISHED event
        EventService.log_event(
            event_type="POST_PUBLISHED",
            event_name=f"Published post: {post.title}",
            properties={
                "user": user.id if user else None,
                "store": post.store.id,
                "entity_type": "Post",
                "entity_id": post.id,
                "post_title": post.title,
                "post_author": post.author.id if post.author else None,
                "published_at": (post.published_at.isoformat() if post.published_at else None),
            },
            user=user,
            store=post.store,
        )

        return notification

    @staticmethod
    def create_entity_action_notification(entity_interaction, user=None):
        """
        Create notification for entity action (like, favorite, etc.) with EntityService logging
        """
        from apps.analytics.services.event_service import EventService

        # Create notification
        notification = NotificationService.create_notification(
            user=entity_interaction.user,
            notification_type="entity_action",
            title=f"{entity_interaction.action.name}: {entity_interaction.content_object}",
            message=f"{entity_interaction.user.get_display_name()} {entity_interaction.action.name.lower()}d {entity_interaction.content_object}",
            data={
                "entity_interaction_id": entity_interaction.id,
                "action_name": entity_interaction.action.name,
                "action_slug": entity_interaction.action.slug,
                "content_type": entity_interaction.content_type.model,
                "object_id": entity_interaction.object_id,
                "object_repr": str(entity_interaction.content_object),
            },
            store=entity_interaction.store,
        )

        # Log ENTITY_ADDED event
        EventService.log_event(
            event_type="ENTITY_ADDED",
            event_name=f"Entity action added: {entity_interaction.action.name}",
            properties={
                "user": entity_interaction.user.id if entity_interaction.user else None,
                "store": entity_interaction.store.id,
                "entity_type": "entity_interaction",
                "entity_id": entity_interaction.id,
                "action_name": entity_interaction.action.name,
                "action_slug": entity_interaction.action.slug,
                "content_type": entity_interaction.content_type.model,
                "object_id": entity_interaction.object_id,
            },
            user=entity_interaction.user,
            store=entity_interaction.store,
        )

        return notification

    @staticmethod
    def send_notification(notification):
        """
        Send notification via all enabled channels
        """
        from .models import NotificationPreference

        # Check user preferences
        if notification.user:
            preferences = NotificationPreference.objects.filter(
                store=notification.store,
                user=notification.user,
                notification_type=notification.notification_type,
            ).first()

            if preferences:
                # Filter channels based on preferences
                enabled_channels = [
                    channel
                    for channel in notification.channels
                    if preferences.is_channel_enabled(channel)
                ]
                notification.channels = enabled_channels
                notification.save(update_fields=["channels"])

        # Send via each channel
        for channel in notification.channels:
            try:
                if channel == "email":
                    from .channels.email import EmailChannel

                    EmailChannel.send(notification)
                elif channel == "in_app":
                    from .channels.in_app import InAppChannel

                    InAppChannel.send(notification)
                elif channel == "push":
                    from .channels.push import PushChannel

                    PushChannel.send(notification)
                elif channel == "sms":
                    from .channels.sms import SMSChannel

                    SMSChannel.send(notification)
            except Exception as e:
                logger.error(f"Failed to send notification via {channel}: {e}")

        # Update status
        notification.status = "sent"
        notification.delivery_attempts += 1
        notification.last_attempt_at = timezone.now()
        notification.save(update_fields=["status", "delivery_attempts", "last_attempt_at"])

        return notification

    @staticmethod
    def get_user_notifications(user, status=None, limit=50):
        """Get notifications for a user"""
        from .models import Notification

        queryset = Notification.objects.filter(user=user)

        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by("-created_at")[:limit]

    @staticmethod
    def get_unread_count(user):
        """Get unread notification count for user"""
        from .models import Notification

        return Notification.objects.filter(user=user, status="pending").count()

    @staticmethod
    def mark_all_as_read(user):
        """Mark all user notifications as read"""
        from .models import Notification

        count = Notification.objects.filter(user=user, status="pending").update(
            status="read", read_at=timezone.now()
        )

        return count
