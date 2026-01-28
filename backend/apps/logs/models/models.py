"""
Models for logs app.
"""
from core.models import TenantModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class LogEntry(TenantModel):
    """Store-scoped unified log entry for all events"""

    EVENT_TYPES = [
        # System
        ("SYSTEM_STARTUP", "System Startup"),
        ("SYSTEM_ERROR", "System Error"),
        # User actions
        ("USER_LOGIN", "User Login"),
        ("USER_LOGOUT", "User Logout"),
        ("USER_REGISTER", "User Registration"),
        ("PASSWORD_CHANGE", "Password Change"),
        ("PASSWORD_RESET", "Password Reset"),
        # Content actions
        ("CONTENT_CREATE", "Content Created"),
        ("CONTENT_UPDATE", "Content Updated"),
        ("CONTENT_DELETE", "Content Deleted"),
        ("CONTENT_PUBLISH", "Content Published"),
        # Visitor analytics
        ("PAGE_VIEW", "Page View"),
        ("CLICK", "Click Event"),
        ("FORM_SUBMIT", "Form Submit"),
        ("FILE_DOWNLOAD", "File Download"),
        ("BOUNCE", "Bounce (quick exit)"),
        # Security
        ("LOGIN_FAILED", "Failed Login"),
        ("SUSPICIOUS_ACTIVITY", "Suspicious Activity"),
        ("RATE_LIMIT", "Rate Limit Exceeded"),
        ("BLOCKED_IP", "IP Blocked"),
        # Email
        ("EMAIL_SEND_ATTEMPT", "Email Send Attempt"),
        ("EMAIL_SEND_SUCCESS", "Email Send Success"),
        ("EMAIL_SEND_FAILED", "Email Send Failed"),
        ("EMAIL_OPENED", "Email Opened"),
        ("EMAIL_CLICKED", "Email Clicked"),
        # API
        ("API_CALL", "API Call"),
        ("API_ERROR", "API Error"),
    ]

    LOG_LEVELS = [
        ("DEBUG", "Debug"),
        ("INFO", "Info"),
        ("WARNING", "Warning"),
        ("ERROR", "Error"),
        ("CRITICAL", "Critical"),
    ]

    # Core fields
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    level = models.CharField(max_length=20, choices=LOG_LEVELS, default="INFO")
    message = models.TextField(blank=True)

    # User tracking
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="log_entries"
    )
    session_id = models.CharField(max_length=100, blank=True)

    # Request tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_id = models.CharField(max_length=100, blank=True)

    # Event details
    entity_type = models.CharField(max_length=100, blank=True)
    entity_id = models.PositiveIntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    # Analytics
    page_url = models.URLField(blank=True)
    referrer = models.URLField(blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    # Security
    is_suspicious = models.BooleanField(default=False)
    risk_score = models.PositiveSmallIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta(TenantModel.Meta):
        db_table = "logs_entry"
        indexes = [
            models.Index(fields=["store", "event_type", "created_at"]),
            models.Index(fields=["store", "created_at"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["session_id"]),
            models.Index(fields=["ip_address"]),
            models.Index(fields=["is_suspicious"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.store.name} - {self.event_type} - {self.created_at}"
