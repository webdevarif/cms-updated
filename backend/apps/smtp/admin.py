"""
Admin configuration for SMTP app.
"""
from django.contrib import admin

from .models import EmailLog, EmailTemplate, SmtpConfiguration


@admin.register(SmtpConfiguration)
class SmtpConfigurationAdmin(admin.ModelAdmin):
    """Admin interface for SmtpConfiguration model"""

    list_display = ("name", "provider", "host", "port", "is_active", "store")
    list_filter = ("provider", "is_active", "store")
    search_fields = ("name", "host", "username")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("name", "provider", "store", "is_active")}),
        (
            "SMTP Settings",
            {"fields": ("host", "port", "username", "password", "use_tls", "use_ssl")},
        ),
        ("Limits", {"fields": ("daily_limit", "hourly_limit")}),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    """Admin interface for EmailTemplate model"""

    list_display = ("name", "template_type", "subject", "is_active", "store")
    list_filter = ("template_type", "is_active", "store")
    search_fields = ("name", "subject", "html_content")
    readonly_fields = ("created_at", "updated_at")


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """Admin interface for EmailLog model"""

    list_display = ("to_email", "subject", "status", "sent_at", "store")
    list_filter = ("status", "sent_at", "store")
    search_fields = ("to_email", "subject", "message_id")
    readonly_fields = (
        "sent_at",
        "delivered_at",
        "opened_at",
        "clicked_at",
        "created_at",
        "updated_at",
    )
    date_hierarchy = "sent_at"
