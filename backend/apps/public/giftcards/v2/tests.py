"""
Tests for gift cards API v2.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from decimal import Decimal
from ..models import GiftCard, GiftCardHistory
from ..services import GiftCardService

User = get_user_model()


class GiftCardServiceTestCase(TestCase):
    """Test GiftCardService methods"""
    
    def setUp(self):
        """Set up test data"""
        from apps.stores.models import Store
        
        self.store = Store.objects.create(
            name="Test Store",
            slug="test-store",
            owner=None
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
    
    def test_create_gift_card(self):
        """Test gift card creation"""
        gift_card = GiftCardService.create_gift_card(
            store=self.store,
            created_by=self.user,
            gift_card_type='digital',
            initial_balance=Decimal('100.00'),
            currency='USD',
            recipient_name='John Doe',
            recipient_email='john@example.com'
        )
        
        self.assertEqual(gift_card.store, self.store)
        self.assertEqual(gift_card.initial_balance, Decimal('100.00'))
        self.assertEqual(gift_card.current_balance, Decimal('100.00'))
        self.assertEqual(gift_card.status, 'active')
        self.assertIsNotNone(gift_card.code)
        self.assertEqual(len(gift_card.code), 12)
        
        # Check history was created
        history = GiftCardHistory.objects.filter(gift_card=gift_card, action='created').first()
        self.assertIsNotNone(history)
        self.assertEqual(history.created_by, self.user)
    
    def test_redeem_gift_card(self):
        """Test gift card redemption"""
        # Create gift card first
        gift_card = GiftCardService.create_gift_card(
            store=self.store,
            created_by=self.user,
            gift_card_type='digital',
            initial_balance=Decimal('100.00')
        )
        
        # Redeem partial amount
        redeemed_card = GiftCardService.redeem_gift_card(
            code=gift_card.code,
            amount=Decimal('25.50'),
            user=self.user
        )
        
        self.assertEqual(redeemed_card.current_balance, Decimal('74.50'))
        
        # Check history
        history = GiftCardHistory.objects.filter(gift_card=gift_card, action='redeemed').first()
        self.assertIsNotNone(history)
        self.assertEqual(history.amount, Decimal('25.50'))
    
    def test_redeem_insufficient_balance(self):
        """Test redemption with insufficient balance"""
        gift_card = GiftCardService.create_gift_card(
            store=self.store,
            created_by=self.user,
            gift_card_type='digital',
            initial_balance=Decimal('10.00')
        )
        
        with self.assertRaises(Exception) as context:
            GiftCardService.redeem_gift_card(
                code=gift_card.code,
                amount=Decimal('15.00'),
                user=self.user
            )
        
        self.assertIn("Insufficient balance", str(context.exception))
    
    def test_get_gift_card_balance(self):
        """Test balance check"""
        gift_card = GiftCardService.create_gift_card(
            store=self.store,
            created_by=self.user,
            gift_card_type='digital',
            initial_balance=Decimal('100.00')
        )
        
        balance_info = GiftCardService.get_gift_card_balance(gift_card.code)
        
        self.assertIsNotNone(balance_info)
        self.assertEqual(balance_info['code'], gift_card.code)
        self.assertEqual(balance_info['balance'], str(Decimal('100.00')))
        self.assertEqual(balance_info['currency'], 'USD')
        self.assertFalse(balance_info['is_expired'])
    
    def test_get_gift_card_analytics(self):
        """Test analytics generation"""
        # Create some test data
        for i in range(5):
            GiftCardService.create_gift_card(
                store=self.store,
                created_by=self.user,
                gift_card_type='digital',
                initial_balance=Decimal('50.00')
            )
        
        analytics = GiftCardService.get_gift_card_analytics(self.store)
        
        self.assertIn('total_gift_cards', analytics)
        self.assertIn('total_value', analytics)
        self.assertIn('active_gift_cards', analytics)
        self.assertEqual(analytics['total_gift_cards'], 5)


class GiftCardAPITestCase(APITestCase):
    """Test GiftCard API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        from apps.stores.models import Store
        
        self.store = Store.objects.create(
            name="Test Store",
            slug="test-store",
            owner=None
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        
        # Add user to store
        from apps.stores.models import StoreMember
        StoreMember.objects.create(
            store=self.store,
            user=self.user,
            role='admin'
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_create_gift_card_api(self):
        """Test gift card creation via API"""
        url = reverse('giftcards:giftcard-list')
        data = {
            'gift_card_type': 'digital',
            'initial_balance': '100.00',
            'currency': 'USD',
            'recipient_name': 'John Doe',
            'recipient_email': 'john@example.com'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GiftCard.objects.count(), 1)
        
        gift_card = GiftCard.objects.first()
        self.assertEqual(gift_card.recipient_name, 'John Doe')
        self.assertEqual(gift_card.initial_balance, Decimal('100.00'))
    
    def test_redeem_gift_card_api(self):
        """Test gift card redemption via API"""
        # Create gift card first
        gift_card = GiftCardService.create_gift_card(
            store=self.store,
            created_by=self.user,
            gift_card_type='digital',
            initial_balance=Decimal('100.00')
        )
        
        url = reverse('giftcards:giftcard-redeem')
        data = {
            'code': gift_card.code,
            'amount': '25.50',
            'method': 'online'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check balance was updated
        gift_card.refresh_from_db()
        self.assertEqual(gift_card.current_balance, Decimal('74.50'))
    
    def test_check_balance_api(self):
        """Test balance check via API"""
        gift_card = GiftCardService.create_gift_card(
            store=self.store,
            created_by=self.user,
            gift_card_type='digital',
            initial_balance=Decimal('100.00')
        )
        
        url = reverse('giftcards:giftcard-balance')
        response = self.client.get(url, {'code': gift_card.code})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], '100.00')
    
    def test_list_gift_cards_api(self):
        """Test listing gift cards via API"""
        # Create multiple gift cards
        for i in range(3):
            GiftCardService.create_gift_card(
                store=self.store,
                created_by=self.user,
                gift_card_type='digital',
                initial_balance=Decimal('50.00')
            )
        
        url = reverse('giftcards:giftcard-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
