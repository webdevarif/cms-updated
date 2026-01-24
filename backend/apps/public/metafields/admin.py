"""
Admin configuration for metafields module.
"""
from django.contrib import admin
from .models import MetafieldDefinition, Metafield


@admin.register(MetafieldDefinition)
class MetafieldDefinitionAdmin(admin.ModelAdmin):
    """Admin for MetafieldDefinition"""
    list_display = ['name', 'namespace', 'key', 'type', 'is_required', 'is_visible']
    list_filter = ['type', 'is_required', 'is_visible', 'is_filterable', 'is_sortable']
    search_fields = ['name', 'namespace', 'key']


@admin.register(Metafield)
class MetafieldAdmin(admin.ModelAdmin):
    """Admin for Metafield"""
    list_display = ['definition', 'content_type', 'object_id']
    list_filter = ['definition__type']
