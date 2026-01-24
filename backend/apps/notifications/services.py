"""
Services for notifications app.
"""
from django.db import transaction
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Shared notification management service"""
    
    @staticmethod
    @transaction.atomic
    def create_notification(
        store,
        notification_type,
        title,
        message,
        user=None,
        channels=None,
        metadata=None
    ):
        """
        Create a new notification
        """
        if channels is None:
            channels = ['in_app']
        
        from .models import Notification
        notification = Notification.objects.create(
            store=store,
            notification_type=notification_type,
            title=title,
            message=message,
            user=user,
            channels=channels,
            metadata=metadata or {}
        )
        
        # Trigger async sending
        from .tasks import send_notification
        send_notification.delay(notification.id)
        
        return notification
    
    @staticmethod
    def notify_user(user, notification_type, context, store=None):
        """
        Helper method to notify a specific user
        """
        if not store:
            store = user.storemembership_set.first().store
        
        # Get user preferences
        from .models import NotificationPreference
        preference = NotificationPreference.objects.filter(
            store=store,
            user=user,
            notification_type=notification_type
        ).first()
        
        # Default channels if no preference
        channels = ['email', 'in_app']
        if preference:
            channels = [
                channel for channel in channels
                if preference.is_channel_enabled(channel)
            ]
        
        return NotificationService.create_notification(
            store=store,
            notification_type=notification_type,
            title=context.get('title', f'{notification_type.replace(".", " ").title()}'),
            message=context.get('message', ''),
            user=user,
            channels=channels,
            metadata=context
        )
    
    @staticmethod
    def notify_staff(store, notification_type, context):
        """
        Helper method to notify all staff users in a store
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        staff_users = User.objects.filter(
            storemembership__store=store,
            storemembership__role__in=['owner', 'staff']
        )
        
        notifications = []
        for user in staff_users:
            notification = NotificationService.notify_user(
                user=user,
                notification_type=notification_type,
                context=context,
                store=store
            )
            notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def create_post_published_notification(post, user=None):
        """
        Create notification for post publish event with proper logging
        """
        from apps.logs.tasks import log_event_async
        
        # Create notification
        notification = NotificationService.create_notification(
            store=post.store,
            notification_type='post.published',
            title=f'Post Published: {post.title}',
            message=f'Your post "{post.title}" has been published',
            user=user,
            channels=['in_app', 'email'],
            metadata={
                'post_id': str(post.id),
                'post_type': post.post_type.slug,
                'published_at': post.published_at.isoformat() if post.published_at else None
            }
        )
        
        # Log POST_PUBLISHED event
        log_event_async.delay({
            'event_type': 'POST_PUBLISHED',
            'message': f'Published post: {post.title}',
            'store': post.store,
            'user': user,
            'entity_type': 'Post',
            'entity_id': post.id,
            'metadata': {
                'post_id': str(post.id),
                'post_type': post.post_type.slug,
                'notification_id': str(notification.id)
            }
        })
        
        return notification
    
    @staticmethod
    def create_entity_action_notification(entity_interaction, user=None):
        """
        Create notification for entity action (like, favorite, etc.) with EntityService logging
        """
        from apps.logs.tasks import log_event_async
        
        # Create notification
        notification = NotificationService.create_notification(
            store=entity_interaction.store,
            notification_type='entity.action',
            title=f'{entity_interaction.action.name.title()} Added',
            message=f'You {entity_interaction.action.name.lower()} {entity_interaction.content_object}',
            user=user,
            channels=['in_app'],
            metadata={
                'entity_interaction_id': str(entity_interaction.id),
                'action_slug': entity_interaction.action.slug,
                'content_type': entity_interaction.content_type.model,
                'object_id': entity_interaction.object_id
            }
        )
        
        # Log ENTITY_ADDED event
        log_event_async.delay({
            'event_type': 'ENTITY_ADDED',
            'message': f"Entity action added: {entity_interaction.action.name}",
            'store': entity_interaction.store,
            'user': user,
            'entity_type': 'entity_interaction',
            'entity_id': entity_interaction.id,
            'metadata': {
                'action_slug': entity_interaction.action.slug,
                'content_type': entity_interaction.content_type.model,
                'object_id': entity_interaction.object_id,
                'notification_id': str(notification.id)
            }
        })
        
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
                notification_type=notification.notification_type
            ).first()
            
            if preferences:
                # Filter channels based on preferences
                enabled_channels = [
                    channel for channel in notification.channels
                    if preferences.is_channel_enabled(channel)
                ]
                notification.channels = enabled_channels
                notification.save(update_fields=['channels'])
        
        # Send via each channel
        for channel in notification.channels:
            try:
                if channel == 'email':
                    from .channels.email import EmailChannel
                    EmailChannel.send(notification)
                elif channel == 'in_app':
                    from .channels.in_app import InAppChannel
                    InAppChannel.send(notification)
                elif channel == 'push':
                    from .channels.push import PushChannel
                    PushChannel.send(notification)
                elif channel == 'sms':
                    from .channels.sms import SMSChannel
                    SMSChannel.send(notification)
            except Exception as e:
                logger.error(f"Failed to send notification via {channel}: {e}")
        
        # Update status
        notification.status = 'sent'
        notification.delivery_attempts += 1
        notification.last_attempt_at = timezone.now()
        notification.save(update_fields=['status', 'delivery_attempts', 'last_attempt_at'])
        
        return notification
    
    @staticmethod
    def get_user_notifications(user, status=None, limit=50):
        """Get notifications for a user"""
        from .models import Notification
        queryset = Notification.objects.filter(user=user)
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')[:limit]
    
    @staticmethod
    def get_unread_count(user):
        """Get unread notification count for user"""
        from .models import Notification
        return Notification.objects.filter(
            user=user,
            status='pending'
        ).count()
    
    @staticmethod
    def mark_all_as_read(user):
        """Mark all user notifications as read"""
        from .models import Notification
        count = Notification.objects.filter(
            user=user,
            status='pending'
        ).update(status='read', read_at=timezone.now())
        
        return count
