"""
Cache service tests.
"""
from django.test import TestCase
from django.core.cache import cache
from apps.cache.services import CacheService


class CacheServiceTest(TestCase):
    def setUp(self):
        from apps.stores.models import Store
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
    
    def test_cache_key_generation(self):
        """Test cache key generation"""
        key = CacheService.get_cache_key(self.store, 'pages', 'page', '123')
        expected = 'test-store:pages:page:123:v1'
        self.assertEqual(key, expected)
    
    def test_json_caching(self):
        """Test JSON caching"""
        data = {'key': 'value', 'number': 42}
        
        CacheService.cache_json(self.store, 'test', 'object', '1', data)
        cached = CacheService.get_json(self.store, 'test', 'object', '1')
        
        self.assertEqual(cached, data)
