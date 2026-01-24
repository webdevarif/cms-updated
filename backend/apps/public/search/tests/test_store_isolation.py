import pytest
from django.contrib.auth import get_user_model
from apps.stores.models import Store
from apps.public.search.models import SearchIndex, SearchDocument

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
def test_searchindex_store_isolation(store_a, store_b):
    """Test SearchIndex is isolated by store"""
    index_a = SearchIndex.objects.create(store=store_a, name='Index A', slug='index-a')
    index_b = SearchIndex.objects.create(store=store_b, name='Index B', slug='index-b')
    
    # Store A should only see its own search indexes
    assert SearchIndex.objects.filter(store=store_a).count() == 1
    assert SearchIndex.objects.filter(store=store_b).count() == 0

@pytest.mark.django_db
def test_searchdocument_store_isolation(store_a, store_b):
    """Test SearchDocument is isolated by store"""
    index_a = SearchIndex.objects.create(store=store_a, name='Index A', slug='index-a')
    index_b = SearchIndex.objects.create(store=store_b, name='Index B', slug='index-b')
    
    from django.contrib.contenttypes.models import ContentType
    content_type = ContentType.objects.get_for_model(SearchIndex)
    
    doc_a = SearchDocument.objects.create(
        store=store_a, 
        search_index=index_a, 
        content_type=content_type, 
        object_id=index_a.id,
        title='Document A',
        content='Content A'
    )
    doc_b = SearchDocument.objects.create(
        store=store_b, 
        search_index=index_b, 
        content_type=content_type, 
        object_id=index_b.id,
        title='Document B',
        content='Content B'
    )
    
    # Store A should only see its own search documents
    assert SearchDocument.objects.filter(store=store_a).count() == 1
    assert SearchDocument.objects.filter(store=store_b).count() == 0

@pytest.mark.django_db
def test_cross_store_search_data_leak(store_a, store_b):
    """Test that stores cannot access each other's search data"""
    index_a = SearchIndex.objects.create(store=store_a, name='Index A', slug='index-a')
    
    # Store B should not see Store A's data
    assert SearchIndex.objects.filter(store=store_b).count() == 0
    
    # Verify data exists for Store A
    assert SearchIndex.objects.filter(store=store_a).count() == 1
