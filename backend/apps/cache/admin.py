"""
Admin configuration for cache module.
"""
from django.contrib import admin
from .models import CacheEntry


@admin.register(CacheEntry)
class CacheEntryAdmin(admin.ModelAdmin):
    """Admin for CacheEntry"""
    list_display = ['key', 'expires_at', 'created_at']
    list_filter = ['expires_at']
    search_fields = ['key']
    readonly_fields = ['created_at', 'updated_at']
