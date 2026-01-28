"""
Admin configuration for entities app.
"""
from django.contrib import admin

from .models import EntityAction, EntityInteraction


@admin.register(EntityAction)
class EntityActionAdmin(admin.ModelAdmin):
    """Admin interface for EntityAction model"""

    list_display = ["name", "slug", "action_type", "is_active", "is_public", "store"]
    list_filter = ["action_type", "is_active", "is_public"]
    search_fields = ["name", "slug"]


@admin.register(EntityInteraction)
class EntityInteractionAdmin(admin.ModelAdmin):
    """Admin interface for EntityInteraction model"""

    list_display = ["user", "action", "content_type", "object_id", "is_active", "created_at"]
    list_filter = ["action", "is_active"]
    search_fields = ["user__email"]
    readonly_fields = ["created_at", "updated_at"]
