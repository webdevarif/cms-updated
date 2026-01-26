"""
Admin configuration for search module.
"""
from django.contrib import admin
from .models import SearchIndex, SearchDocument


@admin.register(SearchIndex)
class SearchIndexAdmin(admin.ModelAdmin):
    """Admin for SearchIndex"""
    list_display = ['name', 'index_name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(SearchDocument)
class SearchDocumentAdmin(admin.ModelAdmin):
    """Admin for SearchDocument"""
    list_display = ['title', 'search_index', 'is_indexed']
    list_filter = ['is_indexed']
    search_fields = ['title']
