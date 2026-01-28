"""
Admin configuration for logs app.
"""
from django.contrib import admin

from .models import LogEntry


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    """Admin interface for LogEntry model"""

    list_display = [
        "store",
        "event_type",
        "level",
        "user",
        "ip_address",
        "is_suspicious",
        "created_at",
    ]
    list_filter = ["event_type", "level", "is_suspicious", "created_at"]
    search_fields = ["message", "ip_address", "request_id"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("Event Information", {"fields": ("event_type", "level", "message")}),
        (
            "User & Request",
            {"fields": ("user", "session_id", "ip_address", "user_agent", "request_id")},
        ),
        ("Event Details", {"fields": ("entity_type", "entity_id", "metadata")}),
        ("Analytics", {"fields": ("page_url", "referrer", "duration_ms")}),
        ("Security", {"fields": ("is_suspicious", "risk_score")}),
        ("Timestamps", {"fields": ("created_at",)}),
    )
