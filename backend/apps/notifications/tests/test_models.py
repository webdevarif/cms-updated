"""
Tests for notification models.
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestNotificationModel:
    """Test Notification model"""

    def test_create_notification(self):
        """Test creating a notification"""
        from apps.notifications.models import Notification
        from apps.stores.models import Store

        user = User.objects.create_user(email="test@example.com", password="pass")
        store = Store.objects.create(name="Test Store", owner=user)

        notification = Notification.objects.create(
            store=store,
            notification_type="order.created",
            title="Order Created",
            message="Your order has been created",
            user=user,
        )

        assert str(notification) == "Order Created - test@example.com"
        assert notification.status == "pending"

    def test_mark_as_read(self):
        """Test marking notification as read"""
        from apps.notifications.models import Notification
        from apps.stores.models import Store

        user = User.objects.create_user(email="test@example.com", password="pass")
        store = Store.objects.create(name="Test Store", owner=user)

        notification = Notification.objects.create(
            store=store,
            notification_type="order.created",
            title="Order Created",
            message="Your order has been created",
            user=user,
        )

        notification.mark_as_read()

        assert notification.status == "read"
        assert notification.read_at is not None
