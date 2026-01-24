import pytest
from django.contrib.auth import get_user_model
from apps.stores.models import Store
from apps.public.giftcards.models import GiftCard, GiftCardHistory

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
def test_giftcard_store_isolation(store_a, store_b):
    """Test GiftCard is isolated by store"""
    giftcard_a = GiftCard.objects.create(store=store_a, code='GIFT-A', balance=100)
    giftcard_b = GiftCard.objects.create(store=store_b, code='GIFT-B', balance=200)
    
    # Store A should only see its own giftcards
    assert GiftCard.objects.filter(store=store_a).count() == 1
    assert GiftCard.objects.filter(store=store_b).count() == 0

@pytest.mark.django_db
def test_giftcardhistory_store_isolation(store_a, store_b):
    """Test GiftCardHistory is isolated by store"""
    giftcard_a = GiftCard.objects.create(store=store_a, code='GIFT-A', balance=100)
    giftcard_b = GiftCard.objects.create(store=store_b, code='GIFT-B', balance=200)
    
    history_a = GiftCardHistory.objects.create(store=store_a, gift_card=giftcard_a, action='created')
    history_b = GiftCardHistory.objects.create(store=store_b, gift_card=giftcard_b, action='created')
    
    # Store A should only see its own giftcard history
    assert GiftCardHistory.objects.filter(store=store_a).count() == 1
    assert GiftCardHistory.objects.filter(store=store_b).count() == 0

@pytest.mark.django_db
def test_cross_store_giftcard_data_leak(store_a, store_b):
    """Test that stores cannot access each other's giftcard data"""
    giftcard_a = GiftCard.objects.create(store=store_a, code='GIFT-A', balance=100)
    history_a = GiftCardHistory.objects.create(store=store_a, gift_card=giftcard_a, action='created')
    
    # Store B should not see Store A's data
    assert GiftCard.objects.filter(store=store_b).count() == 0
    assert GiftCardHistory.objects.filter(store=store_b).count() == 0
    
    # Verify data exists for Store A
    assert GiftCard.objects.filter(store=store_a).count() == 1
    assert GiftCardHistory.objects.filter(store=store_a).count() == 1
