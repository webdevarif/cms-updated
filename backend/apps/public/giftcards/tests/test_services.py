"""
Tests for gift cards services.
"""
import json
from datetime import timedelta
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.utils import timezone
from django.core.cache import cache
from django.core.exceptions import ValidationError

from ...ecommerce.models import Order
from ...accounts.tests.factories import UserFactory
from ...stores.tests.factories import StoreFactory
from ..models import GiftCard, GiftCardHistory
from ..services import GiftCardService


class GiftCardServiceTestCase(TestCase):
    """Test cases for GiftCardService."""

    def setUp(self):
        """Set up test data."""
        self.store = StoreFactory()
        self.user = UserFactory()
        self.now = timezone.now()
        
        # Create a test gift card
        self.gift_card = GiftCard.objects.create(
            store=self.store,
            code='TEST12345678',
            initial_balance=100.00,
            current_balance=100.00,
            currency='USD',
            gift_card_type='digital',
            status='active',
            expires_at=self.now + timedelta(days=365),
            created_by=self.user
        )
        
        # Clear cache before each test
        cache.clear()
    
    def test_create_gift_card(self):
        """Test creating a new gift card."""
        with patch('apps.public.giftcards.services.GiftCardService._generate_code', return_value='NEWCODE123456'):
            gift_card = GiftCardService.create_gift_card(
                store=self.store,
                created_by=self.user,
                initial_balance=50.00,
                currency='USD',
                gift_card_type='physical'
            )
            
            self.assertIsNotNone(gift_card)
            self.assertEqual(gift_card.code, 'NEWCODE123456')
            self.assertEqual(gift_card.initial_balance, 50.00)
            self.assertEqual(gift_card.current_balance, 50.00)
            self.assertEqual(gift_card.status, 'active')
            
            # Verify history was created
            history = GiftCardHistory.objects.filter(gift_card=gift_card).first()
            self.assertIsNotNone(history)
            self.assertEqual(history.action, 'created')
            self.assertEqual(history.amount, 50.00)
    
    def test_redeem_gift_card_success(self):
        """Test redeeming a gift card successfully."""
        order = Order.objects.create(
            store=self.store,
            total_amount=30.00,
            status='pending',
            created_by=self.user
        )
        
        # Test partial redemption
        gift_card = GiftCardService.redeem_gift_card(
            code=self.gift_card.code,
            amount=30.00,
            user=self.user,
            order=order,
            method='online'
        )
        
        self.assertEqual(gift_card.current_balance, 70.00)
        
        # Verify history
        history = GiftCardHistory.objects.filter(
            gift_card=gift_card,
            action='redeemed'
        ).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.amount, 30.00)
        self.assertEqual(history.order, order)
        
        # Test full redemption
        gift_card = GiftCardService.redeem_gift_card(
            code=self.gift_card.code,
            amount=70.00,
            user=self.user
        )
        
        self.assertEqual(gift_card.current_balance, 0.00)
        self.assertEqual(gift_card.status, 'redeemed')
    
    def test_redeem_gift_card_insufficient_balance(self):
        """Test redeeming more than the available balance."""
        with self.assertRaises(ValidationError):
            GiftCardService.redeem_gift_card(
                code=self.gift_card.code,
                amount=200.00,
                user=self.user
            )
    
    def test_activate_gift_card(self):
        """Test activating a gift card."""
        # Create an inactive gift card
        gift_card = GiftCard.objects.create(
            store=self.store,
            code='INACTIVE123',
            initial_balance=50.00,
            current_balance=50.00,
            currency='USD',
            gift_card_type='digital',
            status='inactive',
            created_by=self.user
        )
        
        # Activate the gift card
        activated_card = GiftCardService.activate_gift_card(
            gift_card=gift_card,
            activated_by=self.user,
            notes='Activated during testing'
        )
        
        self.assertEqual(activated_card.status, 'active')
        
        # Verify history
        history = GiftCardHistory.objects.filter(
            gift_card=gift_card,
            action='activated'
        ).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.notes, 'Activated during testing')
    
    def test_void_gift_card(self):
        """Test voiding a gift card."""
        voided_card = GiftCardService.void_gift_card(
            gift_card=self.gift_card,
            voided_by=self.user,
            reason='Test void',
            notes='Voided during testing'
        )
        
        self.assertEqual(voided_card.status, 'voided')
        
        # Verify history
        history = GiftCardHistory.objects.filter(
            gift_card=self.gift_card,
            action='voided'
        ).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.notes, 'Voided during testing')
        self.assertEqual(history.metadata['reason'], 'Test void')
    
    def test_expire_gift_cards(self):
        """Test expiring gift cards."""
        # Create an expired gift card
        expired_card = GiftCard.objects.create(
            store=self.store,
            code='EXPIRED123',
            initial_balance=50.00,
            current_balance=50.00,
            currency='USD',
            gift_card_type='digital',
            status='active',
            expires_at=self.now - timedelta(days=1),
            created_by=self.user
        )
        
        # Run the expiration
        expired_count, error_count = GiftCardService.expire_gift_cards()
        
        self.assertEqual(expired_count, 1)
        self.assertEqual(error_count, 0)
        
        # Verify the card was expired
        expired_card.refresh_from_db()
        self.assertEqual(expired_card.status, 'expired')
    
    def test_get_gift_card_balance(self):
        """Test getting gift card balance with caching."""
        # First call - should hit the database
        balance = GiftCardService.get_gift_card_balance(self.gift_card.code)
        self.assertEqual(balance['code'], self.gift_card.code)
        self.assertEqual(balance['balance'], '100.00')
        
        # Second call - should use cache
        with self.assertNumQueries(0):
            cached_balance = GiftCardService.get_gift_card_balance(self.gift_card.code)
            self.assertEqual(cached_balance, balance)
        
        # Invalidate cache and verify
        GiftCardService.invalidate_balance_cache(self.gift_card.code)
        with self.assertNumQueries(1):
            GiftCardService.get_gift_card_balance(self.gift_card.code)
    
    def test_get_gift_card_analytics(self):
        """Test generating gift card analytics."""
        # Create some test data
        GiftCard.objects.create(
            store=self.store,
            code='ANALYTICS1',
            initial_balance=50.00,
            current_balance=50.00,
            currency='USD',
            gift_card_type='physical',
            status='active',
            created_by=self.user
        )
        
        # Generate analytics
        analytics = GiftCardService.get_gift_card_analytics(
            store=self.store,
            start_date=self.now - timedelta(days=30),
            end_date=self.now + timedelta(days=1)
        )
        
        # Verify the results
        self.assertEqual(analytics['total_gift_cards'], 2)  # 1 from setUp + 1 here
        self.assertEqual(analytics['active_gift_cards'], 2)
        self.assertEqual(analytics['status_distribution']['active'], 2)
        self.assertIn('physical', analytics['type_distribution'])
        self.assertEqual(len(analytics['recent_activity']), 1)  # From setUp
    
    def test_generate_code(self):
        """Test gift card code generation."""
        # Test with default settings
        code = GiftCardService._generate_code()
        self.assertEqual(len(code), 12)  # Default length
        
        # Test with custom length
        code = GiftCardService._generate_code(8)
        self.assertEqual(len(code), 8)
        
        # Test with prefix
        with self.settings(GIFT_CARD_CODE_PREFIX='GC'):
            code = GiftCardService._generate_code(10)
            self.assertTrue(code.startswith('GC'))
            self.assertEqual(len(code), 10)  # Includes prefix
        
        # Test with custom charset
        with self.settings(GIFT_CARD_CODE_CHARS='ABC123'):
            code = GiftCardService._generate_code(10)
            self.assertTrue(all(c in 'ABC123' for c in code))
