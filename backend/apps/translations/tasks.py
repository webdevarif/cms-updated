"""
Async tasks for translations module.
"""

import logging

from celery import shared_task
from django.core.cache import caches

from .utils import TranslationParser

logger = logging.getLogger(__name__)


@shared_task
def prewarm_translation_cache(store_id, language_code, content_hashes):
    """
    Prewarm cache for common translations
    """
    try:
        parser = TranslationParser(store_id=store_id, language_code=language_code)
        for content_hash in content_hashes:
            parser.get_cached_translation(content_hash)

        logger.info(f"Prewarmed translation cache for store {store_id}, language {language_code}")

    except Exception as exc:
        logger.error(f"Translation cache prewarming failed: {exc}")


@shared_task
def clear_translation_cache(store_id=None, language_code=None):
    """
    Clear translation cache
    """
    try:
        cache = caches["translations"]

        # Build cache key pattern
        if store_id and language_code:
            pattern = f"trans:{store_id}:{language_code}:*"
        elif store_id:
            pattern = f"trans:{store_id}:*"
        elif language_code:
            pattern = f"trans:*:{language_code}:*"
        else:
            pattern = "trans:*"

        # Use Redis client to delete by pattern
        try:
            from django_redis import get_redis_connection

            redis_conn = get_redis_connection("translations")

            # Find all keys matching pattern
            keys = redis_conn.keys(pattern)
            if keys:
                redis_conn.delete(*keys)
                logger.info(
                    f"Cleared {len(keys)} translation cache entries with pattern: {pattern}"
                )
            else:
                logger.info(f"No translation cache entries found for pattern: {pattern}")

        except Exception as redis_error:
            logger.error(f"Redis error when clearing cache: {redis_error}")
            # Fallback: try Django cache clear (less efficient)
            if store_id and language_code:
                cache.delete(f"trans:{store_id}:{language_code}:*")
            elif store_id:
                cache.delete(f"trans:{store_id}:*")
            elif language_code:
                cache.delete(f"trans:*:{language_code}:*")
            else:
                cache.delete("trans:*")

    except Exception as exc:
        logger.error(f"Translation cache clearing failed: {exc}")


@shared_task
def warm_store_translations(store_id):
    """
    Warm translation cache for a store
    """
    try:
        from .models import Language, Translation

        # Get all translations for the store
        translations = Translation.objects.filter(store_id=store_id).select_related(
            "key", "language"
        )

        cache = caches["translations"]
        warmed_count = 0

        for translation in translations:
            cache_key = f"trans:{store_id}:{translation.language.code}:{translation.key.key}"
            cache.set(cache_key, translation.text, timeout=3600)
            warmed_count += 1

        logger.info(f"Warmed {warmed_count} translations for store {store_id}")

    except Exception as exc:
        logger.error(f"Store translation warming failed: {exc}")


@shared_task
def invalidate_translation_on_update(translation_id):
    """
    Invalidate cache when translation is updated
    """
    try:
        from .models import Translation

        translation = Translation.objects.get(id=translation_id)
        cache = caches["translations"]

        # Invalidate specific translation cache
        cache_key = f"trans:{translation.store.id if translation.store else 'global'}:{translation.language.code}:{translation.key.key}"
        cache.delete(cache_key)

        logger.info(f"Invalidated cache for translation {translation_id}")

    except Exception as exc:
        logger.error(f"Translation cache invalidation failed: {exc}")
