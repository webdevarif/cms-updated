"""
Tests for notification channels.
"""

import pytest

from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestEmailChannel:
    """Test EmailChannel"""

    def test_validate_config(self):
        """Test email channel validation"""
        from apps.notifications.channels.email import EmailChannel
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

        assert EmailChannel.validate_config(notification) is True


@pytest.mark.django_db
class TestInAppChannel:
    """Test InAppChannel"""

    def test_validate_config(self):
        """Test in-app channel validation"""
        from apps.notifications.channels.in_app import InAppChannel
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

        assert InAppChannel.validate_config(notification) is True
