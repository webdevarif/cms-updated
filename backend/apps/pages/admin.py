"""
Pages admin configuration.
"""

from django.contrib import admin

from .models import Menu, MenuItem


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    """Menu admin configuration"""

    list_display = ["name", "slug", "store", "is_default", "created_at"]
    list_filter = ["is_default", "store", "created_at"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    date_hierarchy = "created_at"
    ordering = ["name"]

    def get_queryset(self, request):
        """Filter to store for non-superusers."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(store=request.user.stores.first())


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """Menu item admin configuration"""

    list_display = ["title", "menu", "parent", "position", "is_visible", "created_at"]
    list_filter = ["is_visible", "menu", "created_at"]
    search_fields = ["title", "url"]
    ordering = ["menu", "position", "created_at"]

    def get_queryset(self, request):
        """Filter to store for non-superusers."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(menu__store=request.user.stores.first())
