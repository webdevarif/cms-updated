"""
Admin configuration for translations module.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Language, TranslationKey, Translation


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    """Admin for Language"""
    list_display = ['code', 'name', 'is_active', 'is_default']
    list_filter = ['is_active', 'is_default']
    search_fields = ['code', 'name']


@admin.register(TranslationKey)
class TranslationKeyAdmin(admin.ModelAdmin):
    """Admin for TranslationKey"""
    list_display = ['key', 'namespace', 'content_type', 'plural_form', 'translation_count']
    list_filter = ['namespace', 'content_type', 'plural_form']
    search_fields = ['key', 'description']
    
    def translation_count(self, obj):
        return obj.translations.count()
    translation_count.short_description = 'Translations'


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    """Admin for Translation"""
    list_display = ['key', 'language', 'store', 'preview_text', 'is_auto_translated', 'needs_review']
    list_filter = ['language', 'store', 'is_auto_translated', 'needs_review']
    search_fields = ['key__key', 'text']
    
    def preview_text(self, obj):
        return obj.text[:100] + ('...' if len(obj.text) > 100 else '')
    preview_text.short_description = 'Text Preview'
