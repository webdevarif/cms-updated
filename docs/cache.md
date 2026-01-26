# Cache App Rules v1.0

## 🎯 Purpose

This document defines strict development rules for the **cache** system in CMS-Updated backend, implementing a unified caching strategy with Redis for performance optimization across all modules.

---

## 🏗️ Cache System Structure

### **Fixed Directory Structure**
```
apps/
├── cache/
│   ├── __init__.py
│   ├── services.py
│   ├── tasks.py
│   ├── management/
│   │   └── commands/
│   │       ├── clear_cache.py
│   │       ├── warm_cache.py
│   │       └── analyze_cache.py
│   └── tests/
│       ├── __init__.py
│       └── test_services.py
```

---

## 📋 Cache Key Standards

### **Key Naming Convention**
All cache keys must follow this pattern:

```
{store_slug}:{module}:{object_type}:{object_id}:{version}
```

**Examples:**
- `my-store:pages:page:123:v1`
- `my-store:ecommerce:product:456:v1`
- `my-store:translations:translation:en_US:v1`

### **Key Prefixes**
```python
# Cache key prefixes by module
CACHE_PREFIXES = {
    'pages': 'pages',
    'posts': 'posts',
    'ecommerce': 'ecommerce',
    'translations': 'translations',
    'themes': 'themes',
    'media': 'media',
    'forms': 'forms',
    'webhooks': 'webhooks',
    'notifications': 'notifications',
    'search': 'search',
}
```

---

## 🛠️ Services Layer

### **CacheService**
```python
# apps/cache/services.py
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
```

---

## 🔄 Cache Invalidation Strategies

### **Invalidation Rules**

#### **1. Time-Based Invalidation**
```python
# Short-lived cache (5 minutes)
CacheService.set(store, 'ecommerce', 'product', product.id, data, timeout=300)

# Medium-lived cache (1 hour)
CacheService.set(store, 'pages', 'page', page.id, data, timeout=3600)

# Long-lived cache (24 hours)
CacheService.set(store, 'translations', 'translation', lang_code, data, timeout=86400)
```

#### **2. Event-Based Invalidation**
```python
# Invalidate on model save
from django.db.models.signals import post_save, post_delete

@receiver(post_save, sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    CacheService.delete(instance.store, 'ecommerce', 'product', instance.id)
    CacheService.delete_pattern(instance.store, 'ecommerce:product:*')

@receiver(post_delete, sender=Product)
def invalidate_product_cache_delete(sender, instance, **kwargs):
    CacheService.delete(instance.store, 'ecommerce', 'product', instance.id)
```

#### **3. Manual Invalidation**
```python
# Invalidate specific object
CacheService.delete(store, 'pages', 'page', page.id)

# Invalidate all pages for a store
CacheService.delete_pattern(store, 'pages:*')

# Invalidate entire store
CacheService.invalidate_store(store)
```

---

## 📊 Cache Warming Strategies

### **Cache Warming Service**
```python
# apps/cache/services.py (continued)

class CacheWarmupService:
    """Cache warming service"""
    
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
        from apps.pages.models import Page
        
        pages = Page.objects.filter(
            store=store,
            status='published'
        ).select_related('store')
        
        for page in pages:
            data = {
                'id': page.id,
                'title': page.title,
                'slug': page.slug,
                'content': page.content,
                'url': page.get_absolute_url()
            }
            CacheService.cache_json(store, 'pages', 'page', page.id, data, timeout=3600)
    
    @staticmethod
    def _warm_products(store):
        """Warm product cache"""
        from apps.ecommerce.models import Product
        
        products = Product.objects.filter(
            store=store,
            is_active=True
        ).select_related('store').prefetch_related('variants')
        
        for product in products:
            data = {
                'id': product.id,
                'title': product.title,
                'description': product.description,
                'price': float(product.price),
                'is_active': product.is_active
            }
            CacheService.cache_json(store, 'ecommerce', 'product', product.id, data, timeout=3600)
    
    @staticmethod
    def _warm_translations(store):
        """Warm translation cache"""
        from apps.translations.models import Translation
        
        translations = Translation.objects.filter(
            store=store
        ).select_related('language', 'translation_key')
        
        for translation in translations:
            key = f"{translation.language.code}:{translation.translation_key.key}"
            CacheService.set(store, 'translations', 'translation', key, translation.text, timeout=86400)
```

---

## 🚀 Celery Tasks

### **Cache Management Tasks**
```python
# apps/cache/tasks.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def clear_cache(store_id=None):
    """
    Clear cache for store or all stores
    """
    if store_id:
        from .models import Store
        store = Store.objects.get(id=store_id)
        CacheService.invalidate_store(store)
        logger.info(f"Cleared cache for store: {store.slug}")
    else:
        # Clear all cache
        cache.clear()
        logger.info("Cleared all cache")

@shared_task
def warm_cache(store_id):
    """
    Warm cache for a store
    """
    from .models import Store
    from .services import CacheWarmupService
    
    store = Store.objects.get(id=store_id)
    CacheWarmupService.warm_store_cache(store)

@shared_task
def analyze_cache():
    """
    Analyze cache performance
    """
    stats = CacheService.get_cache_stats()
    
    logger.info(f"Cache Stats: {stats}")
    
    # Alert if hit rate is low
    if stats.get('hit_rate', 0) < 50:
        logger.warning(f"Low cache hit rate: {stats['hit_rate']:.2f}%")
```

---

## 🔧 Management Commands

### **Clear Cache**
```bash
# Clear all cache
python manage.py clear_cache

# Clear cache for specific store
python manage.py clear_cache --store=my-store

# Clear cache for specific module
python manage.py clear_cache --store=my-store --module=pages
```

### **Warm Cache**
```bash
# Warm cache for a store
python manage.py warm_cache --store=my-store
```

### **Analyze Cache**
```bash
# Analyze cache performance
python manage.py analyze_cache
```

---

## 📚 Cache Best Practices

### **DO:**
1. **Use consistent key patterns** - Follow the naming convention
2. **Set appropriate timeouts** - Match data freshness requirements
3. **Invalidate on changes** - Use signals for automatic invalidation
4. **Warm critical data** - Preload frequently accessed data
5. **Monitor hit rates** - Track cache performance
6. **Use JSON for complex data** - Serialize complex objects
7. **Cache database queries** - Reduce database load
8. **Cache expensive computations** - Improve response times
9. **Use get_or_set pattern** - Simplify cache logic
10. **Log cache operations** - Debug cache issues

### **DON'T:**
1. **Don't cache sensitive data** - Never cache passwords, tokens, etc.
2. **Don't cache forever** - Always set timeouts
3. **Don't cache without invalidation** - Stale data is worse than no data
4. **Don't cache large objects** - Keep cache entries small
5. **Don't ignore cache failures** - Handle cache errors gracefully
6. **Don't cache user-specific data without user ID** - Include user in key
7. **Don't cache mutable objects** - Always return copies
8. **Don't cache without versioning** - Use version numbers for schema changes
9. **Don't rely on cache** - Always have fallback logic
10. **Don't cache everything** - Only cache what's expensive to compute

---

## 🔗 Integration Examples

### **Integration with pages.md**
```python
# apps/pages/services.py
from apps.cache.services import CacheService

class PageService:
    @staticmethod
    def get_page(store, page_id):
        """Get page with caching"""
        # Try cache first
        cached = CacheService.get_json(store, 'pages', 'page', page_id)
        if cached:
            return cached
        
        # Fetch from database
        page = Page.objects.get(store=store, id=page_id)
        
        # Cache the result
        data = {
            'id': page.id,
            'title': page.title,
            'slug': page.slug,
            'content': page.content,
            'url': page.get_absolute_url()
        }
        CacheService.cache_json(store, 'pages', 'page', page.id, data, timeout=3600)
        
        return data
```

### **Integration with ecommerce.md**
```python
# apps/ecommerce/services.py
from apps.cache.services import CacheService

class ProductService:
    @staticmethod
    def get_product(store, product_id):
        """Get product with caching"""
        # Try cache first
        cached = CacheService.get_json(store, 'ecommerce', 'product', product_id)
        if cached:
            return cached
        
        # Fetch from database
        product = Product.objects.get(store=store, id=product_id)
        
        # Cache the result
        data = {
            'id': product.id,
            'title': product.title,
            'description': product.description,
            'price': float(product.price),
            'is_active': product.is_active
        }
        CacheService.cache_json(store, 'ecommerce', 'product', product.id, data, timeout=3600)
        
        return data
```

### **Integration with translations.md**
```python
# apps/translations/services.py
from apps.cache.services import CacheService

class TranslationService:
    @staticmethod
    def get_translation(store, language_code, key):
        """Get translation with caching"""
        cache_key = f"{language_code}:{key}"
        
        # Try cache first
        cached = CacheService.get(store, 'translations', 'translation', cache_key)
        if cached:
            return cached
        
        # Fetch from database
        translation = Translation.objects.get(
            store=store,
            language__code=language_code,
            translation_key__key=key
        )
        
        # Cache the result
        CacheService.set(store, 'translations', 'translation', cache_key, translation.text, timeout=86400)
        
        return translation.text
```

---

## 📊 Cache Configuration

### **Redis Configuration**
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'cms-updated',
        'TIMEOUT': 3600,
    }
}
```

### **Cache Timeout Standards**
```python
CACHE_TIMEOUTS = {
    'short': 300,      # 5 minutes
    'medium': 3600,    # 1 hour
    'long': 86400,     # 24 hours
    'very_long': 604800,  # 7 days
}
```

---

## 🧪 Testing Rules

### **Required Coverage**
- **Services**: 100% code coverage
- **Integration**: Critical path testing

### **Test Examples**
```python
# apps/cache/tests/test_services.py
from django.test import TestCase
from ..services import CacheService

class CacheServiceTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', slug='test-store')
    
    def test_cache_set_and_get(self):
        """Test cache set and get"""
        data = {'test': 'data'}
        
        CacheService.set(self.store, 'test', 'object', '1', data)
        cached = CacheService.get(self.store, 'test', 'object', '1')
        
        self.assertEqual(cached, data)
    
    def test_cache_delete(self):
        """Test cache delete"""
        data = {'test': 'data'}
        
        CacheService.set(self.store, 'test', 'object', '1', data)
        CacheService.delete(self.store, 'test', 'object', '1')
        
        cached = CacheService.get(self.store, 'test', 'object', '1')
        self.assertIsNone(cached)
    
    def test_cache_get_or_set(self):
        """Test cache get_or_set"""
        callback_called = []
        
        def callback():
            callback_called.append(True)
            return {'test': 'data'}
        
        # First call - should execute callback
        result1 = CacheService.get_or_set(self.store, 'test', 'object', '1', callback)
        self.assertEqual(len(callback_called), 1)
        
        # Second call - should use cache
        result2 = CacheService.get_or_set(self.store, 'test', 'object', '1', callback)
        self.assertEqual(len(callback_called), 1)
        
        self.assertEqual(result1, result2)
```

---

## 📈 Monitoring

### **Cache Metrics to Track**
- **Hit Rate**: Percentage of cache hits vs misses
- **Memory Usage**: Total memory used by cache
- **Key Count**: Number of keys in cache
- **Eviction Rate**: Rate at which keys are evicted
- **Latency**: Average cache response time

### **Alerting**
- **Low Hit Rate**: Alert if hit rate < 50%
- **High Memory Usage**: Alert if memory > 80%
- **Cache Errors**: Alert on cache connection errors

---

## 🎯 Implementation Checklist

- [ ] Create CacheService with standard methods
- [ ] Implement cache key naming convention
- [ ] Create cache invalidation strategies
- [ ] Implement cache warming service
- [ ] Create Celery tasks for cache management
- [ ] Add management commands
- [ ] Create tests (services)
- [ ] Add monitoring and logging
- [ ] Document cache best practices
- [ ] Add integration examples
- [ ] Configure Redis cache backend
- [ ] Set up cache monitoring

---

## 📖 Version History

- **v1.0** - Initial version with Redis cache integration
