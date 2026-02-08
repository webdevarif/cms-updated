from django.contrib import admin

from .models import ColorScheme, Layout, StyleClass, Template, Theme


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ["name", "key", "store", "is_default", "created_at", "updated_at"]
    list_filter = ["is_default", "created_at", "store"]
    search_fields = ["name", "key", "description"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("store", "name", "key", "description", "is_default")}),
        ("Typography", {"fields": ("typography",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(ColorScheme)
class ColorSchemeAdmin(admin.ModelAdmin):
    list_display = ["name", "key", "theme", "is_default", "created_at", "updated_at"]
    list_filter = ["is_default", "created_at", "theme"]
    search_fields = ["name", "key", "theme__name"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("theme", "name", "key", "is_default")}),
        ("Colors", {"fields": ("colors", "dark_colors")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Layout)
class LayoutAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "key",
        "theme",
        "store",
        "is_default",
        "is_active",
        "created_at",
        "updated_at",
    ]
    list_filter = ["is_default", "is_active", "is_system", "created_at", "theme", "store"]
    search_fields = ["name", "key", "description", "theme__name"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("theme", "store", "name", "key", "description")}),
        ("Templates", {"fields": ("header_template", "footer_template")}),
        ("Settings", {"fields": ("content_slots", "is_default", "is_system", "is_active")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(StyleClass)
class StyleClassAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "theme", "created_at", "updated_at"]
    list_filter = ["created_at", "theme"]
    search_fields = ["name", "slug", "description", "theme__name"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("theme", "name", "slug", "description")}),
        ("CSS Properties", {"fields": ("default_css", "light_css", "dark_css")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "key",
        "template_role",
        "content_type",
        "theme",
        "is_active",
        "created_at",
        "updated_at",
    ]
    list_filter = ["template_role", "content_type", "is_active", "created_at", "theme"]
    search_fields = ["name", "key", "theme__name"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("theme", "name", "key", "template_role")}),
        ("Content", {"fields": ("content", "content_type", "is_active")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
