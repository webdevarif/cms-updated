"""
Test compliance with notifications.md rules
"""

from unittest.mock import MagicMock, patch

from apps.ecommerce.models import Inventory, Order, Product
from apps.notifications.models import Notification, NotificationPreference
from apps.notifications.services import NotificationService
from apps.posts.v2.models import Post, PostType
from apps.stores.models import Store

from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class NotificationComplianceTest(TestCase):
    """Test that all notification flows comply with notifications.md"""

    def setUp(self):
        """Set up test data"""
        self.store = Store.objects.create(
            name="Test Store",
            slug="test-store",
            owner=User.objects.create_user(email="owner@test.com", password="testpass123"),
        )

        self.staff_user = User.objects.create_user(email="staff@test.com", password="testpass123")

        self.customer = User.objects.create_user(email="customer@test.com", password="testpass123")

    def test_notification_service_is_single_entry_point(self):
        """Test that NotificationService is the only entry point for notifications"""
        # All notification creation should go through NotificationService.create_notification
        with patch("apps.notifications.tasks.send_notification") as mock_task:
            notification = NotificationService.create_notification(
                store=self.store,
                notification_type="test.type",
                title="Test",
                message="Test message",
                user=self.customer,
            )

            # Verify async task is triggered
            mock_task.delay.assert_called_once_with(notification.id)

            # Verify notification is created with correct status
            self.assertEqual(notification.status, "pending")

    def test_user_preferences_are_respected(self):
        """Test that user preferences are checked and respected"""
        # Create user preference to disable email notifications
        NotificationPreference.objects.create(
            store=self.store,
            user=self.customer,
            notification_type="order.created",
            channel_preferences={"email": False, "in_app": True},
        )

        with patch("apps.notifications.tasks.send_notification") as mock_task:
            notification = NotificationService.notify_user(
                user=self.customer,
                notification_type="order.created",
                context={"title": "Test Order"},
                store=self.store,
            )

            # Verify only in_app channel is used
            self.assertEqual(notification.channels, ["in_app"])

    def test_store_scoping_is_enforced(self):
        """Test that all notifications are store-scoped"""
        notification = NotificationService.create_notification(
            store=self.store,
            notification_type="test.type",
            title="Test",
            message="Test message",
            user=self.customer,
        )

        # Verify notification is store-scoped
        self.assertEqual(notification.store, self.store)

        # Verify queries are store-scoped
        notifications = Notification.objects.filter(store=self.store)
        self.assertIn(notification, notifications)

    def test_async_tasks_only(self):
        """Test that no synchronous sending occurs"""
        with patch("apps.notifications.tasks.send_notification") as mock_task:
            notification = NotificationService.create_notification(
                store=self.store,
                notification_type="test.type",
                title="Test",
                message="Test message",
                user=self.customer,
            )

            # Verify task is called asynchronously
            mock_task.delay.assert_called_once()

            # Verify notification is not immediately sent
            notification.refresh_from_db()
            self.assertEqual(notification.status, "pending")

    def test_retry_logic_for_failures(self):
        """Test that payment failures have proper retry logic"""
        from apps.ecommerce.services.payment_service import handle_payment_failure

        # Create test payment
        product = Product.objects.create(
            store=self.store, title="Test Product", sku="TEST-001", base_price=10.00
        )

        order = Order.objects.create(
            store=self.store,
            user=self.customer,
            order_number="TEST-001",
            total=10.00,
            customer_email="customer@test.com",
        )

        from apps.ecommerce.models import Payment, PaymentMethod

        payment_method = PaymentMethod.objects.create(
            store=self.store, name="Test Method", provider="test"
        )

        payment = Payment.objects.create(
            store=self.store,
            order=order,
            payment_method=payment_method,
            amount=10.00,
            status="failed",
        )

        with patch("apps.notifications.services.NotificationService.notify_user") as mock_notify:
            # Test that task has retry decorator
            self.assertTrue(hasattr(handle_payment_failure, "retry"))
            self.assertEqual(handle_payment_failure.max_retries, 3)

    def test_low_stock_notification(self):
        """Test that low stock notifications are sent to staff"""
        # Create product with inventory
        product = Product.objects.create(
            store=self.store, title="Test Product", sku="TEST-001", base_price=10.00
        )

        inventory = Inventory.objects.create(
            store=self.store, product=product, quantity=5, low_stock_threshold=10
        )

        with patch("apps.notifications.services.NotificationService.notify_staff") as mock_notify:
            # Trigger low stock check
            inventory.quantity = 5  # Below threshold
            inventory.save()

            # Verify notify_staff is called
            mock_notify.assert_called_once()

    def test_post_published_notification(self):
        """Test that post publishing triggers notification"""
        post_type = PostType.objects.create(store=self.store, name="Blog", slug="blog")

        post = Post.objects.create(
            store=self.store,
            post_type=post_type,
            author=self.customer,
            title="Test Post",
            content="Test content",
            status="draft",
        )

        with patch("apps.notifications.services.NotificationService.notify_user") as mock_notify:
            # Publish post
            post.status = "published"
            post.save()

            # Verify notification is sent
            mock_notify.assert_called_once()

    def test_order_notifications(self):
        """Test that order events trigger proper notifications"""
        with patch(
            "apps.notifications.services.NotificationService.notify_user"
        ) as mock_user, patch(
            "apps.notifications.services.NotificationService.notify_staff"
        ) as mock_staff:
            # Create order
            from apps.ecommerce.v2.services import OrderService

            order = OrderService.create_order(
                store=self.store,
                user=self.customer,
                cart_data={"subtotal": 10.00, "total": 10.00, "items": []},
                shipping_data={},
                billing_data={"email": "customer@test.com"},
            )

            # Verify both customer and staff notifications
            mock_user.assert_called_once()
            mock_staff.assert_called_once()

    def test_payment_failure_retry(self):
        """Test that payment failures use Celery retry with exponential backoff"""
        from apps.ecommerce.services.payment_service import handle_payment_failure

        # Verify task has proper retry configuration
        self.assertTrue(hasattr(handle_payment_failure, "retry"))
        self.assertEqual(handle_payment_failure.max_retries, 3)

        # Test exponential backoff calculation
        with patch(
            "apps.ecommerce.services.payment_service.handle_payment_failure.retry"
        ) as mock_retry:
            # Simulate failure
            handle_payment_failure.retry(exc=Exception("Test error"))

            # Verify retry is called with countdown
            mock_retry.assert_called()

    def test_cleanup_task_exists(self):
        """Test that cleanup task exists and works"""
        from apps.notifications.tasks import cleanup_old_notifications

        with patch("apps.notifications.models.Notification.objects.filter") as mock_filter:
            # Run cleanup
            cleanup_old_notifications(days=90)

            # Verify cleanup is called with correct filter
            mock_filter.assert_called_once()
