import pytest
from django.contrib.auth import get_user_model
from apps.stores.models import Store
from apps.metafields.models import MetafieldDefinition, Metafield

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
def test_metafielddefinition_store_isolation(store_a, store_b):
    """Test MetafieldDefinition is isolated by store"""
    def_a = MetafieldDefinition.objects.create(store=store_a, namespace='test', key='color', type='text')
    def_b = MetafieldDefinition.objects.create(store=store_b, namespace='test', key='color', type='text')
    
    # Store A should only see its own metafield definitions
    assert MetafieldDefinition.objects.filter(store=store_a).count() == 1
    assert MetafieldDefinition.objects.filter(store=store_b).count() == 0

@pytest.mark.django_db
def test_metafield_store_isolation(store_a, store_b):
    """Test Metafield is isolated by store"""
    def_a = MetafieldDefinition.objects.create(store=store_a, namespace='test', key='color', type='text')
    def_b = MetafieldDefinition.objects.create(store=store_b, namespace='test', key='color', type='text')
    
    from django.contrib.contenttypes.models import ContentType
    content_type = ContentType.objects.get_for_model(MetafieldDefinition)
    
    meta_a = Metafield.objects.create(
        store=store_a, 
        definition=def_a, 
        content_type=content_type, 
        object_id=def_a.id,
        value_text='red'
    )
    meta_b = Metafield.objects.create(
        store=store_b, 
        definition=def_b, 
        content_type=content_type, 
        object_id=def_b.id,
        value_text='blue'
    )
    
    # Store A should only see its own metafields
    assert Metafield.objects.filter(store=store_a).count() == 1
    assert Metafield.objects.filter(store=store_b).count() == 0

@pytest.mark.django_db
def test_cross_store_metafield_data_leak(store_a, store_b):
    """Test that stores cannot access each other's metafield data"""
    def_a = MetafieldDefinition.objects.create(store=store_a, namespace='test', key='color', type='text')
    
    # Store B should not see Store A's data
    assert MetafieldDefinition.objects.filter(store=store_b).count() == 0
    
    # Verify data exists for Store A
    assert MetafieldDefinition.objects.filter(store=store_a).count() == 1
