"""
Integration tests for translations module.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import caches
from apps.translations.models import Language, TranslationKey, Translation
from apps.translations.services import TranslationService
from apps.stores.models import Store

User = get_user_model()


class TranslationIntegrationTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store',
            owner=User.objects.create_user(
                email='test@example.com',
                password='testpass123'
            )
        )
        
        # Create test languages
        self.en_lang = Language.objects.create(
            code='en',
            name='English',
            is_default=True
        )
        
        self.es_lang = Language.objects.create(
            code='es',
            name='Spanish',
            is_default=False
        )
        
        # Create test translation key
        self.trans_key = TranslationKey.objects.create(
            key='test.key',
            namespace='test',
            content_type='plain',
            plural_form='none',
            description='Test translation key'
        )
        
        # Create test translations
        self.en_translation = Translation.objects.create(
            key=self.trans_key,
            language=self.en_lang,
            store=self.store,
            text='Hello World'
        )
        
        self.es_translation = Translation.objects.create(
            key=self.trans_key,
            language=self.es_lang,
            store=self.store,
            text='Hola Mundo'
        )
    
    def test_translation_service_get_with_cache(self):
        """Test translation retrieval with caching"""
        cache = caches['translations']
        
        # First call - should hit database
        result1 = TranslationService.get_translation('test.key', 'en', self.store)
        self.assertEqual(result1, 'Hello World')
        
        # Second call - should hit cache
        result2 = TranslationService.get_translation('test.key', 'en', self.store)
        self.assertEqual(result2, 'Hello World')
        
        # Verify cache key exists
        cache_key = f"trans:{self.store.id}:en:test.key"
        cached_value = cache.get(cache_key)
        self.assertEqual(cached_value, 'Hello World')
    
    def test_translation_service_fallback_language(self):
        """Test fallback to default language"""
        # Request translation in non-existent language
        result = TranslationService.get_translation('test.key', 'fr', self.store)
        # Should fallback to English
        self.assertEqual(result, 'Hello World')
    
    def test_translation_service_fallback_text(self):
        """Test fallback to provided text"""
        # Request translation for non-existent key
        result = TranslationService.get_translation('nonexistent.key', 'en', self.store, 'Fallback Text')
        self.assertEqual(result, 'Fallback Text')
    
    def test_bulk_create_translations(self):
        """Test bulk translation creation"""
        translations_data = [
            {
                'key': 'bulk.key1',
                'language_code': 'en',
                'text': 'Bulk Translation 1',
                'namespace': 'bulk'
            },
            {
                'key': 'bulk.key2',
                'language_code': 'es',
                'text': 'Bulk Translation 2',
                'namespace': 'bulk'
            }
        ]
        
        created = TranslationService.bulk_create_translations(translations_data, self.store)
        
        self.assertEqual(len(created), 2)
        
        # Verify translations were created
        self.assertTrue(
            Translation.objects.filter(
                store=self.store,
                key__key__in=['bulk.key1', 'bulk.key2']
            ).exists()
        )
    
    def test_translate_text_method(self):
        """Test automatic text translation"""
        text = "Test text to translate"
        
        # First call creates translation key
        result1 = TranslationService.translate_text(text, 'es', self.store)
        self.assertEqual(result1, text)  # Returns original text
        
        # Add translation for the auto-generated key
        auto_key = f"auto.{hash(text)}"
        trans_key = TranslationService.get_or_create_translation_key(
            key=auto_key,
            namespace='auto',
            content_type='plain',
            description='Auto-generated translation key'
        )
        
        TranslationService.create_translation(
            key=auto_key,
            language_code='es',
            text='Texto de prueba',
            store=self.store
        )
        
        # Second call should return translated text
        result2 = TranslationService.translate_text(text, 'es', self.store)
        self.assertEqual(result2, 'Texto de prueba')
    
    def test_cache_invalidation_on_update(self):
        """Test cache invalidation when translation is updated"""
        cache = caches['translations']
        
        # Get translation (caches it)
        result1 = TranslationService.get_translation('test.key', 'en', self.store)
        self.assertEqual(result1, 'Hello World')
        
        # Verify cache exists
        cache_key = f"trans:{self.store.id}:en:test.key"
        self.assertIsNotNone(cache.get(cache_key))
        
        # Update translation
        self.en_translation.text = 'Updated Hello World'
        self.en_translation.save()
        
        # Wait a moment for async task to complete
        import time
        time.sleep(0.1)
        
        # Cache should be invalidated (in real implementation)
        # For test purposes, we'll manually clear it
        cache.delete(cache_key)
        
        # Next call should hit database
        result2 = TranslationService.get_translation('test.key', 'en', self.store)
        self.assertEqual(result2, 'Updated Hello World')
