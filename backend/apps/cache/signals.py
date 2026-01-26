"""
Cache invalidation signals for Digital Farmers CMS.

Automatic cache invalidation on model changes.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .services import CacheService
import logging

logger = logging.getLogger(__name__)


@receiver(post_save)
def invalidate_cache_on_save(sender, instance, **kwargs):
    """
    Invalidate cache when any model is saved
    """
    # Check if instance has store attribute for store-scoped invalidation
    if hasattr(instance, 'store'):
        store = instance.store
        
        # Get module name from sender
        module_name = sender._meta.model_name.lower()
        
        # Invalidate specific object cache
        CacheService.delete(store, module_name, 'object', str(instance.id))
        
        # Invalidate module cache for broader invalidation
        CacheService.invalidate_module(store, module_name)
        
        logger.debug(f"Invalidated cache for {module_name}:{instance.id} in store {store.slug}")
    else:
        # Global objects - invalidate all cache
        cache.clear()
        logger.debug(f"Invalidated all cache for {sender._meta.model_name}:{instance.id}")


@receiver(post_delete)
def invalidate_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate cache when any model is deleted
    """
    # Check if instance has store attribute for store-scoped invalidation
    if hasattr(instance, 'store'):
        store = instance.store
        
        # Get module name from sender
        module_name = sender._meta.model_name.lower()
        
        # Invalidate specific object cache
        CacheService.delete(store, module_name, 'object', str(instance.id))
        
        # Invalidate module cache for broader invalidation
        CacheService.invalidate_module(store, module_name)
        
        logger.debug(f"Invalidated cache for deleted {module_name}:{instance.id} in store {store.slug}")
    else:
        # Global objects - invalidate all cache
        cache.clear()
        logger.debug(f"Invalidated all cache for deleted {sender._meta.model_name}:{instance.id}")


# Specific model invalidations
@receiver(post_save, sender='posts.Post')
def invalidate_post_cache(sender, instance, **kwargs):
    """Invalidate post cache on post save"""
    if hasattr(instance, 'store'):
        store = instance.store
        
        # Invalidate specific post
        CacheService.delete(store, 'pages', 'page', str(instance.id))
        CacheService.delete(store, 'posts', 'post', str(instance.id))
        
        # Invalidate page listings
        CacheService.delete_pattern(store, 'pages:page:*')
        CacheService.delete_pattern(store, 'posts:post:*')
        
        logger.debug(f"Invalidated post cache for {instance.id} in store {store.slug}")


@receiver(post_delete, sender='posts.Post')
def invalidate_post_cache_delete(sender, instance, **kwargs):
    """Invalidate post cache on post delete"""
    if hasattr(instance, 'store'):
        store = instance.store
        
        # Invalidate specific post
        CacheService.delete(store, 'pages', 'page', str(instance.id))
        CacheService.delete(store, 'posts', 'post', str(instance.id))
        
        # Invalidate page listings
        CacheService.delete_pattern(store, 'pages:page:*')
        CacheService.delete_pattern(store, 'posts:post:*')
        
        logger.debug(f"Invalidated deleted post cache for {instance.id} in store {store.slug}")


# @receiver(post_save, sender='ecommerce.Product')
# def invalidate_product_cache(sender, instance, **kwargs):
#     """Invalidate product cache on product save"""
#     if hasattr(instance, 'store'):
#         store = instance.store
#         
#         # Invalidate specific product
#         CacheService.delete(store, 'ecommerce', 'product', str(instance.id))
#         
#         # Invalidate product listings
#         CacheService.delete_pattern(store, 'ecommerce:product:*')
#         
#         logger.debug(f"Invalidated product cache for {instance.id} in store {store.slug}")


# @receiver(post_delete, sender='ecommerce.Product')
# def invalidate_product_cache_delete(sender, instance, **kwargs):
#     """Invalidate product cache on product delete"""
#     if hasattr(instance, 'store'):
#         store = instance.store
#         
#         # Invalidate specific product
#         CacheService.delete(store, 'ecommerce', 'product', str(instance.id))
#         
#         # Invalidate product listings
#         CacheService.delete_pattern(store, 'ecommerce:product:*')
#         
#         logger.debug(f"Invalidated deleted product cache for {instance.id} in store {store.slug}")


# @receiver(post_save, sender='translations.Translation')
# def invalidate_translation_cache(sender, instance, **kwargs):
#     """Invalidate translation cache on translation save"""
#     if hasattr(instance, 'store'):
#         store = instance.store
#         
#         # Build cache key
#         cache_key = f"{instance.language.code}:{instance.translation_key.key}"
#         
#         # Invalidate specific translation
#         CacheService.delete(store, 'translations', 'translation', cache_key)
#         
#         # Invalidate translation listings
#         CacheService.delete_pattern(store, 'translations:translation:*')
#         
#         logger.debug(f"Invalidated translation cache for {cache_key} in store {store.slug}")


# @receiver(post_delete, sender='translations.Translation')
# def invalidate_translation_cache_delete(sender, instance, **kwargs):
#     """Invalidate translation cache on translation delete"""
#     if hasattr(instance, 'store'):
#         store = instance.store
#         
#         # Build cache key
#         cache_key = f"{instance.language.code}:{instance.translation_key.key}"
#         
#         # Invalidate specific translation
#         CacheService.delete(store, 'translations', 'translation', cache_key)
#         
#         # Invalidate translation listings
#         CacheService.delete_pattern(store, 'translations:translation:*')
#         
#         logger.debug(f"Invalidated deleted translation cache for {cache_key} in store {store.slug}")


@receiver(post_save, sender='stores.Store')
def invalidate_store_cache_on_save(sender, instance, **kwargs):
    """Invalidate all cache for store when store is updated"""
    # Invalidate all cache for the store
    CacheService.invalidate_store(instance)
    
    logger.debug(f"Invalidated all cache for store {instance.slug} on update")


# @receiver(post_save, sender='themes.Theme')
# def invalidate_theme_cache(sender, instance, **kwargs):
#     """Invalidate theme cache on theme save"""
#     if hasattr(instance, 'store'):
#         store = instance.store
#         
#         # Invalidate theme cache
#         CacheService.delete(store, 'themes', 'theme', str(instance.id))
#         
#         # Invalidate theme listings
#         CacheService.delete_pattern(store, 'themes:theme:*')
#         
#         # Invalidate pages that depend on theme
#         CacheService.delete_pattern(store, 'pages:page:*')
#         
#         logger.debug(f"Invalidated theme cache for {instance.id} in store {store.slug}")
