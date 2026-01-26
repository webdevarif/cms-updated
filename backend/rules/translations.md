# Translations Rules v1.0

## 🎯 Purpose
[Purpose content to be added]

## 🏗️ Structure
[Structure content to be added]

## 🔧 Implementation
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

## 🔒 Permissions
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

## 🧪 Testing
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

## ⚙️ Services
[Services content to be added]

## 🔗 Dependencies
[Dependencies content to be added]

## 📋 Migration
[Migration content to be added]

## ✅ Benefits
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

---
**Version**: 1.0  
**Last Updated**: 2026-01-26
**Next Review**: 2026-02-25
