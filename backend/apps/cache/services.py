"""
Services for cache module.
"""
from django.core.cache import cache
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """Shared cache management service"""
    
    @staticmethod
    def get_cache_key(store, module, object_type, object_id, version='v1'):
        """
        Generate standardized cache key
        """
        return f"{store.slug}:{module}:{object_type}:{object_id}:{version}"
    
    @staticmethod
    def get(store, module, object_type, object_id, default=None):
        """
        Get value from cache
        """
        key = CacheService.get_cache_key(store, module, object_type, object_id)
        value = cache.get(key)
        
        if value is not None:
            logger.debug(f"Cache HIT: {key}")
        else:
            logger.debug(f"Cache MISS: {key}")
        
        return value
    
    @staticmethod
    def set(store, module, object_type, object_id, value, timeout=3600):
        """
        Set value in cache
        """
        key = CacheService.get_cache_key(store, module, object_type, object_id)
        cache.set(key, value, timeout)
        
        logger.debug(f"Cache SET: {key} (timeout: {timeout}s)")
        return True
    
    @staticmethod
    def delete(store, module, object_type, object_id):
        """
        Delete value from cache
        """
        key = CacheService.get_cache_key(store, module, object_type, object_id)
        cache.delete(key)
        
        logger.debug(f"Cache DELETE: {key}")
        return True
    
    @staticmethod
    def delete_pattern(store, pattern):
        """
        Delete all keys matching pattern
        """
        from django.core.cache.backends.redis import RedisCache
        
        if not isinstance(cache, RedisCache):
            logger.warning("Pattern deletion only works with Redis cache")
            return False
        
        # Get Redis client
        client = cache._client
        
        # Build pattern
        full_pattern = f"{store.slug}:{pattern}*"
        
        # Find and delete keys
        keys = client.keys(full_pattern)
        if keys:
            client.delete(*keys)
            logger.debug(f"Cache DELETE PATTERN: {full_pattern} ({len(keys)} keys)")
        
        return True
    
    @staticmethod
    def invalidate_store(store):
        """
        Invalidate all cache for a store
        """
        return CacheService.delete_pattern(store, '*')
    
    @staticmethod
    def invalidate_module(store, module):
        """
        Invalidate all cache for a module in a store
        """
        return CacheService.delete_pattern(store, f"{module}:*")
    
    @staticmethod
    def get_or_set(store, module, object_type, object_id, callback, timeout=3600):
        """
        Get value from cache or set using callback
        """
        value = CacheService.get(store, module, object_type, object_id)
        
        if value is None:
            value = callback()
            CacheService.set(store, module, object_type, object_id, value, timeout)
        
        return value
    
    @staticmethod
    def cache_json(store, module, object_type, object_id, data, timeout=3600):
        """
        Cache JSON data
        """
        key = CacheService.get_cache_key(store, module, object_type, object_id)
        cache.set(key, json.dumps(data), timeout)
        
        logger.debug(f"Cache JSON: {key}")
        return True
    
    @staticmethod
    def get_json(store, module, object_type, object_id):
        """
        Get JSON data from cache
        """
        value = CacheService.get(store, module, object_type, object_id)
        
        if value is not None:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON from cache: {key}")
                return None
        
        return None
    
    @staticmethod
    def get_cache_stats():
        """
        Get cache statistics
        """
        from django.core.cache.backends.redis import RedisCache
        
        if not isinstance(cache, RedisCache):
            return {'error': 'Only Redis cache supports stats'}
        
        client = cache._client
        info = client.info('stats')
        
        return {
            'hits': info.get('keyspace_hits', 0),
            'misses': info.get('keyspace_misses', 0),
            'hit_rate': info.get('keyspace_hits', 0) / (info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1)) * 100,
        }


class CacheWarmupService:
    """Cache warming service for store performance"""
    
    @staticmethod
    def warm_store_cache(store):
        """
        Warm cache for a store
        """
        logger.info(f"Warming cache for store: {store.slug}")
        
        # Warm pages
        CacheWarmupService._warm_pages(store)
        
        # Warm products
        CacheWarmupService._warm_products(store)
        
        # Warm translations
        CacheWarmupService._warm_translations(store)
        
        logger.info(f"Cache warming complete for store: {store.slug}")
    
    @staticmethod
    def _warm_pages(store):
        """Warm page cache"""
        from apps.posts.models import Post
        
        posts = Post.objects.filter(
            store=store,
            status='published'
        ).select_related('store')
        
        for post in posts:
            data = {
                'id': post.id,
                'title': post.title,
                'slug': post.slug,
                'content': post.content,
                'url': post.get_absolute_url()
            }
            CacheService.cache_json(store, 'pages', 'page', post.id, data, timeout=3600)
    
    @staticmethod
    def _warm_products(store):
        """Warm product cache"""
        from apps.public.ecommerce.models import Product
        
        products = Product.objects.filter(
            store=store,
            is_active=True
        ).select_related('store').prefetch_related('variants')
        
        for product in products:
            data = {
                'id': product.id,
                'title': product.title,
                'description': product.description,
                'price': float(product.base_price),
                'is_active': product.is_active
            }
            CacheService.cache_json(store, 'ecommerce', 'product', product.id, data, timeout=3600)
    
    @staticmethod
    def _warm_translations(store):
        """Warm translation cache"""
        from apps.public.translations.models import Translation
        
        translations = Translation.objects.filter(
            store=store
        ).select_related('language', 'translation_key')
        
        for translation in translations:
            key = f"{translation.language.code}:{translation.translation_key.key}"
            CacheService.set(store, 'translations', 'translation', key, translation.text, timeout=86400)
