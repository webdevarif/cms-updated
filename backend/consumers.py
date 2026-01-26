"""
WebSocket consumers for real-time features using Django Channels.
Provides real-time notifications and search updates via WebSockets.
"""
import json
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.notifications.models import Notification
from apps.search.services import SearchService

logger = logging.getLogger(__name__)
User = get_user_model()


class NotificationsConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    Pushes new notifications to authenticated users.
    """

    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope.get('user')

        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)  # Unauthorized
            return

        # Create a unique group for this user
        self.user_group = f"user_{self.user.id}_notifications"

        # Join the user's notification group
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )

        await self.accept()
        logger.info(f"User {self.user.id} connected to notifications WebSocket")

        # Send initial connection confirmation
        await self.send_json({
            'type': 'connection_established',
            'message': 'Connected to notifications',
            'user_id': self.user.id,
            'timestamp': timezone.now().isoformat()
        })

        # Send any unread notifications on connect
        unread_notifications = await self.get_unread_notifications()
        if unread_notifications:
            await self.send_json({
                'type': 'initial_notifications',
                'notifications': unread_notifications,
                'count': len(unread_notifications)
            })

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )
        logger.info(f"User {self.user.id if self.user else 'unknown'} disconnected from notifications")

    async def receive_json(self, content):
        """Handle incoming WebSocket messages."""
        message_type = content.get('type', '')

        if message_type == 'mark_read':
            notification_id = content.get('notification_id')
            if notification_id:
                await self.mark_notification_read(notification_id)
                await self.send_json({
                    'type': 'notification_marked_read',
                    'notification_id': notification_id,
                    'timestamp': timezone.now().isoformat()
                })

        elif message_type == 'mark_all_read':
            await self.mark_all_notifications_read()
            await self.send_json({
                'type': 'all_notifications_marked_read',
                'timestamp': timezone.now().isoformat()
            })

        elif message_type == 'subscribe_to_post':
            # Subscribe to post-specific notifications (comments, etc.)
            post_id = content.get('post_id')
            if post_id:
                await self.subscribe_to_post(post_id)
                await self.send_json({
                    'type': 'subscribed_to_post',
                    'post_id': post_id,
                    'timestamp': timezone.now().isoformat()
                })

        elif message_type == 'subscribe_to_product':
            # Subscribe to product-specific notifications (reviews, etc.)
            product_id = content.get('product_id')
            if product_id:
                await self.subscribe_to_product(product_id)
                await self.send_json({
                    'type': 'subscribed_to_product',
                    'product_id': product_id,
                    'timestamp': timezone.now().isoformat()
                })

        elif message_type == 'unsubscribe_from_post':
            # Unsubscribe from post-specific notifications
            post_id = content.get('post_id')
            if post_id:
                await self.unsubscribe_from_post(post_id)
                await self.send_json({
                    'type': 'unsubscribed_from_post',
                    'post_id': post_id,
                    'timestamp': timezone.now().isoformat()
                })

        elif message_type == 'unsubscribe_from_product':
            # Unsubscribe from product-specific notifications
            product_id = content.get('product_id')
            if product_id:
                await self.unsubscribe_from_product(product_id)
                await self.send_json({
                    'type': 'unsubscribed_from_product',
                    'product_id': product_id,
                    'timestamp': timezone.now().isoformat()
                })

        elif message_type == 'ping':
            # Handle ping/pong for connection health
            await self.send_json({
                'type': 'pong',
                'timestamp': timezone.now().isoformat()
            })

    async def comment_created_message(self, event):
        """Send comment creation notification to WebSocket."""
        await self.send_json({
            'type': 'comment_created',
            'comment': event['comment'],
            'post_id': event['post_id'],
            'timestamp': event['timestamp']
        })

    async def comment_approved_message(self, event):
        """Send comment approval notification to WebSocket."""
        await self.send_json({
            'type': 'comment_approved',
            'comment': event['comment'],
            'post_id': event['post_id'],
            'timestamp': event['timestamp']
        })

    async def comment_rejected_message(self, event):
        """Send comment rejection notification to WebSocket."""
        await self.send_json({
            'type': 'comment_rejected',
            'comment': event['comment'],
            'post_id': event['post_id'],
            'reason': event.get('reason'),
            'timestamp': event['timestamp']
        })

    async def review_created_message(self, event):
        """Send review creation notification to WebSocket."""
        await self.send_json({
            'type': 'review_created',
            'review': event['review'],
            'product_id': event['product_id'],
            'timestamp': event['timestamp']
        })

    async def review_approved_message(self, event):
        """Send review approval notification to WebSocket."""
        await self.send_json({
            'type': 'review_approved',
            'review': event['review'],
            'product_id': event['product_id'],
            'timestamp': event['timestamp']
        })

    async def review_rejected_message(self, event):
        """Send review rejection notification to WebSocket."""
        await self.send_json({
            'type': 'review_rejected',
            'review': event['review'],
            'product_id': event['product_id'],
            'reason': event.get('reason'),
            'timestamp': event['timestamp']
        })

    async def subscribe_to_post(self, post_id):
        """Subscribe to post-specific notifications."""
        self.post_group = f"post_{post_id}_comments"
        await self.channel_layer.group_add(
            self.post_group,
            self.channel_name
        )
        logger.info(f"User {self.user.id} subscribed to post {post_id} notifications")

    async def subscribe_to_product(self, product_id):
        """Subscribe to product-specific notifications."""
        self.product_group = f"product_{product_id}_reviews"
        await self.channel_layer.group_add(
            self.product_group,
            self.channel_name
        )
        logger.info(f"User {self.user.id} subscribed to product {product_id} notifications")

    async def unsubscribe_from_post(self, post_id):
        """Unsubscribe from post-specific notifications."""
        if hasattr(self, 'post_group'):
            await self.channel_layer.group_discard(
                self.post_group,
                self.channel_name
            )
            logger.info(f"User {self.user.id} unsubscribed from post {post_id} notifications")

    async def unsubscribe_from_product(self, product_id):
        """Unsubscribe from product-specific notifications."""
        if hasattr(self, 'product_group'):
            await self.channel_layer.group_discard(
                self.product_group,
                self.channel_name
            )
            logger.info(f"User {self.user.id} unsubscribed from product {product_id} notifications")

    async def bulk_notification_message(self, event):
        """Send bulk notifications to WebSocket."""
        await self.send_json({
            'type': 'bulk_notifications',
            'notifications': event['notifications'],
            'count': len(event['notifications']),
            'timestamp': event['timestamp']
        })

    @database_sync_to_async
    def get_unread_notifications(self):
        """Get unread notifications for the user."""
        try:
            notifications = Notification.objects.filter(
                user=self.user,
                is_read=False
            ).order_by('-created_at')[:10]  # Limit to 10 most recent

            return [{
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'type': n.notification_type,
                'data': n.data,
                'created_at': n.created_at.isoformat(),
                'priority': n.priority
            } for n in notifications]

        except Exception as e:
            logger.error(f"Error getting unread notifications: {str(e)}")
            return []

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark a specific notification as read."""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=['is_read', 'read_at'])
        except Notification.DoesNotExist:
            logger.warning(f"Notification {notification_id} not found for user {self.user.id}")

    @database_sync_to_async
    def mark_all_notifications_read(self):
        """Mark all notifications as read for the user."""
        try:
            Notification.objects.filter(
                user=self.user,
                is_read=False
            ).update(
                is_read=True,
                read_at=timezone.now()
            )
        except Exception as e:
            logger.error(f"Error marking all notifications read: {str(e)}")


class SearchConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time search updates.
    Provides live search suggestions and results.
    """

    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope.get('user')
        self.store = self.scope.get('store')  # Store from middleware

        # Create a unique group for this user's search session
        self.search_group = f"user_{self.user.id if self.user else 'anonymous'}_search"

        # Join the search group
        await self.channel_layer.group_add(
            self.search_group,
            self.channel_name
        )

        await self.accept()
        logger.info(f"User {self.user.id if self.user else 'anonymous'} connected to search WebSocket")

        # Send connection confirmation
        await self.send_json({
            'type': 'search_connection_established',
            'message': 'Connected to live search',
            'user_id': self.user.id if self.user else None,
            'store_id': self.store.id if self.store else None,
            'timestamp': timezone.now().isoformat()
        })

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'search_group'):
            await self.channel_layer.group_discard(
                self.search_group,
                self.channel_name
            )
        logger.info(f"User {self.user.id if self.user else 'anonymous'} disconnected from search")

    async def receive_json(self, content):
        """Handle incoming search WebSocket messages."""
        message_type = content.get('type', '')

        if message_type == 'search_query':
            query = content.get('query', '').strip()
            search_type = content.get('search_type', 'all')
            limit = min(int(content.get('limit', 20)), 50)

            if query and len(query) >= 2:
                # Perform real-time search
                search_result = await self.perform_live_search(query, search_type, limit)

                await self.send_json({
                    'type': 'search_results',
                    'query': query,
                    'search_type': search_type,
                    'results': search_result,
                    'timestamp': timezone.now().isoformat()
                })

        elif message_type == 'get_suggestions':
            query = content.get('query', '').strip()
            limit = min(int(content.get('limit', 10)), 20)

            if query and len(query) >= 1:
                # Get search suggestions
                suggestions = await self.get_live_suggestions(query, limit)

                await self.send_json({
                    'type': 'search_suggestions',
                    'query': query,
                    'suggestions': suggestions,
                    'timestamp': timezone.now().isoformat()
                })

        elif message_type == 'ping':
            # Handle ping/pong for connection health
            await self.send_json({
                'type': 'pong',
                'timestamp': timezone.now().isoformat()
            })

    async def search_update_message(self, event):
        """Send search-related updates to WebSocket."""
        await self.send_json({
            'type': 'search_update',
            'update_type': event['update_type'],
            'data': event['data'],
            'timestamp': event['timestamp']
        })

    @database_sync_to_async
    def perform_live_search(self, query, search_type, limit):
        """Perform live search synchronously."""
        try:
            # Use the enhanced SearchService
            search_result = SearchService.search(
                query=query,
                types=[search_type] if search_type != 'all' else None,
                store=self.store,
                limit=limit,
                offset=0,
                user=self.user if self.user and self.user.is_authenticated else None
            )

            return search_result.get('results', [])

        except Exception as e:
            logger.error(f"Live search error: {str(e)}")
            return []

    @database_sync_to_async
    def get_live_suggestions(self, query, limit):
        """Get live search suggestions synchronously."""
        try:
            suggestions = SearchService.get_suggestions(
                store=self.store,
                query=query,
                limit=limit
            )

            return [{'text': s, 'type': 'suggestion'} for s in suggestions]

        except Exception as e:
            logger.error(f"Live suggestions error: {str(e)}")
            return []


class DashboardConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for dashboard real-time updates.
    Provides live analytics and system status updates.
    """

    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope.get('user')

        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)  # Unauthorized
            return

        # Check if user has admin/store owner permissions
        if not await self.has_dashboard_access():
            await self.close(code=4003)  # Forbidden
            return

        # Create dashboard group for this user
        self.dashboard_group = f"user_{self.user.id}_dashboard"

        # Join the dashboard group
        await self.channel_layer.group_add(
            self.dashboard_group,
            self.channel_name
        )

        await self.accept()
        logger.info(f"User {self.user.id} connected to dashboard WebSocket")

        # Send initial dashboard data
        await self.send_json({
            'type': 'dashboard_connection_established',
            'message': 'Connected to dashboard updates',
            'user_id': self.user.id,
            'timestamp': timezone.now().isoformat()
        })

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'dashboard_group'):
            await self.channel_layer.group_discard(
                self.dashboard_group,
                self.channel_name
            )
        logger.info(f"User {self.user.id} disconnected from dashboard")

    async def receive_json(self, content):
        """Handle incoming dashboard WebSocket messages."""
        message_type = content.get('type', '')

        if message_type == 'request_analytics':
            # Send current analytics data
            analytics_data = await self.get_current_analytics()
            await self.send_json({
                'type': 'analytics_update',
                'data': analytics_data,
                'timestamp': timezone.now().isoformat()
            })

        elif message_type == 'ping':
            await self.send_json({
                'type': 'pong',
                'timestamp': timezone.now().isoformat()
            })

    async def analytics_update_message(self, event):
        """Send analytics updates to dashboard."""
        await self.send_json({
            'type': 'analytics_update',
            'data': event['analytics'],
            'update_type': event['update_type'],
            'timestamp': event['timestamp']
        })

    async def system_status_message(self, event):
        """Send system status updates to dashboard."""
        await self.send_json({
            'type': 'system_status',
            'status': event['status'],
            'timestamp': event['timestamp']
        })

    @database_sync_to_async
    def has_dashboard_access(self):
        """Check if user has dashboard access permissions."""
        try:
            # Check if user owns any stores (store owner) or has admin permissions
            return self.user.stores_owned.exists() or self.user.is_staff or self.user.is_superuser
        except Exception:
            return False

    @database_sync_to_async
    def get_current_analytics(self):
        """Get current analytics data for dashboard."""
        try:
            # Get basic analytics overview
            analytics = {
                'stores': self.user.stores_owned.count(),
                'total_posts': 0,  # Would aggregate from user's stores
                'total_orders': 0,  # Would aggregate from user's stores
                'system_status': 'healthy'
            }

            # This would be enhanced with real analytics data
            return analytics

        except Exception as e:
            logger.error(f"Dashboard analytics error: {str(e)}")
            return {'error': 'Analytics unavailable'}
