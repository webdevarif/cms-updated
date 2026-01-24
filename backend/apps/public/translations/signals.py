"""
Signals for translations module.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Translation, TranslationKey
from .tasks import invalidate_translation_on_update
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Translation)
def invalidate_cache_on_translation_save(sender, instance, **kwargs):
    """Invalidate cache when translation is saved"""
    # The cache invalidation is handled in the model's save method
    # This signal can be used for additional logic if needed
    logger.info(f"Translation saved: {instance.key} for language {instance.language.code}")
    
    # Add any additional post-save logic here
    # For example: notify translation services, update search indexes, etc.


@receiver(post_delete, sender=Translation)
def invalidate_cache_on_translation_delete(sender, instance, **kwargs):
    """Invalidate cache when translation is deleted"""
    try:
        from django.core.cache import caches
        cache = caches['translations']
        
        # Invalidate specific translation cache
        cache_key = f"trans:{instance.store.id if instance.store else 'global'}:{instance.language.code}:{instance.key.key}"
        cache.delete(cache_key)
        
        logger.info(f"Invalidated cache for deleted translation {instance.id}")
        
    except Exception as exc:
        logger.error(f"Translation cache invalidation failed on delete: {exc}")


@receiver(post_save, sender=TranslationKey)
def handle_translation_key_update(sender, instance, created, **kwargs):
    """Handle translation key updates"""
    if not created:
        # Invalidate all translations for this key when key is updated
        try:
            from .tasks import clear_translation_cache
            # Clear cache for all languages for this key
            for translation in instance.translations.all():
                clear_translation_cache.delay(
                    store_id=translation.store.id if translation.store else None,
                    language_code=translation.language.code
                )
        except Exception as exc:
            logger.error(f"Failed to invalidate cache for translation key update: {exc}")


@receiver(post_delete, sender=TranslationKey)
def handle_translation_key_delete(sender, instance, **kwargs):
    """Handle translation key deletion"""
    try:
        from .tasks import clear_translation_cache
        # Clear all related translations cache
        for translation in instance.translations.all():
            clear_translation_cache.delay(
                store_id=translation.store.id if translation.store else None,
                language_code=translation.language.code
            )
    except Exception as exc:
        logger.error(f"Failed to invalidate cache for translation key delete: {exc}")
