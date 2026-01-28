"""Themes admin configuration."""
from django.contrib import admin

from .models import ColorScheme, StyleClass, Template, Theme, Typography


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    """Theme admin"""

    list_display = ["name", "store", "is_active", "created_at", "updated_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-is_active", "name"]


@admin.register(ColorScheme)
class ColorSchemeAdmin(admin.ModelAdmin):
    """Color scheme admin"""

    list_display = ["name", "theme", "key", "is_default", "created_at", "updated_at"]
    list_filter = ["is_default", "theme"]
    search_fields = ["name", "key"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["name"]


@admin.register(Typography)
class TypographyAdmin(admin.ModelAdmin):
    """Typography admin"""

    list_display = ["theme", "base_font_size", "font_smoothing", "created_at", "updated_at"]
    list_filter = ["theme", "font_smoothing"]
    search_fields = ["theme__name"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["theme"]


@admin.register(StyleClass)
class StyleClassAdmin(admin.ModelAdmin):
    """Style class admin"""

    list_display = ["name", "theme", "slug", "created_at", "updated_at"]
    list_filter = ["theme"]
    search_fields = ["name", "slug"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["name"]


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    """Template admin"""

    list_display = [
        "name",
        "theme",
        "key",
        "template_role",
        "is_active",
        "created_at",
        "updated_at",
    ]
    list_filter = ["template_role", "is_active", "theme"]
    search_fields = ["name", "key", "description"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["template_role", "name"]
