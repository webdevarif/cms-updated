"""Django admin bindings for metafields."""
from django.contrib import admin

from .models import Metafield, MetafieldDefinition


@admin.register(MetafieldDefinition)
class MetafieldDefinitionAdmin(admin.ModelAdmin):
    list_display = ("store", "namespace", "key", "type", "created_at")
    search_fields = ("namespace", "key", "name")
    list_filter = ("store", "type")


@admin.register(Metafield)
class MetafieldAdmin(admin.ModelAdmin):
    list_display = ("store", "definition", "content_type", "object_id")
    search_fields = ("definition__namespace", "definition__key", "object_id")
    list_filter = ("content_type",)
