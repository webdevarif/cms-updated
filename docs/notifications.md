# Notifications App Rules v1.0

## 🎯 Purpose

This document defines strict development rules for the **notifications** app in CMS-Updated backend, implementing a unified, multi-channel notification system supporting email, in-app, push, and SMS notifications.

---

## 🏗️ Notifications App Structure

### **Fixed Directory Structure**
```
apps/
├── notifications/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── admin.py
│   ├── services.py
│   ├── tasks.py
│   ├── channels/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── email.py
│   │   ├── in_app.py
│   │   ├── push.py
│   │   └── sms.py
│   ├── management/
│   │   └── commands/
│   │       ├── cleanup_notifications.py
│   │       └── send_digest.py
│   ├── migrations/
│   ├── v2/
│   │   ├── __init__.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_services.py
│       └── test_channels.py
```

---

## 📋 Core Models

### **Model Inheritance**
All notifications models must inherit from `TenantModel` for store scoping:

```python
from core.models import TenantModel
from django.db import models

class Notification(TenantModel):
    # Store-scoped notification model
    pass
```

### **Notification Model**
```python
# apps/notifications/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import TenantModel

User = get_user_model()

class NotificationType(models.TextChoices):
    """Predefined notification types"""
    ORDER_CREATED = 'order.created', 'Order Created'
    ORDER_SHIPPED = 'order.shipped', 'Order Shipped'
    ORDER_DELIVERED = 'order.delivered', 'Order Delivered'
    PAYMENT_RECEIVED = 'payment.received', 'Payment Received'
    PRODUCT_LOW_STOCK = 'product.low_stock', 'Product Low Stock'
    PRODUCT_OUT_OF_STOCK = 'product.out_of_stock', 'Product Out of Stock'
    FORM_SUBMITTED = 'form.submitted', 'Form Submitted'
    USER_REGISTERED = 'user.registered', 'User Registered'
    SYSTEM_ALERT = 'system.alert', 'System Alert'
    CUSTOM = 'custom', 'Custom Notification'

class NotificationChannel(models.TextChoices):
    """Available notification channels"""
    EMAIL = 'email', 'Email'
    IN_APP = 'in_app', 'In-App'
    PUSH = 'push', 'Push'
    SMS = 'sms', 'SMS'

class NotificationStatus(models.TextChoices):
    """Notification delivery status"""
    PENDING = 'pending', 'Pending'
    SENT = 'sent', 'Sent'
    DELIVERED = 'delivered', 'Delivered'
    FAILED = 'failed', 'Failed'
    READ = 'read', 'Read'

class Notification(TenantModel):
    """
    Store-scoped notification for multi-channel delivery
    """
    
    # Core fields
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        db_index=True
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Relationships
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    
    # Targeting
    target_type = models.CharField(
        max_length=50,
        choices=[
            ('user', 'User'),
            ('role', 'Role'),
            ('store', 'Store'),
            ('all', 'All')
        ],
        default='user'
    )
    target_id = models.CharField(max_length=100, blank=True)
    
    # Channels
    channels = models.JSONField(
        default=list,
        help_text="List of channels to send notification through"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default='pending'
    )
    
    # Delivery tracking
    delivery_attempts = models.PositiveSmallIntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta(TenantModel.Meta):
        db_table = 'notifications_notification'
        indexes = [
            models.Index(fields=['store', 'user', 'status']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.email if self.user else 'No user'}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if self.status != 'read':
            self.status = 'read'
            self.read_at = timezone.now()
            self.save(update_fields=['status', 'read_at'])
    
    def is_delivered(self):
        """Check if notification is delivered"""
        return self.status in ['delivered', 'read']
    
    def should_send_via_channel(self, channel):
        """Check if notification should be sent via specific channel"""
        return channel in self.channels
```

### **NotificationPreference Model**
```python
class NotificationPreference(TenantModel):
    """
    User notification preferences per channel and type
    """
    
    # Relationships
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Preferences
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices
    )
    channel_preferences = models.JSONField(
        default=dict,
        help_text="Channel preferences: {email: true, in_app: true, push: false, sms: false}"
    )
    
    # Digest settings
    digest_enabled = models.BooleanField(default=False)
    digest_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediate'),
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly')
        ],
        default='immediate'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta(TenantModel.Meta):
        db_table = 'notifications_preference'
        unique_together = [['store', 'user', 'notification_type']]
        ordering = ['user', 'notification_type']
    
    def __str__(self):
        return f"{self.user.email} - {self.notification_type}"
    
    def is_channel_enabled(self, channel):
        """Check if channel is enabled for this notification type"""
        return self.channel_preferences.get(channel, True)
```

### **NotificationTemplate Model**
```python
class NotificationTemplate(TenantModel):
    """
    Reusable notification templates
    """
    
    # Core fields
    name = models.CharField(max_length=255)
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices
    )
    
    # Template content
    title_template = models.CharField(max_length=255)
    message_template = models.TextField()
    
    # Channel-specific templates
    email_subject_template = models.CharField(max_length=255, blank=True)
    email_body_template = models.TextField(blank=True)
    push_title_template = models.CharField(max_length=255, blank=True)
    push_body_template = models.TextField(blank=True)
    sms_template = models.TextField(blank=True)
    
    # Variables documentation
    variables = models.JSONField(
        default=dict,
        help_text="Available variables and their descriptions"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta(TenantModel.Meta):
        db_table = 'notifications_template'
        unique_together = [['store', 'notification_type', 'name']]
        ordering = ['notification_type', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.notification_type}"
    
    def render(self, context):
        """Render template with context variables"""
        from django.template import Template, Context
        
        def render_template(template_string):
            template = Template(template_string)
            return template.render(Context(context))
        
        return {
            'title': render_template(self.title_template),
            'message': render_template(self.message_template),
            'email_subject': render_template(self.email_subject_template) if self.email_subject_template else None,
            'email_body': render_template(self.email_body_template) if self.email_body_template else None,
            'push_title': render_template(self.push_title_template) if self.push_title_template else None,
            'push_body': render_template(self.push_body_template) if self.push_body_template else None,
            'sms': render_template(self.sms_template) if self.sms_template else None,
        }
```

---

## 🔌 API Endpoints

### **V2-Only Implementation**
All notification endpoints must be V2-only with clean architecture:

#### NotificationViewSet
```python
# apps/notifications/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class NotificationViewSet(TenantViewSet):
    """
    Notification management endpoints for dashboard
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    filterset_fields = ['status', 'notification_type', 'user']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    @extend_schema(
        summary="Mark as Read",
        description="Mark notification as read",
        responses={200: NotificationSerializer}
    )
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Resend Notification",
        description="Resend failed notification",
        responses={200: NotificationSerializer}
    )
    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        """Resend notification"""
        notification = self.get_object()
        
        from services.notification import NotificationService
        NotificationService.send_notification(notification)
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)
```

#### NotificationPreferenceViewSet
```python
class NotificationPreferenceViewSet(TenantViewSet):
    """
    Notification preference management endpoints
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    
    queryset = NotificationPreference.objects.all()
    serializer_class = NotificationPreferenceSerializer
    filterset_fields = ['notification_type']
    ordering_fields = ['notification_type']
    ordering = ['notification_type']
```

---

## 🛠️ Services Layer

### **Business Logic Centralization**
All notification business logic must be in services.py:

#### NotificationService
```python
# apps/notifications/services.py
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
    def send_notification(notification):
        """
        Send notification via all enabled channels
        """
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
                NotificationService._send_via_channel(notification, channel)
            except Exception as e:
                logger.error(f"Failed to send notification via {channel}: {e}")
        
        # Update status
        notification.status = 'sent'
        notification.delivery_attempts += 1
        notification.last_attempt_at = timezone.now()
        notification.save(update_fields=['status', 'delivery_attempts', 'last_attempt_at'])
        
        return notification
    
    @staticmethod
    def _send_via_channel(notification, channel):
        """Send notification via specific channel"""
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
    
    @staticmethod
    def get_user_notifications(user, status=None, limit=50):
        """Get notifications for a user"""
        queryset = Notification.objects.filter(user=user)
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')[:limit]
    
    @staticmethod
    def get_unread_count(user):
        """Get unread notification count for user"""
        return Notification.objects.filter(
            user=user,
            status='pending'
        ).count()
    
    @staticmethod
    def mark_all_as_read(user):
        """Mark all user notifications as read"""
        count = Notification.objects.filter(
            user=user,
            status='pending'
        ).update(status='read', read_at=timezone.now())
        
        return count
```

---

## 📡 Channel Implementations

### **Base Channel**
```python
# apps/notifications/channels/base.py
from abc import ABC, abstractmethod

class BaseChannel(ABC):
    """Base channel class"""
    
    @staticmethod
    @abstractmethod
    def send(notification):
        """Send notification via this channel"""
        pass
    
    @staticmethod
    @abstractmethod
    def validate_config(notification):
        """Validate channel configuration"""
        pass
```

### **Email Channel**
```python
# apps/notifications/channels/email.py
from .base import BaseChannel
from services.smtp import SMTPService

class EmailChannel(BaseChannel):
    """Email notification channel"""
    
    @staticmethod
    def send(notification):
        """Send notification via email"""
        if not notification.user or not notification.user.email:
            logger.warning(f"No email for notification #{notification.id}")
            return
        
        # Get or create email template
        template = NotificationTemplate.objects.filter(
            store=notification.store,
            notification_type=notification.notification_type
        ).first()
        
        if template:
            rendered = template.render(notification.metadata)
            subject = rendered.get('email_subject', notification.title)
            body = rendered.get('email_body', notification.message)
        else:
            subject = notification.title
            body = notification.message
        
        # Send via SMTP service
        SMTPService.send_template_email(
            template_name='notification',
            recipients=[notification.user.email],
            subject=subject,
            html_content=body,
            text_content=notification.message,
            store=notification.store
        )
        
        logger.info(f"Email notification sent to {notification.user.email}")
    
    @staticmethod
    def validate_config(notification):
        """Validate email configuration"""
        return notification.user and notification.user.email
```

### **In-App Channel**
```python
# apps/notifications/channels/in_app.py
from .base import BaseChannel

class InAppChannel(BaseChannel):
    """In-app notification channel"""
    
    @staticmethod
    def send(notification):
        """Store notification for in-app display"""
        # In-app notifications are stored in the database
        # No additional action needed
        notification.status = 'delivered'
        notification.delivered_at = timezone.now()
        notification.save(update_fields=['status', 'delivered_at'])
        
        logger.info(f"In-app notification #{notification.id} delivered")
    
    @staticmethod
    def validate_config(notification):
        """Validate in-app configuration"""
        return True  # Always valid
```

### **Push Channel**
```python
# apps/notifications/channels/push.py
from .base import BaseChannel

class PushChannel(BaseChannel):
    """Push notification channel"""
    
    @staticmethod
    def send(notification):
        """Send notification via push"""
        # Get user's push tokens
        from .models import PushToken
        tokens = PushToken.objects.filter(
            user=notification.user,
            is_active=True
        )
        
        if not tokens.exists():
            logger.warning(f"No push tokens for user {notification.user.email}")
            return
        
        # Get template
        template = NotificationTemplate.objects.filter(
            store=notification.store,
            notification_type=notification.notification_type
        ).first()
        
        if template:
            rendered = template.render(notification.metadata)
            title = rendered.get('push_title', notification.title)
            body = rendered.get('push_body', notification.message)
        else:
            title = notification.title
            body = notification.message
        
        # Send via FCM/APNs (implementation depends on provider)
        # This is a placeholder for actual push service integration
        for token in tokens:
            # Send push notification
            logger.info(f"Push notification sent to {token.token}")
    
    @staticmethod
    def validate_config(notification):
        """Validate push configuration"""
        from .models import PushToken
        return PushToken.objects.filter(
            user=notification.user,
            is_active=True
        ).exists()
```

### **SMS Channel**
```python
# apps/notifications/channels/sms.py
from .base import BaseChannel

class SMSChannel(BaseChannel):
    """SMS notification channel"""
    
    @staticmethod
    def send(notification):
        """Send notification via SMS"""
        if not notification.user or not notification.user.phone:
            logger.warning(f"No phone number for notification #{notification.id}")
            return
        
        # Get template
        template = NotificationTemplate.objects.filter(
            store=notification.store,
            notification_type=notification.notification_type
        ).first()
        
        if template:
            rendered = template.render(notification.metadata)
            message = rendered.get('sms', notification.message)
        else:
            message = notification.message
        
        # Send via SMS service (implementation depends on provider)
        # This is a placeholder for actual SMS service integration
        logger.info(f"SMS notification sent to {notification.user.phone}")
    
    @staticmethod
    def validate_config(notification):
        """Validate SMS configuration"""
        return notification.user and notification.user.phone
```

---

## 🔄 Celery Tasks

### **Async Notification Sending**
```python
# apps/notifications/tasks.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_notification(self, notification_id):
    """
    Async notification sending task
    """
    from .models import Notification
    from .services import NotificationService
    
    try:
        notification = Notification.objects.get(id=notification_id)
        result = NotificationService.send_notification(notification)
        
        return {
            'notification_id': notification_id,
            'status': result.status
        }
        
    except Notification.DoesNotExist:
        logger.error(f"Notification #{notification_id} not found")
        raise
        
    except Exception as exc:
        logger.error(f"Notification sending failed: {exc}")
        raise self.retry(exc=exc, countdown=60)

@shared_task
def cleanup_old_notifications(days=90):
    """
    Clean up old notification records
    """
    from django.utils import timezone
    from .models import Notification
    
    cutoff = timezone.now() - timezone.timedelta(days=days)
    deleted_count = Notification.objects.filter(
        created_at__lt=cutoff,
        status='read'
    ).delete()[0]
    
    logger.info(f"Cleaned up {deleted_count} old notifications")
    return deleted_count

@shared_task
def send_digest_notifications():
    """
    Send digest notifications for users with digest enabled
    """
    from .models import Notification, NotificationPreference
    from django.utils import timezone
    
    # Get users with digest enabled
    preferences = NotificationPreference.objects.filter(
        digest_enabled=True
    ).select_related('user')
    
    for preference in preferences:
        # Get pending notifications
        cutoff = timezone.now() - timezone.timedelta(hours=24)
        notifications = Notification.objects.filter(
            user=preference.user,
            store=preference.store,
            status='pending',
            created_at__gte=cutoff
        )
        
        if notifications.exists():
            # Create digest notification
            NotificationService.create_notification(
                store=preference.store,
                notification_type='digest',
                title=f'Your Daily Digest',
                message=f'You have {notifications.count()} new notifications',
                user=preference.user,
                channels=['email'],
                metadata={'notification_count': notifications.count()}
            )
            
            # Mark as delivered
            notifications.update(status='delivered', delivered_at=timezone.now())
    
    logger.info("Digest notifications sent")
```

---

## 🔒 Security Rules

### **Notification Security**
- **User Privacy**: Only send notifications to authorized users
- **Data Minimization**: Only include necessary data in notifications
- **Rate Limiting**: Implement rate limiting on notification endpoints
- **Content Validation**: Validate all notification content
- **Channel Validation**: Validate channel configurations
- **Opt-out Support**: Allow users to opt-out of notifications
- **Secure Templates**: Prevent template injection attacks
- **Audit Logging**: Log all notification events

---

## 📊 Performance Rules

### **Delivery Optimization**
- **Async Sending**: All notification sending must be asynchronous
- **Batch Processing**: Process multiple notifications in batches
- **Queue Management**: Use Celery for notification queue
- **Cleanup**: Regular cleanup of old notifications
- **Caching**: Cache notification templates

### **Database Optimization**
- **Indexes**: Add indexes on frequently queried fields
- **Query Optimization**: Use `select_related` for user lookups
- **Bulk Operations**: Use bulk operations for cleanup
- **Partitioning**: Consider partitioning large notification tables by date

---

## 🧪 Testing Rules

### **Required Coverage**
- **Models**: 95% code coverage
- **Services**: 100% code coverage
- **Channels**: 100% code coverage
- **Views**: 90% code coverage

### **Test Examples**
```python
# apps/notifications/tests/test_services.py
from django.test import TestCase
from ..models import Notification, NotificationPreference
from ..services import NotificationService

class NotificationServiceTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', slug='test-store')
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password'
        )
    
    def test_create_notification(self):
        """Test notification creation"""
        notification = NotificationService.create_notification(
            store=self.store,
            notification_type='order.created',
            title='Order Created',
            message='Your order has been created',
            user=self.user
        )
        
        self.assertEqual(notification.notification_type, 'order.created')
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.status, 'pending')
    
    def test_mark_as_read(self):
        """Test marking notification as read"""
        notification = Notification.objects.create(
            store=self.store,
            notification_type='order.created',
            title='Order Created',
            message='Your order has been created',
            user=self.user
        )
        
        notification.mark_as_read()
        
        self.assertEqual(notification.status, 'read')
        self.assertIsNotNone(notification.read_at)
```

---

## 🔗 Integration Rules

### **Required Integrations**
- **smtp.md**: Email channel implementation
- **accounts.md**: User authentication and preferences
- **stores.md**: Store scoping
- **logs.md**: Activity logging
- **core.md**: TenantModel and TenantViewSet

### **Integration Examples**
```python
# Integration with ecommerce.md for order notifications
from signals import order_created

@receiver(order_created)
def send_order_notifications(sender, instance, **kwargs):
    """Send notifications on order creation"""
    NotificationService.create_notification(
        store=instance.store,
        notification_type='order.created',
        title='Order Created',
        message=f'Your order #{instance.order_number} has been created',
        user=instance.customer.user,
        channels=['email', 'in_app'],
        metadata={
            'order_id': instance.id,
            'order_number': instance.order_number,
            'total': float(instance.total)
        }
    )

# Integration with forms.md for form submissions
from signals import form_submitted

@receiver(form_submitted)
def send_form_notifications(sender, instance, **kwargs):
    """Send notifications on form submission"""
    NotificationService.create_notification(
        store=instance.form_template.store,
        notification_type='form.submitted',
        title='Form Submitted',
        message=f'New form submission: {instance.form_template.title}',
        channels=['email', 'in_app'],
        metadata={
            'form_id': instance.form_template.form_id,
            'submission_id': instance.id
        }
    )
```

---

## 📈 Notification Types Reference

### **Ecommerce Notifications**
- `order.created` - New order created
- `order.shipped` - Order shipped
- `order.delivered` - Order delivered
- `payment.received` - Payment received
- `product.low_stock` - Product low stock warning
- `product.out_of_stock` - Product out of stock

### **Content Notifications**
- `page.published` - Page published
- `post.published` - Blog post published
- `comment.added` - Comment added

### **User Notifications**
- `user.registered` - New user registered
- `password.reset` - Password reset requested
- `email.verified` - Email verified

### **System Notifications**
- `system.alert` - System alert
- `digest` - Daily digest
- `custom` - Custom notification

---

## 🚀 Deployment Notes

### **Required Dependencies**
```python
# requirements.txt
celery>=5.3.0
```

### **Celery Configuration**
```python
# settings.py
CELERY_BEAT_SCHEDULE = {
    'cleanup-notifications': {
        'task': 'apps.notifications.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'send-digest-notifications': {
        'task': 'apps.notifications.tasks.send_digest_notifications',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
}
```

### **Monitoring**
- Monitor notification delivery success rates
- Track channel-specific failures
- Alert on high failure rates
- Monitor queue sizes

---

## 📚 Best Practices

1. **Always use async sending** - Never block on notification delivery
2. **Respect user preferences** - Honor opt-out requests
3. **Validate all content** - Prevent injection attacks
4. **Log all deliveries** - Maintain audit trail
5. **Rate limit endpoints** - Prevent abuse
6. **Clean up old records** - Prevent table bloat
7. **Monitor performance** - Track delivery times and success rates
8. **Provide clear messages** - Help users understand notifications
9. **Use templates** - Ensure consistent messaging
10. **Support digest mode** - Reduce notification fatigue

---

## 🔧 Management Commands

### **Cleanup Old Notifications**
```bash
python manage.py cleanup_notifications --days=90
```

### **Send Digest Notifications**
```bash
python manage.py send_digest
```

---

## 📝 API Documentation

### **Base URL**
```
/v2/api/notifications/
```

### **Endpoints**

#### Notifications
- `GET /v2/api/notifications/` - List notifications
- `POST /v2/api/notifications/` - Create notification
- `GET /v2/api/notifications/{id}/` - Get notification details
- `POST /v2/api/notifications/{id}/mark_read/` - Mark as read
- `POST /v2/api/notifications/{id}/resend/` - Resend notification

#### Notification Preferences
- `GET /v2/api/notification-preferences/` - List preferences
- `POST /v2/api/notification-preferences/` - Create preference
- `GET /v2/api/notification-preferences/{id}/` - Get preference details
- `PUT /v2/api/notification-preferences/{id}/` - Update preference

---

## 🎯 Implementation Checklist

- [ ] Create Notification, NotificationPreference, NotificationTemplate models
- [ ] Implement NotificationService
- [ ] Create channel implementations (Email, In-App, Push, SMS)
- [ ] Create Celery tasks for async sending
- [ ] Create API endpoints (NotificationViewSet, NotificationPreferenceViewSet)
- [ ] Add admin interface
- [ ] Implement notification preferences
- [ ] Add digest functionality
- [ ] Create tests (models, services, channels)
- [ ] Add monitoring and logging
- [ ] Implement cleanup tasks
- [ ] Create management commands
- [ ] Add integration examples
- [ ] Document notification types

---

## 📖 Version History

- **v1.0** - Initial version with multi-channel notification support
