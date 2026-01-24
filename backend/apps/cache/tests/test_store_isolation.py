import pytest
from django.contrib.auth import get_user_model
from apps.stores.models import Store
from apps.public.cache.models import CacheEntry

User = get_user_model()

@pytest.fixture
def store_a(db):
    """Create store A"""
    user = User.objects.create_user('user_a', email='a@example.com', password='pass123')
    return Store.objects.create(name='Store A', slug='store-a', owner=user)

@pytest.fixture
def store_b(db):
    """Create store B"""
    user = User.objects.create_user('user_b', email='b@example.com', password='pass123')
    return Store.objects.create(name='Store B', slug='store-b', owner=user)

@pytest.mark.django_db
def test_cacheentry_store_isolation(store_a, store_b):
    """Test CacheEntry is isolated by store"""
    cache_a = CacheEntry.objects.create(store=store_a, key='cache-a', value='data-a')
    cache_b = CacheEntry.objects.create(store=store_b, key='cache-b', value='data-b')
    
    # Store A should only see its own cache entries
    assert CacheEntry.objects.filter(store=store_a).count() == 1
    assert CacheEntry.objects.filter(store=store_b).count() == 0

@pytest.mark.django_db
def test_cross_store_cache_data_leak(store_a, store_b):
    """Test that stores cannot access each other's cache data"""
    cache_a = CacheEntry.objects.create(store=store_a, key='cache-a', value='data-a')
    
    # Store B should not see Store A's data
    assert CacheEntry.objects.filter(store=store_b).count() == 0
    
    # Verify data exists for Store A
    assert CacheEntry.objects.filter(store=store_a).count() == 1
