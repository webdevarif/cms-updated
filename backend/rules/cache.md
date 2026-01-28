# Cache Infrastructure Rules v1.0

## Authority
- Owner: Infrastructure Lead
- Enforced By: CacheService, management commands
- Scope: Shared Infrastructure
- Authority Level: INFRASTRUCTURE STANDARD

## 🎯 Purpose
This document defines SHARED INFRASTRUCTURE rules for the **cache** system in CMS-Updated backend, providing a unified caching strategy with Redis for performance optimization across all modules.

---

## 🏗️ Structure
### **Infrastructure Directory Structure**
```
apps/
├── cache/
│   ├── __init__.py
│   ├── services.py          # Infrastructure service layer
│   ├── tasks.py             # Async cache operations
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

## 📦 Data Model
### **Infrastructure Key Schema**
All cache keys MUST follow this pattern:
```
{store_slug}:{module}:{object_type}:{object_id}:{version}
```
**Examples:**
- `my-store:pages:page:123:v1`
- `my-store:ecommerce:product:456:v1`
- `my-store:translations:translation:en_US:v1`

### **Infrastructure Module Prefixes**
```python
# Infrastructure-provided cache key prefixes
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

## ⚙️ Services
### **Infrastructure CacheService**
```python
# apps/cache/services.py
from django.core.cache import cache
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """Infrastructure cache management service"""

    @staticmethod
    def get_cache_key(store, module, object_type, object_id, version='v1'):
        """
        Generate standardized cache key
        INFRASTRUCTURE PROVIDES: Key generation
        """
        return f"{store.slug}:{module}:{object_type}:{object_id}:{version}"

    @staticmethod
    def get(store, module, object_type, object_id, default=None):
        """
        Get value from cache
        INFRASTRUCTURE PROVIDES: Cache retrieval
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
        INFRASTRUCTURE PROVIDES: Cache storage
        """
        key = CacheService.get_cache_key(store, module, object_type, object_id)
        cache.set(key, value, timeout)

        logger.debug(f"Cache SET: {key} (timeout: {timeout}s)")
        return True

    @staticmethod
    def delete(store, module, object_type, object_id):
        """
        Delete value from cache
        INFRASTRUCTURE PROVIDES: Cache deletion
        """
        key = CacheService.get_cache_key(store, module, object_type, object_id)
        cache.delete(key)

        logger.debug(f"Cache DELETE: {key}")
        return True

    @staticmethod
    def delete_pattern(store, pattern):
        """
        Delete all keys matching pattern
        INFRASTRUCTURE PROVIDES: Pattern-based deletion
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
        INFRASTRUCTURE PROVIDES: Store-level invalidation
        """
        return CacheService.delete_pattern(store, '*')

    @staticmethod
    def invalidate_module(store, module):
        """
        Invalidate all cache for a module in a store
        INFRASTRUCTURE PROVIDES: Module-level invalidation
        """
        return CacheService.delete_pattern(store, f"{module}:*")

    @staticmethod
    def get_or_set(store, module, object_type, object_id, callback, timeout=3600):
        """
        Get value from cache or set using callback
        INFRASTRUCTURE PROVIDES: Callback-based caching
        APPLICATION MUST: Provide callback function
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
        INFRASTRUCTURE PROVIDES: JSON serialization
        """
        key = CacheService.get_cache_key(store, module, object_type, object_id)
        cache.set(key, json.dumps(data), timeout)

        logger.debug(f"Cache JSON: {key}")
        return True

    @staticmethod
    def get_json(store, module, object_type, object_id):
        """
        Get JSON data from cache
        INFRASTRUCTURE PROVIDES: JSON deserialization
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
        INFRASTRUCTURE PROVIDES: Performance monitoring
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

## 🔐 Security
### **Infrastructure Security Requirements**
- INFRASTRUCTURE MUST validate cache keys before use
- INFRASTRUCTURE MUST sanitize cached data before storage
- INFRASTRUCTURE MUST implement cache isolation between stores
- INFRASTRUCTURE MUST log cache operations for audit trails

### **Application Security Responsibilities**
- APPLICATION MUST NOT cache sensitive user data without encryption
- APPLICATION MUST implement cache invalidation on data changes
- APPLICATION MUST validate data before caching
- APPLICATION MUST ensure cache keys follow naming convention

---

## 🧪 Testing
### **Infrastructure Testing Requirements**
- **Services**: 100% code coverage
- **Integration**: Critical path testing
- **Performance**: Cache hit/miss ratio validation

### **Infrastructure Test Examples**
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

## 🚫 Forbidden Patterns
### **Infrastructure Forbidden Patterns**
- MUST NOT use cache without proper key validation
- MUST NOT create cache keys without store isolation
- MUST NOT store large objects in cache (>1MB)
- MUST NOT bypass cache service direct access

### **Application Forbidden Patterns**
- MUST NOT cache sensitive data without encryption
- MUST NOT use cache for real-time data
- MUST NOT ignore cache invalidation requirements
- MUST NOT use cache for session data

---

## 🔗 Cross-Module Dependencies
### **Infrastructure Interface Requirements**
- ALL modules MUST import from apps.cache.services
- ALL modules MUST use CacheService for cache operations
- ALL modules MUST follow key naming convention
- ALL modules MUST implement cache invalidation

### **Application Integration Examples**
```python
# APPLICATION RESPONSIBILITY: Use infrastructure service
from apps.cache.services import CacheService

class ExampleService:
    @staticmethod
    def get_cached_data(store, object_id):
        """APPLICATION MUST: Use infrastructure service"""
        # Try cache first
        cached = CacheService.get_json(store, 'module', 'object', object_id)
        if cached:
            return cached

        # Fetch from database
        data = fetch_from_database(store, object_id)

        # Cache the result
        CacheService.cache_json(store, 'module', 'object', object_id, data, timeout=3600)

        return data
```

---

## 📝 Notes
### **Infrastructure Management Commands**
#### Clear Cache
```bash
# Clear all cache
python manage.py clear_cache

# Clear cache for specific store
python manage.py clear_cache --store=my-store

# Clear cache for specific module
python manage.py clear_cache --store=my-store --module=pages
```

#### Warm Cache
```bash
# Warm cache for a store
python manage.py warm_cache --store=my-store
```

#### Analyze Cache
```bash
# Analyze cache performance
python manage.py analyze_cache
```

---

**Version**: 1.0
**Last Updated**: 2026-01-26
**Next Review**: 2026-02-25
