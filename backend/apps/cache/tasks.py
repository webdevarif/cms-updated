"""
Cache management tasks for Digital Farmers CMS.

Asynchronous cache operations using Celery.
"""
from celery import shared_task
from django.core.cache import cache
from .services import CacheService, CacheWarmupService, CacheMonitor
import logging

logger = logging.getLogger(__name__)


@shared_task
def clear_cache(store_id=None, module=None):
    """
    Clear cache for store or all stores
    """
    if store_id:
        try:
            from apps.stores.models import Store
            store = Store.objects.get(id=store_id)
            
            if module:
                # Clear specific module for store
                CacheService.invalidate_module(store, module)
                logger.info(f"Cleared cache for store '{store.slug}' module '{module}'")
            else:
                # Clear all cache for store
                CacheService.invalidate_store(store)
                logger.info(f"Cleared all cache for store '{store.slug}'")
                
        except Store.DoesNotExist:
            logger.error(f"Store with id {store_id} does not exist")
    else:
        # Clear all cache
        cache.clear()
        logger.info("Cleared all cache")


@shared_task
def warm_cache(store_id):
    """
    Warm cache for a store
    """
    try:
        from apps.stores.models import Store
        store = Store.objects.get(id=store_id)
        
        CacheWarmupService.warm_store_cache(store)
        logger.info(f"Warmed cache for store '{store.slug}'")
        
    except Store.DoesNotExist:
        logger.error(f"Store with id {store_id} does not exist")


@shared_task
def analyze_cache():
    """
    Analyze cache performance and log metrics
    """
    try:
        stats = CacheService.get_cache_stats()
        
        if 'error' in stats:
            logger.error(f"Cache analysis error: {stats['error']}")
            return stats
        
        logger.info(f"Cache Stats - Hits: {stats['hits']}, Misses: {stats['misses']}, "
                   f"Hit Rate: {stats['hit_rate']:.2f}%")
        
        # Alert if hit rate is low
        if stats['hit_rate'] < 50:
            logger.warning(f"Low cache hit rate: {stats['hit_rate']:.2f}%")
        
        return stats
        
    except Exception as e:
        logger.error(f"Cache analysis failed: {e}")
        return {'error': str(e)}


@shared_task
def monitor_cache_health():
    """
    Monitor cache health and send alerts
    """
    try:
        health = CacheMonitor.check_cache_health()
        
        if health['status'] == 'critical':
            logger.error(f"CRITICAL: Cache health issues detected - {len(health['issues'])} issues")
            for issue in health['issues']:
                logger.error(f"  - {issue['message']}")
        elif health['status'] == 'warning':
            logger.warning(f"WARNING: Cache health warnings - {len(health['issues'])} issues")
            for issue in health['issues']:
                logger.warning(f"  - {issue['message']}")
        else:
            logger.info("Cache health is good")
        
        return health
        
    except Exception as e:
        logger.error(f"Cache monitoring failed: {e}")
        return {'error': str(e)}


@shared_task
def cleanup_expired_cache():
    """
    Clean up expired cache entries (for database-based cache fallback)
    """
    try:
        from .models import CacheEntry
        from django.utils import timezone
        
        count, _ = CacheEntry.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()
        
        logger.info(f"Cleaned up {count} expired cache entries")
        return count
        
    except Exception as e:
        logger.error(f"Cache cleanup failed: {e}")
        return 0


@shared_task
def warm_store_translations(store_id):
    """
    Warm translation cache for a specific store
    """
    try:
        from apps.stores.models import Store
        store = Store.objects.get(id=store_id)
        
        CacheWarmupService._warm_translations(store)
        logger.info(f"Warmed translation cache for store '{store.slug}'")
        
    except Store.DoesNotExist:
        logger.error(f"Store with id {store_id} does not exist")


@shared_task
def invalidate_store_cache_on_update(store_id, model_name, object_id):
    """
    Invalidate cache when a model is updated
    """
    try:
        from apps.stores.models import Store
        store = Store.objects.get(id=store_id)
        
        module_name = model_name.lower()
        
        # Invalidate specific object cache
        CacheService.delete(store, module_name, 'object', str(object_id))
        
        # Invalidate module cache for broader invalidation
        CacheService.invalidate_module(store, module_name)
        
        logger.info(f"Invalidated cache for {module_name}:{object_id} in store '{store.slug}'")
        
    except Store.DoesNotExist:
        logger.error(f"Store with id {store_id} does not exist")


@shared_task
def bulk_invalidate_cache(store_ids, module=None):
    """
    Bulk invalidate cache for multiple stores
    """
    try:
        from apps.stores.models import Store
        
        stores = Store.objects.filter(id__in=store_ids)
        
        for store in stores:
            if module:
                CacheService.invalidate_module(store, module)
            else:
                CacheService.invalidate_store(store)
        
        logger.info(f"Invalidated cache for {len(stores)} stores (module: {module or 'all'})")
        
    except Exception as e:
        logger.error(f"Bulk cache invalidation failed: {e}")


@shared_task
def schedule_cache_monitoring():
    """
    Schedule regular cache monitoring and metrics collection
    """
    try:
        # Log metrics
        CacheMonitor.log_cache_metrics()
        
        # Check health
        health = CacheMonitor.check_cache_health()
        
        # Schedule next monitoring
        from celery import current_app
        current_app.send_task(
            'apps.cache.tasks.schedule_cache_monitoring',
            countdown=300  # Every 5 minutes
        )
        
        logger.info("Scheduled next cache monitoring cycle")
        
        return health
        
    except Exception as e:
        logger.error(f"Cache monitoring scheduling failed: {e}")
        return {'error': str(e)}
    except Exception as exc:
        logger.error(f"Cache warm failed: {exc}")
        raise self.retry(exc=exc, countdown=60)
