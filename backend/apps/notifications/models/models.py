"""
Models for notifications app.
"""

from core.models import TenantModel
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class NotificationType(models.TextChoices):
    """Predefined notification types"""

    ORDER_CREATED = "order.created", "Order Created"
    ORDER_SHIPPED = "order.shipped", "Order Shipped"
    ORDER_DELIVERED = "order.delivered", "Order Delivered"
    PAYMENT_RECEIVED = "payment.received", "Payment Received"
    PRODUCT_LOW_STOCK = "product.low_stock", "Product Low Stock"
    PRODUCT_OUT_OF_STOCK = "product.out_of_stock", "Product Out of Stock"
    FORM_SUBMITTED = "form.submitted", "Form Submitted"
    USER_REGISTERED = "user.registered", "User Registered"
    SYSTEM_ALERT = "system.alert", "System Alert"
    COMMENT_APPROVED = "comment.approved", "Comment Approved"
    COMMENT_REJECTED = "comment.rejected", "Comment Rejected"
    REVIEW_APPROVED = "review.approved", "Review Approved"
    REVIEW_REJECTED = "review.rejected", "Review Rejected"
    CUSTOM = "custom", "Custom Notification"


class NotificationChannel(models.TextChoices):
    """Available notification channels"""

    EMAIL = "email", "Email"
    IN_APP = "in_app", "In-App"
    PUSH = "push", "Push"
    SMS = "sms", "SMS"


class NotificationStatus(models.TextChoices):
    """Notification delivery status"""

    PENDING = "pending", "Pending"
    SENT = "sent", "Sent"
    DELIVERED = "delivered", "Delivered"
    FAILED = "failed", "Failed"
    READ = "read", "Read"


class Notification(TenantModel):
    """
    Store-scoped notification for multi-channel delivery
    """

    # Core fields
    notification_type = models.CharField(
        max_length=50, choices=NotificationType.choices, db_index=True
    )
    title = models.CharField(max_length=255)
    message = models.TextField()

    # Relationships
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )

    # Targeting
    target_type = models.CharField(
        max_length=50,
        choices=[
            ("user", "User"),
            ("role", "Role"),
            ("store", "Store"),
            ("all", "All"),
        ],
        default="user",
    )
    target_id = models.CharField(max_length=100, blank=True)

    # Channels
    channels = models.JSONField(
        default=list, help_text="List of channels to send notification through"
    )

    # Status
    status = models.CharField(max_length=20, choices=NotificationStatus.choices, default="pending")

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
        db_table = "notifications_notification"
        indexes = [
            models.Index(fields=["store", "user", "status"]),
            models.Index(fields=["notification_type"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.email if self.user else 'No user'}"

    def mark_as_read(self):
        """Mark notification as read"""
        if self.status != "read":
            self.status = "read"
            self.read_at = timezone.now()
            self.save(update_fields=["status", "read_at"])

    def is_delivered(self):
        """Check if notification is delivered"""
        return self.status in ["delivered", "read"]

    def should_send_via_channel(self, channel):
        """Check if notification should be sent via specific channel"""
        return channel in self.channels


class NotificationPreference(TenantModel):
    """
    User notification preferences per channel and type
    """

    # Relationships
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notification_preferences"
    )

    # Preferences
    notification_type = models.CharField(max_length=50, choices=NotificationType.choices)
    channel_preferences = models.JSONField(
        default=dict,
        help_text="Channel preferences: {email: true, in_app: true, push: false, sms: false}",
    )

    # Digest settings
    digest_enabled = models.BooleanField(default=False)
    digest_frequency = models.CharField(
        max_length=20,
        choices=[
            ("immediate", "Immediate"),
            ("hourly", "Hourly"),
            ("daily", "Daily"),
            ("weekly", "Weekly"),
        ],
        default="immediate",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = "notifications_preference"
        unique_together = [["store", "user", "notification_type"]]
        ordering = ["user", "notification_type"]

    def __str__(self):
        return f"{self.user.email} - {self.notification_type}"

    def is_channel_enabled(self, channel):
        """Check if channel is enabled for this notification type"""
        return self.channel_preferences.get(channel, True)


class NotificationTemplate(TenantModel):
    """
    Reusable notification templates
    """

    # Core fields
    name = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=50, choices=NotificationType.choices)

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
        default=dict, help_text="Available variables and their descriptions"
    )

    # Status
    is_active = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = "notifications_template"
        unique_together = [["store", "notification_type", "name"]]
        ordering = ["notification_type", "name"]

    def __str__(self):
        return f"{self.name} - {self.notification_type}"

    def render(self, context):
        """Render template with context variables"""
        from django.template import Context, Template

        def render_template(template_string):
            template = Template(template_string)
            return template.render(Context(context))

        return {
            "title": render_template(self.title_template),
            "message": render_template(self.message_template),
            "email_subject": (
                render_template(self.email_subject_template)
                if self.email_subject_template
                else None
            ),
            "email_body": (
                render_template(self.email_body_template) if self.email_body_template else None
            ),
            "push_title": (
                render_template(self.push_title_template) if self.push_title_template else None
            ),
            "push_body": (
                render_template(self.push_body_template) if self.push_body_template else None
            ),
            "sms": render_template(self.sms_template) if self.sms_template else None,
        }
