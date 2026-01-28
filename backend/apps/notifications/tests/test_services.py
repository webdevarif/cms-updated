"""
Tests for notification services.
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestNotificationService:
    """Test NotificationService"""

    def test_create_notification(self):
        """Test notification creation"""
        from apps.notifications.models import Notification
        from apps.notifications.services import NotificationService
        from apps.stores.models import Store

        user = User.objects.create_user(email="test@example.com", password="pass")
        store = Store.objects.create(name="Test Store", owner=user)

        notification = NotificationService.create_notification(
            store=store,
            notification_type="order.created",
            title="Order Created",
            message="Your order has been created",
            user=user,
        )

        assert notification.notification_type == "order.created"
        assert notification.user == user
        assert notification.status == "pending"
