"""
Admin configuration for notifications app.
"""
from django.contrib import admin

from .models import Notification, NotificationPreference, NotificationTemplate


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model"""

    list_display = ["title", "notification_type", "user", "status", "store", "created_at"]
    list_filter = ["status", "notification_type", "store"]
    search_fields = ["title", "message"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for NotificationPreference model"""

    list_display = ["user", "notification_type", "digest_enabled", "digest_frequency", "store"]
    list_filter = ["digest_enabled", "digest_frequency", "notification_type"]
    search_fields = ["user__email"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """Admin interface for NotificationTemplate model"""

    list_display = ["name", "notification_type", "is_active", "store"]
    list_filter = ["is_active", "notification_type"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at"]
