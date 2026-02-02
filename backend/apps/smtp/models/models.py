"""
SMTP models for email configuration.
"""

from core.fields import EncryptedCharField
from django.db import models
from django.utils import timezone


class SmtpConfiguration(models.Model):
    """SMTP configuration for email sending"""

    # Store scoping
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE)

    # Core fields
    name = models.CharField(max_length=100)

    PROVIDER_CHOICES = [
        ("gmail", "Gmail"),
        ("outlook", "Outlook"),
        ("sendgrid", "SendGrid"),
        ("mailgun", "Mailgun"),
        ("ses", "Amazon SES"),
        ("custom", "Custom SMTP"),
    ]
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default="custom")

    # SMTP settings
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField(default=587)
    username = models.EmailField()
    password = EncryptedCharField(max_length=255)
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)

    # Limits
    daily_limit = models.PositiveIntegerField(default=1000)
    hourly_limit = models.PositiveIntegerField(default=100)

    # Status
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "smtp_configuration"
        unique_together = [["store", "name"]]
        indexes = [
            models.Index(fields=["store", "is_active"]),
            models.Index(fields=["store", "provider"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.store.name} - {self.name}"

    def get_decrypted_password(self):
        """Get decrypted password for SMTP auth"""
        return self.password


class EmailTemplate(models.Model):
    """Email templates for different email types"""

    # Store scoping
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE)

    TEMPLATE_TYPES = [
        ("password_reset", "Password Reset"),
        ("email_verification", "Email Verification"),
        ("welcome", "Welcome"),
        ("order_confirmation", "Order Confirmation"),
        ("custom", "Custom"),
    ]

    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES)
    subject = models.CharField(max_length=255)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "smtp_email_template"
        unique_together = [["store", "name"]]
        indexes = [
            models.Index(fields=["store", "template_type"]),
            models.Index(fields=["store", "is_active"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.store.name} - {self.name}"


class EmailLog(models.Model):
    """Log of sent emails with tracking"""

    # Store scoping
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE)

    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("sent", "Sent"),
        ("delivered", "Delivered"),
        ("opened", "Opened"),
        ("clicked", "Clicked"),
        ("bounced", "Bounced"),
        ("dropped", "Dropped"),
        ("failed", "Failed"),
    ]

    to_email = models.EmailField()
    subject = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued")

    # Content
    html_content = models.TextField(blank=True)
    text_content = models.TextField(blank=True)

    # Tracking
    tracking_id = models.UUIDField(unique=True, default=timezone.now)
    message_id = models.CharField(max_length=255, blank=True)
    is_tracked = models.BooleanField(default=False)

    # SMTP config
    smtp_config = models.ForeignKey(SmtpConfiguration, on_delete=models.SET_NULL, null=True)

    # Template
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True)

    # User reference
    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True)

    # Retry tracking
    retry_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "smtp_email_log"
        indexes = [
            models.Index(fields=["store", "status", "created_at"]),
            models.Index(fields=["store", "to_email"]),
            models.Index(fields=["tracking_id"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.store.name} - {self.to_email} - {self.status}"


class EmailTracking(models.Model):
    """Email tracking events"""

    # Store scoping
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE)

    EVENT_TYPES = [
        ("sent", "Sent"),
        ("delivered", "Delivered"),
        ("opened", "Opened"),
        ("clicked", "Clicked"),
        ("bounced", "Bounced"),
        ("dropped", "Dropped"),
        ("failed", "Failed"),
    ]

    email_log = models.ForeignKey(
        EmailLog, on_delete=models.CASCADE, related_name="tracking_events"
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    event_data = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "smtp_email_tracking"
        indexes = [
            models.Index(fields=["store", "event_type", "created_at"]),
            models.Index(fields=["email_log", "event_type"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email_log.to_email} - {self.event_type}"
