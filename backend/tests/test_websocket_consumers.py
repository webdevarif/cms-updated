"""
Tests for WebSocket consumers.
Tests real-time functionality for notifications and search.
"""
import json

import pytest
from apps.core.consumers import DashboardConsumer, NotificationsConsumer, SearchConsumer
from apps.notifications.models import Notification
from apps.stores.models import Store
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from django.utils import timezone

User = get_user_model()


class NotificationsConsumerTestCase(TransactionTestCase):
    """Test WebSocket notifications consumer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create a store owned by the user
        self.store = Store.objects.create(name="Test Store", owner=self.user)

    async def test_notifications_consumer_connection(self):
        """Test WebSocket connection for authenticated user."""
        # Create communicator with authenticated user
        communicator = WebsocketCommunicator(NotificationsConsumer.as_asgi(), "/ws/notifications/")

        # Set user in scope
        communicator.scope["user"] = self.user

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Receive connection confirmation
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "connection_established")
        self.assertEqual(response["user_id"], self.user.id)

        # Close connection
        await communicator.disconnect()

    async def test_notifications_consumer_unauthorized(self):
        """Test WebSocket rejects unauthorized connections."""
        # Create communicator without authenticated user
        communicator = WebsocketCommunicator(NotificationsConsumer.as_asgi(), "/ws/notifications/")

        # Connect (should fail)
        connected, close_code = await communicator.connect()
        self.assertFalse(connected)
        self.assertEqual(close_code, 4001)  # Unauthorized

    async def test_notifications_consumer_mark_read(self):
        """Test marking notifications as read via WebSocket."""
        # Create a notification
        notification = Notification.objects.create(
            user=self.user,
            title="Test Notification",
            message="Test message",
            notification_type="info",
            is_read=False,
        )

        # Create communicator
        communicator = WebsocketCommunicator(NotificationsConsumer.as_asgi(), "/ws/notifications/")
        communicator.scope["user"] = self.user

        # Connect
        await communicator.connect()

        # Send mark_read message
        await communicator.send_json_to({"type": "mark_read", "notification_id": notification.id})

        # Receive confirmation
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "notification_marked_read")
        self.assertEqual(response["notification_id"], notification.id)

        # Check notification was marked as read
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

        # Close connection
        await communicator.disconnect()

    async def test_notifications_consumer_initial_unread(self):
        """Test receiving initial unread notifications on connect."""
        # Create unread notifications
        Notification.objects.create(
            user=self.user,
            title="Unread Notification 1",
            message="Message 1",
            notification_type="info",
            is_read=False,
        )
        Notification.objects.create(
            user=self.user,
            title="Unread Notification 2",
            message="Message 2",
            notification_type="warning",
            is_read=False,
        )

        # Create communicator
        communicator = WebsocketCommunicator(NotificationsConsumer.as_asgi(), "/ws/notifications/")
        communicator.scope["user"] = self.user

        # Connect
        await communicator.connect()

        # Skip connection established message
        await communicator.receive_json_from()

        # Receive initial notifications
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "initial_notifications")
        self.assertEqual(response["count"], 2)
        self.assertEqual(len(response["notifications"]), 2)

        # Close connection
        await communicator.disconnect()


class SearchConsumerTestCase(TransactionTestCase):
    """Test WebSocket search consumer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="searchuser", email="search@example.com", password="searchpass123"
        )

        # Create a store
        self.store = Store.objects.create(name="Search Test Store", owner=self.user)

    async def test_search_consumer_connection(self):
        """Test WebSocket connection for search."""
        communicator = WebsocketCommunicator(SearchConsumer.as_asgi(), "/ws/search/")
        communicator.scope["user"] = self.user
        communicator.scope["store"] = self.store

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Receive connection confirmation
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "search_connection_established")
        self.assertEqual(response["user_id"], self.user.id)
        self.assertEqual(response["store_id"], self.store.id)

        # Close connection
        await communicator.disconnect()

    async def test_search_consumer_suggestions(self):
        """Test getting search suggestions via WebSocket."""
        communicator = WebsocketCommunicator(SearchConsumer.as_asgi(), "/ws/search/")
        communicator.scope["user"] = self.user
        communicator.scope["store"] = self.store

        # Connect
        await communicator.connect()

        # Send suggestions request
        await communicator.send_json_to({"type": "get_suggestions", "query": "test", "limit": 5})

        # Receive suggestions response
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "search_suggestions")
        self.assertEqual(response["query"], "test")
        self.assertIsInstance(response["suggestions"], list)

        # Close connection
        await communicator.disconnect()


class DashboardConsumerTestCase(TransactionTestCase):
    """Test WebSocket dashboard consumer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="adminuser", email="admin@example.com", password="adminpass123", is_staff=True
        )

        # Create a store owned by the user
        self.store = Store.objects.create(name="Dashboard Test Store", owner=self.user)

    async def test_dashboard_consumer_connection_authorized(self):
        """Test WebSocket connection for authorized dashboard user."""
        communicator = WebsocketCommunicator(DashboardConsumer.as_asgi(), "/ws/dashboard/")
        communicator.scope["user"] = self.user

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Receive connection confirmation
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "dashboard_connection_established")
        self.assertEqual(response["user_id"], self.user.id)

        # Close connection
        await communicator.disconnect()

    async def test_dashboard_consumer_connection_unauthorized(self):
        """Test WebSocket rejects unauthorized dashboard connections."""
        # Create regular user without store ownership
        regular_user = User.objects.create_user(
            username="regularuser", email="regular@example.com", password="regularpass123"
        )

        communicator = WebsocketCommunicator(DashboardConsumer.as_asgi(), "/ws/dashboard/")
        communicator.scope["user"] = regular_user

        # Connect (should fail)
        connected, close_code = await communicator.connect()
        self.assertFalse(connected)
        self.assertEqual(close_code, 4003)  # Forbidden
