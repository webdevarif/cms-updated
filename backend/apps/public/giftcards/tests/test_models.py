"""
Tests for gift cards models.
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestGiftCardModel:
    """Test GiftCard model"""
    
    def test_create_gift_card(self):
        """Test creating a gift card"""
        from apps.stores.models import Store
        from ..models import GiftCard
        
        from core.services.user import UserService
        
        user = UserService.create_user(email='test@example.com', password='pass')
        store = Store.objects.create(name='Test Store', slug='test-store', owner=user)
        
        gift_card = GiftCard.objects.create(
            store=store,
            code='TEST123456789',
            initial_balance=100.00,
            current_balance=100.00,
            gift_card_type='digital',
            created_by=user
        )
        
        assert str(gift_card) == 'TEST123456789 - 100.00/100.00 USD'
        assert gift_card.is_redeemable()
    
    def test_gift_card_expiration(self):
        """Test gift card expiration"""
        from apps.stores.models import Store
        from ..models import GiftCard
        from django.utils import timezone
        from datetime import timedelta
        
        from core.services.user import UserService
        
        user = UserService.create_user(email='test@example.com', password='pass')
        store = Store.objects.create(name='Test Store', slug='test-store', owner=user)
        
        gift_card = GiftCard.objects.create(
            store=store,
            code='TEST123456789',
            initial_balance=100.00,
            current_balance=100.00,
            gift_card_type='digital',
            expires_at=timezone.now() - timedelta(days=1),
            created_by=user
        )
        
        assert gift_card.is_expired()
        assert not gift_card.is_redeemable()
