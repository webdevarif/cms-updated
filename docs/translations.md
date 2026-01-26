# Translation System Rules

## 1. Overview

This document outlines the backend-driven translation system for DFCMS, enabling multi-language support across all store content with a focus on:

- Backend-only translation processing
- HTML content support with XSS protection
- Store-specific language defaults
- High performance with Redis caching
- Admin UI for translation management

## 2. Core Components

### 2.1 Models

```python
# translations/models.py
from django.db import models
from django.conf import settings
import bleach

class Language(models.Model):
    """Supported languages in the system"""
    code = models.CharField(max_length=10, unique=True)  # ISO 639-1
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TranslationKey(models.Model):
    """Translation keys with metadata"""
    key = models.CharField(max_length=255, unique=True, db_index=True)
    namespace = models.CharField(max_length=100, db_index=True, default='default')
    description = models.TextField(blank=True)
    content_type = models.CharField(
        max_length=20,
        choices=[('plain', 'Plain Text'), ('html', 'HTML Content')],
        default='plain'
    )
    plural_form = models.CharField(
        max_length=10,
        choices=[
            ('none', 'Not pluralizable'),
            ('en', 'English (1 item/2 items)'),
            ('ar', 'Arabic (complex forms)')
        ],
        default='none'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Translation(models.Model):
    """Actual translations"""
    key = models.ForeignKey(TranslationKey, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    is_auto_translated = models.BooleanField(default=False)
    needs_review = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['key', 'language', 'store']]
```

### 2.2 Translation Parser

```python
# translations/utils/translation_parser.py
import hashlib
import bleach
from bs4 import BeautifulSoup, NavigableString
from django.conf import settings
from django.core.cache import caches

class TranslationParser:
    """Parses and translates HTML content"""
    
    def __init__(self, store=None, language_code=None, user=None):
        self.store = store
        self.language_code = language_code or settings.LANGUAGE_CODE
        self.user = user
        self.cache = caches['translations']
        
    def parse_html(self, html_content, cache_key=None):
        """Parse and translate HTML content with caching"""
        if not html_content:
            return html_content
            
        if not cache_key and self.store:
            cache_key = self._generate_cache_key(html_content)
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached
                
        soup = BeautifulSoup(html_content, 'html.parser')
        self._process_nodes(soup)
        
        result = str(soup)
        if cache_key:
            self.cache.set(cache_key, result, timeout=3600)
            
        return result
    
    def _process_nodes(self, soup):
        """Process all translatable nodes"""
        for text_node in self._find_translatable_text_nodes(soup):
            self._process_text_node(text_node)
            
        for tag in soup.find_all(attrs=True):
            self._process_attributes(tag)
    
    def _process_text_node(self, text_node):
        """Process a single text node with XSS protection"""
        original = text_node.string.strip()
        if not original or len(original) < 2:
            return
            
        # Sanitize HTML content
        if '<' in original:
            original = bleach.clean(
                original,
                tags=settings.BLEACH_ALLOWED_TAGS,
                attributes=settings.BLEACH_ALLOWED_ATTRIBUTES
            )
        
        # Get or create translation key
        key = self._get_or_create_key(original)
        
        # Get translation
        translation = self._get_translation(key, original)
        if translation and translation.text != original:
            text_node.replace_with(translation.text)
    
    # ... (other helper methods)
```

## 3. Middleware

```python
# translations/middleware.py
from django.utils import translation
from django.conf import settings
import re

class TranslationMiddleware:
    """Handles request/response translation"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.ignore_paths = [
            r'^/admin/', r'^/static/', r'^/media/', r'^/api/',
            r'\.(js|css|jpg|jpeg|png|gif|ico|svg|woff|ttf|eot|webp|mp4|webm|mp3|wav|ogg|json|xml|csv)$'
        ]
    
    def __call__(self, request):
        # Set language from request
        self.set_language(request)
        
        # Process response
        response = self.get_response(request)
        
        # Skip translation for certain paths/content types
        if self.should_skip_translation(request, response):
            return response
            
        # Parse and translate response
        return self.translate_response(request, response)
    
    def set_language(self, request):
        """Set language from request"""
        language = self.get_language_from_request(request)
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
    
    def get_language_from_request(self, request):
        """Get language with store fallback"""
        # 1. URL parameter
        if 'lang' in request.GET:
            return request.GET['lang']
            
        # 2. Session
        if hasattr(request, 'session') and 'django_language' in request.session:
            return request.session['django_language']
            
        # 3. Store default
        store = getattr(request, 'store', None)
        if store and hasattr(store, 'default_language') and store.default_language:
            return store.default_language.code
            
        # 4. Accept-Language header
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            try:
                return translation.get_supported_language_variant(
                    request.META['HTTP_ACCEPT_LANGUAGE'].split(',')[0].split(';')[0].strip()
                )
            except LookupError:
                pass
                
        # 5. Default from settings
        return settings.LANGUAGE_CODE
```

## 4. Admin Integration

### 4.1 Admin Interface

```python
# translations/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import TranslationKey, Translation, Language

@admin.register(TranslationKey)
class TranslationKeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'namespace', 'content_type', 'translation_count')
    list_filter = ('namespace', 'content_type', 'plural_form')
    search_fields = ('key', 'description')
    
    def translation_count(self, obj):
        return obj.translations.count()
    translation_count.short_description = 'Translations'

@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('key', 'language', 'store', 'preview_text', 'is_auto_translated')
    list_filter = ('language', 'store', 'is_auto_translated')
    search_fields = ('key__key', 'text')
    
    def preview_text(self, obj):
        return obj.text[:100] + ('...' if len(obj.text) > 100 else '')
    preview_text.short_description = 'Text Preview'

admin.site.register(Language)
```

### 4.2 Editor Integration

1. **HTML Markup**:
   ```html
   <div data-i18n="welcome.message">Hello World</div>
   <span data-i18n-plural="items.count" data-count="5">
     {count} items
   </span>
   ```

2. **Editor Toolbar**:
   - Add "Translate" button to editor
   - On click, open translation dialog with:
     - Original text
     - Available languages
     - Translation inputs
     - Save/Cancel buttons

## 5. Caching Strategy

### 5.1 Cache Keys

```python
def get_cache_key(store_id, language_code, content_hash):
    return f"trans:{store_id or 'global'}:{language_code}:{content_hash}"
```

### 5.2 Cache Invalidation

- Invalidate on translation update
- Use cache versioning for bulk updates
- Set appropriate TTL (e.g., 1 hour)

## 6. Security

### 6.1 XSS Protection

- Always use Bleach for HTML sanitization
- Define allowed tags and attributes in settings
- Escape all user-provided content

### 6.2 Rate Limiting

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'translation': '50/hour'  # For translation API
    }
}
```

## 7. Performance Optimization

### 7.1 Caching Layers

1. **Full Page Caching**:
   - Cache entire rendered pages per language
   - Invalidate on content/translation updates

2. **Fragment Caching**:
   - Cache individual components
   - Use template fragment caching

3. **Database Query Optimization**:
   - Use `select_related` and `prefetch_related`
   - Add appropriate database indexes

### 7.2 Async Processing

```python
# tasks.py
from celery import shared_task
from .utils.translation_parser import TranslationParser

@shared_task
def prewarm_translation_cache(store_id, language_code, content_hashes):
    """Prewarm cache for common translations"""
    parser = TranslationParser(store_id=store_id, language_code=language_code)
    for content_hash in content_hashes:
        parser.get_cached_translation(content_hash)
```

## 8. Testing

### 8.1 Test Cases

```python
# tests/test_translations.py
from django.test import TestCase
from django.test.utils import override_settings
from .factories import TranslationFactory

class TranslationTests(TestCase):
    def test_html_sanitization(self):
        # Test XSS protection
        pass
        
    def test_plural_forms(self):
        # Test pluralization
        pass
        
    def test_performance(self):
        # Test with large content
        pass
```

## 9. Deployment

### 9.1 Requirements

- Redis server for caching
- Database with JSON field support
- Sufficient memory for cache

### 9.2 Monitoring

- Cache hit/miss ratios
- Translation lookup times
- Error rates
- Memory usage

## 10. Maintenance

### 10.1 Cleanup Tasks

```python
# management/commands/cleanup_translations.py
from django.core.management.base import BaseCommand
from django.db.models import Count
from ..models import TranslationKey

class Command(BaseCommand):
    help = 'Clean up unused translation keys'
    
    def handle(self, *args, **options):
        # Find and delete unused keys
        unused = TranslationKey.objects.annotate(
            trans_count=Count('translations')
        ).filter(trans_count=0)
        
        count = unused.count()
        if count > 0:
            self.stdout.write(f'Deleting {count} unused translation keys...')
            unused.delete()
            self.stdout.write(self.style.SUCCESS('Cleanup complete'))
        else:
            self.stdout.write('No unused translation keys found')
```

## 11. Best Practices

1. **Key Naming**:
   - Use dot notation: `namespace.component.key`
   - Be descriptive but concise
   - Group related keys

2. **Content Guidelines**:
   - Keep translations complete sentences when possible
   - Avoid string concatenation
   - Provide context for translators

3. **Performance**:
   - Cache aggressively
   - Use bulk operations
   - Monitor and optimize queries

## Review this final polished backend-only translation plan carefully before applying.
