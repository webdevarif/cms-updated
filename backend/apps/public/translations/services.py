"""
Services for translations module.
"""
from django.db import transaction
from django.core.cache import caches
import logging
import hashlib

logger = logging.getLogger(__name__)


class TranslationService:
    """Core service for translation operations"""
    
    @staticmethod
    def get_cache_key(store_id, language_code, content_hash):
        """Generate cache key for translations"""
        return f"trans:{store_id or 'global'}:{language_code}:{content_hash}"
    
    @staticmethod
    @transaction.atomic
    def create_translation(key, language_code, text, store=None, namespace='default', content_type='plain', plural_form='none'):
        """Create or update a translation"""
        from .models import TranslationKey, Translation, Language
        
        # Get or create translation key
        trans_key, created = TranslationKey.objects.get_or_create(
            key=key,
            defaults={
                'namespace': namespace,
                'content_type': content_type,
                'plural_form': plural_form
            }
        )
        
        # Get or create language
        language = Language.objects.get(code=language_code)
        
        # Create or update translation
        translation, created = Translation.objects.update_or_create(
            key=trans_key,
            language=language,
            store=store,
            defaults={'text': text}
        )
        
        return translation
    
    @staticmethod
    def get_translation(store, key, language_code='en'):
        """
        Get translation for a key in a specific language
        
        Args:
            store: Store instance
            key: Translation key
            language_code: Language code (default: 'en')
            
        Returns:
            str: Translated text
        """
        from apps.cache.services import CacheService
        from ..models import Translation
        
        # Build cache key
        cache_key = f"{language_code}:{key}"
        
        # Try cache first
        cached = CacheService.get(store, 'translations', 'translation', cache_key)
        if cached is not None:
            logger.debug(f"Cache HIT for translation {cache_key} in store {store.slug}")
            return cached
        
        # Fetch from database
        try:
            translation = Translation.objects.get(
                store=store,
                language__code=language_code,
                translation_key__key=key
            )
        except Translation.DoesNotExist:
            # Try fallback language if specified
            fallback_language = getattr(store, 'default_language', 'en')
            if fallback_language != language_code:
                try:
                    translation = Translation.objects.get(
                        store=store,
                        language__code=fallback_language,
                        translation_key__key=key
                    )
                except Translation.DoesNotExist:
                    return key  # Return key as fallback
            else:
                return key
        
        # Cache the result
        CacheService.set(store, 'translations', 'translation', cache_key, translation.text, timeout=86400)
        logger.debug(f"Cached translation {cache_key} for store {store.slug}")
        
        return translation.text
    
    @staticmethod
    def get_translations_by_language(store, language_code):
        """
        Get all translations for a language with caching
        """
        from apps.cache.services import CacheService
        from ..models import Translation
        
        # Try cache first
        cache_key = f"translations_by_language_{language_code}"
        cached = CacheService.get_json(store, 'translations', cache_key, 'all')
        if cached:
            logger.debug(f"Cache HIT for translations by language {language_code} in store {store.slug}")
            return cached
        
        # Fetch from database
        translations = Translation.objects.filter(
            store=store,
            language__code=language_code
        ).select_related('translation_key')
        
        # Build translation data
        data = {}
        for translation in translations:
            data[translation.translation_key.key] = translation.text
        
        # Cache the result
        CacheService.cache_json(store, 'translations', cache_key, 'all', data, timeout=86400)
        logger.debug(f"Cached translations by language {language_code} for store {store.slug}")
        
        return data
        return trans_key
    
    @staticmethod
    def bulk_create_translations(translations_data, store=None):
        """Bulk create translations for better performance"""
        from .models import TranslationKey, Translation, Language
        
        created_translations = []
        
        with transaction.atomic():
            for item in translations_data:
                # Get or create language
                language, _ = Language.objects.get_or_create(
                    code=item['language_code'],
                    defaults={'name': item.get('language_name', item['language_code'])}
                )
                
                # Get or create translation key
                key, _ = TranslationKey.objects.get_or_create(
                    key=item['key'],
                    defaults={
                        'namespace': item.get('namespace', 'default'),
                        'content_type': item.get('content_type', 'plain'),
                        'plural_form': item.get('plural_form', 'none'),
                        'description': item.get('description', '')
                    }
                )
                
                # Create or update translation
                translation, _ = Translation.objects.update_or_create(
                    key=key,
                    language=language,
                    store=store,
                    defaults={'text': item['text']}
                )
                
                created_translations.append(translation)
        
        # Invalidate cache
        TranslationService.invalidate_translation_cache(store)
        
        return created_translations
    
    @staticmethod
    def import_translations(translations_data, store):
        """Import translations from data (legacy method)"""
        return TranslationService.bulk_create_translations(translations_data, store)
    
    @staticmethod
    def translate_text(text, language_code, store=None):
        """Translate a piece of text using the translation system"""
        if not text or not text.strip():
            return text
        
        # Generate a key from the text
        key = f"auto.{hash(text)}"
        
        # Get or create translation key
        TranslationService.get_or_create_translation_key(
            key=key,
            namespace='auto',
            content_type='plain',
            description='Auto-generated translation key'
        )
        
        # Get translation
        return TranslationService.get_translation(key, language_code, store, text)
