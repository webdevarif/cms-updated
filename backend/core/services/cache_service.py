"""
Core cache service using django-redis for high-performance caching.
"""
import logging
from typing import Any, Optional

from django.core.cache import cache
from django.core.cache.backends.redis import RedisCache
from django.utils import timezone

logger = logging.getLogger(__name__)


class CacheService:
    """
    Minimal, high-performance cache service for Digital Farmers CMS.

    Uses django-redis for production-ready caching with store isolation.
    """

    @staticmethod
    def get_key(
        store_slug: str, module: str, obj_type: str, obj_id: str, version: str = "v1"
    ) -> str:
        """
        Generate standardized cache key with store isolation.

        Format: {store_slug}:{module}:{obj_type}:{obj_id}:{version}
        """
        return f"{store_slug}:{module}:{obj_type}:{obj_id}:{version}"

    @staticmethod
    def get(store_slug: str, module: str, obj_type: str, obj_id: str, default: Any = None) -> Any:
        """
        Get value from cache.
        """
        key = CacheService.get_key(store_slug, module, obj_type, obj_id)
        value = cache.get(key, default)

        if value is not None:
            logger.debug(f"Cache HIT: {key}")
        else:
            logger.debug(f"Cache MISS: {key}")

        return value

    @staticmethod
    def set(
        store_slug: str, module: str, obj_type: str, obj_id: str, value: Any, timeout: int = 3600
    ) -> bool:
        """
        Set value in cache.
        """
        key = CacheService.get_key(store_slug, module, obj_type, obj_id)
        cache.set(key, value, timeout)
        logger.debug(f"Cache SET: {key} (timeout: {timeout}s)")
        return True

    @staticmethod
    def delete(store_slug: str, module: str, obj_type: str, obj_id: str) -> bool:
        """
        Delete specific cache key.
        """
        key = CacheService.get_key(store_slug, module, obj_type, obj_id)
        cache.delete(key)
        logger.debug(f"Cache DELETE: {key}")
        return True

    @staticmethod
    def invalidate_store(store_slug: str) -> bool:
        """
        Invalidate all cache for a store using pattern deletion.
        """
        if not isinstance(cache, RedisCache):
            logger.warning("Pattern deletion only works with Redis cache")
            return False

        try:
            client = cache._client
            pattern = f"{store_slug}:*"
            keys = client.keys(pattern)

            if keys:
                client.delete(*keys)
                logger.debug(f"Cache INVALIDATE STORE: {store_slug} ({len(keys)} keys)")

            return True
        except Exception as e:
            logger.error(f"Failed to invalidate store cache: {e}")
            return False

    @staticmethod
    def invalidate_module(store_slug: str, module: str) -> bool:
        """
        Invalidate all cache for a module in a store.
        """
        if not isinstance(cache, RedisCache):
            logger.warning("Pattern deletion only works with Redis cache")
            return False

        try:
            client = cache._client
            pattern = f"{store_slug}:{module}:*"
            keys = client.keys(pattern)

            if keys:
                client.delete(*keys)
                logger.debug(f"Cache INVALIDATE MODULE: {store_slug}:{module} ({len(keys)} keys)")

            return True
        except Exception as e:
            logger.error(f"Failed to invalidate module cache: {e}")
            return False

    @staticmethod
    def get_or_set(
        store_slug: str, module: str, obj_type: str, obj_id: str, callback, timeout: int = 3600
    ) -> Any:
        """
        Get value from cache or set using callback function.
        """
        value = CacheService.get(store_slug, module, obj_type, obj_id)

        if value is None:
            value = callback()
            CacheService.set(store_slug, module, obj_type, obj_id, value, timeout)

        return value

    @staticmethod
    def cache_json(
        store_slug: str, module: str, obj_type: str, obj_id: str, data: dict, timeout: int = 3600
    ) -> bool:
        """
        Cache JSON data with automatic serialization.
        """
        import json

        key = CacheService.get_key(store_slug, module, obj_type, obj_id)
        cache.set(key, json.dumps(data), timeout)
        logger.debug(f"Cache JSON: {key}")
        return True

    @staticmethod
    def get_json(store_slug: str, module: str, obj_type: str, obj_id: str) -> Optional[dict]:
        """
        Get JSON data from cache with automatic deserialization.
        """
        import json

        value = CacheService.get(store_slug, module, obj_type, obj_id)

        if value is not None:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON from cache: {value}")
                return None

        return None

    @staticmethod
    def get_store_stats(store_slug: str) -> dict:
        """
        Get cache statistics for a specific store.
        """
        if not isinstance(cache, RedisCache):
            return {"error": "Redis cache required for statistics"}

        try:
            client = cache._client
            pattern = f"{store_slug}:*"
            keys = client.keys(pattern)

            # Calculate memory usage
            total_size = 0
            for key in keys:
                try:
                    value = client.get(key)
                    if value:
                        total_size += len(value)
                except Exception:
                    pass

            return {
                "store_slug": store_slug,
                "key_count": len(keys),
                "memory_usage_bytes": total_size,
                "memory_usage_human": CacheService._format_bytes(total_size),
                "timestamp": str(timezone.now()),
            }
        except Exception as e:
            logger.error(f"Failed to get store cache stats: {e}")
            return {"error": str(e)}

    @staticmethod
    def get_global_stats() -> dict:
        """
        Get global Redis cache statistics.
        """
        if not isinstance(cache, RedisCache):
            return {"error": "Redis cache required for statistics"}

        try:
            client = cache._client
            info = client.info()

            # Calculate hit rate
            hits = info.get("keyspace_hits", 0)
            misses = info.get("keyspace_misses", 0)
            total_requests = hits + misses
            hit_rate = (hits / total_requests * 100) if total_requests > 0 else 0

            # Memory info
            memory_info = client.info("memory")

            return {
                "hits": hits,
                "misses": misses,
                "hit_rate": round(hit_rate, 2),
                "total_requests": total_requests,
                "memory_used": memory_info.get("used_memory", 0),
                "memory_used_human": CacheService._format_bytes(memory_info.get("used_memory", 0)),
                "memory_peak": memory_info.get("used_memory_peak", 0),
                "memory_peak_human": CacheService._format_bytes(
                    memory_info.get("used_memory_peak", 0)
                ),
                "connected_clients": info.get("connected_clients", 0),
                "uptime_seconds": info.get("uptime_in_seconds", 0),
            }
        except Exception as e:
            logger.error(f"Failed to get global cache stats: {e}")
            return {"error": str(e)}

    @staticmethod
    def _format_bytes(bytes_count: int) -> str:
        """
        Format bytes in human readable format.
        """
        if bytes_count == 0:
            return "0 B"

        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0

        while bytes_count >= 1024 and unit_index < len(units) - 1:
            bytes_count /= 1024.0
            unit_index += 1

        return f"{bytes_count:.2f} {units[unit_index]}"


class CacheWarmupService:
    """
    Simple cache warming service for store performance.
    """

    @staticmethod
    def warm_store_cache(store_slug: str) -> bool:
        """
        Warm cache for a store with essential data.
        """
        logger.info(f"Warming cache for store: {store_slug}")

        try:
            # Warm pages
            CacheWarmupService._warm_pages(store_slug)

            # Warm products
            CacheWarmupService._warm_products(store_slug)

            # Warm translations
            CacheWarmupService._warm_translations(store_slug)

            logger.info(f"Cache warming complete for store: {store_slug}")
            return True

        except Exception as e:
            logger.error(f"Cache warming failed for store {store_slug}: {e}")
            return False

    @staticmethod
    def _warm_pages(store_slug: str) -> None:
        """Warm page cache"""
        try:
            from apps.posts.models import Post
            from apps.stores.models import Store

            store = Store.objects.get(slug=store_slug)
            posts = Post.objects.filter(store=store, status="published").select_related("store")

            for post in posts:
                data = {
                    "id": post.id,
                    "title": post.title,
                    "slug": post.slug,
                    "content": post.content,
                    "url": post.get_absolute_url(),
                }
                CacheService.cache_json(
                    store_slug, "pages", "page", str(post.id), data, timeout=3600
                )

        except Exception as e:
            logger.error(f"Failed to warm pages for store {store_slug}: {e}")

    @staticmethod
    def _warm_products(store_slug: str) -> None:
        """Warm product cache"""
        try:
            from apps.ecommerce.models import Product
            from apps.stores.models import Store

            store = Store.objects.get(slug=store_slug)
            products = (
                Product.objects.filter(store=store, is_active=True)
                .select_related("store")
                .prefetch_related("variants")
            )

            for product in products:
                data = {
                    "id": product.id,
                    "title": product.title,
                    "description": product.description,
                    "price": float(product.base_price),
                    "is_active": product.is_active,
                }
                CacheService.cache_json(
                    store_slug, "ecommerce", "product", str(product.id), data, timeout=3600
                )

        except Exception as e:
            logger.error(f"Failed to warm products for store {store_slug}: {e}")

    @staticmethod
    def _warm_translations(store_slug: str) -> None:
        """Warm translation cache"""
        try:
            from apps.stores.models import Store
            from apps.translations.models import Translation

            store = Store.objects.get(slug=store_slug)
            translations = Translation.objects.filter(store=store).select_related(
                "language", "translation_key"
            )

            for translation in translations:
                key = f"{translation.language.code}:{translation.translation_key.key}"
                CacheService.set(
                    store_slug, "translations", "translation", key, translation.text, timeout=86400
                )

        except Exception as e:
            logger.error(f"Failed to warm translations for store {store_slug}: {e}")
