"""
Admin configuration for stores app.
"""
from django.contrib import admin

from .models import Store, StoreSettings


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    """Admin interface for Store model"""

    list_display = ["name", "slug", "owner", "status", "store_type", "domain", "created_at"]
    list_filter = ["status", "store_type", "created_at"]
    search_fields = ["name", "slug", "owner__email", "domain"]
    readonly_fields = ["access_code", "verification_token", "created_at", "updated_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        (None, {"fields": ("name", "slug", "description", "owner")}),
        ("Status & Type", {"fields": ("status", "store_type")}),
        ("Access & Security", {"fields": ("access_code", "verification_token")}),
        ("Enhanced Features", {"fields": ("domain", "logo", "favicon")}),
        ("SEO", {"fields": ("meta_title", "meta_description", "meta_keywords")}),
        ("Analytics", {"fields": ("google_analytics_id", "facebook_pixel_id")}),
        ("Timestamps", {"fields": ("created_at", "updated_at", "last_accessed")}),
    )


@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin):
    """Admin interface for StoreSettings model"""

    list_display = ["store", "site_name", "currency", "timezone", "language"]
    list_filter = ["currency", "timezone", "language"]
    search_fields = ["store__name", "site_name", "contact_email"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (None, {"fields": ("store", "site_name", "site_description")}),
        ("Contact", {"fields": ("contact_email", "phone")}),
        ("Address", {"fields": ("address", "city", "state", "country", "postal_code")}),
        ("Currency & Locale", {"fields": ("currency", "timezone", "language")}),
        (
            "E-commerce Settings",
            {"fields": ("tax_rate", "shipping_enabled", "free_shipping_threshold")},
        ),
        ("Advanced Settings", {"fields": ("custom_settings",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
