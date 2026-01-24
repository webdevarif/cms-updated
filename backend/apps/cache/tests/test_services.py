"""
Tests for cache services.
"""
from django.test import TestCase
from django.core.cache import cache
from apps.cache.services import CacheService
from apps.stores.models import Store


class CacheServiceTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.store = Store.objects.create(name='Test Store', slug='test-store')
        # Clear cache before each test
        cache.clear()
    
    def test_get_cache_key(self):
        """Test cache key generation"""
        key = CacheService.get_cache_key(self.store, 'pages', 'page', '123')
        expected = 'test-store:pages:page:123:v1'
        self.assertEqual(key, expected)
        
        # Test with custom version
        key = CacheService.get_cache_key(self.store, 'pages', 'page', '123', 'v2')
        expected = 'test-store:pages:page:123:v2'
        self.assertEqual(key, expected)
    
    def test_cache_set_and_get(self):
        """Test cache set and get operations"""
        data = {'test': 'data'}
        
        # Set cache
        result = CacheService.set(self.store, 'test', 'object', '1', data)
        self.assertTrue(result)
        
        # Get cache
        cached = CacheService.get(self.store, 'test', 'object', '1')
        self.assertEqual(cached, data)
    
    def test_cache_get_default(self):
        """Test cache get with default value"""
        # Get non-existent cache
        cached = CacheService.get(self.store, 'test', 'object', 'nonexistent', 'default')
        self.assertEqual(cached, 'default')
    
    def test_cache_delete(self):
        """Test cache delete operations"""
        data = {'test': 'data'}
        
        # Set cache
        CacheService.set(self.store, 'test', 'object', '1', data)
        
        # Delete cache
        result = CacheService.delete(self.store, 'test', 'object', '1')
        self.assertTrue(result)
        
        # Verify deletion
        cached = CacheService.get(self.store, 'test', 'object', '1')
        self.assertIsNone(cached)
    
    def test_cache_get_or_set(self):
        """Test cache get_or_set pattern"""
        callback_called = []
        
        def callback():
            callback_called.append(True)
            return {'test': 'data'}
        
        # First call - should execute callback
        result1 = CacheService.get_or_set(self.store, 'test', 'object', '1', callback)
        self.assertEqual(len(callback_called), 1)
        self.assertEqual(result1, {'test': 'data'})
        
        # Second call - should use cache
        result2 = CacheService.get_or_set(self.store, 'test', 'object', '1', callback)
        self.assertEqual(len(callback_called), 1)  # Still only called once
        self.assertEqual(result2, {'test': 'data'})
    
    def test_cache_json_operations(self):
        """Test JSON cache operations"""
        data = {'id': 1, 'name': 'test', 'items': [1, 2, 3]}
        
        # Cache JSON
        result = CacheService.cache_json(self.store, 'test', 'object', '1', data)
        self.assertTrue(result)
        
        # Get JSON
        cached = CacheService.get_json(self.store, 'test', 'object', '1')
        self.assertEqual(cached, data)
        self.assertIsInstance(cached, dict)
        self.assertEqual(cached['items'], [1, 2, 3])
    
    def test_cache_json_invalid(self):
        """Test JSON cache with invalid data"""
        # Set invalid JSON
        key = CacheService.get_cache_key(self.store, 'test', 'object', '1')
        cache.set(key, 'invalid json')
        
        # Get JSON should return None for invalid data
        cached = CacheService.get_json(self.store, 'test', 'object', '1')
        self.assertIsNone(cached)
    
    def test_invalidate_store(self):
        """Test store cache invalidation"""
        # Set multiple cache entries
        CacheService.set(self.store, 'pages', 'page', '1', 'data1')
        CacheService.set(self.store, 'ecommerce', 'product', '1', 'data2')
        CacheService.set(self.store, 'translations', 'translation', '1', 'data3')
        
        # Invalidate store cache
        result = CacheService.invalidate_store(self.store)
        self.assertTrue(result)
        
        # Verify all entries are gone
        self.assertIsNone(CacheService.get(self.store, 'pages', 'page', '1'))
        self.assertIsNone(CacheService.get(self.store, 'ecommerce', 'product', '1'))
        self.assertIsNone(CacheService.get(self.store, 'translations', 'translation', '1'))
    
    def test_invalidate_module(self):
        """Test module cache invalidation"""
        # Set cache entries for different modules
        CacheService.set(self.store, 'pages', 'page', '1', 'data1')
        CacheService.set(self.store, 'ecommerce', 'product', '1', 'data2')
        CacheService.set(self.store, 'pages', 'page', '2', 'data3')
        
        # Invalidate pages module
        result = CacheService.invalidate_module(self.store, 'pages')
        self.assertTrue(result)
        
        # Verify pages entries are gone but ecommerce remains
        self.assertIsNone(CacheService.get(self.store, 'pages', 'page', '1'))
        self.assertIsNone(CacheService.get(self.store, 'pages', 'page', '2'))
        self.assertIsNotNone(CacheService.get(self.store, 'ecommerce', 'product', '1'))
    
    def test_cache_stats(self):
        """Test cache statistics"""
        # Set some cache entries to generate stats
        CacheService.set(self.store, 'test', 'object', '1', 'data1')
        CacheService.set(self.store, 'test', 'object', '2', 'data2')
        
        # Get some entries to generate hits/misses
        CacheService.get(self.store, 'test', 'object', '1')  # Hit
        CacheService.get(self.store, 'test', 'object', '3')  # Miss
        
        # Get stats
        stats = CacheService.get_cache_stats()
        
        # Should have hits and misses
        self.assertIn('hits', stats)
        self.assertIn('misses', stats)
        self.assertIn('hit_rate', stats)
        self.assertIsInstance(stats['hit_rate'], (int, float))
