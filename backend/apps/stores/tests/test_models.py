"""
Tests for store models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class TestStore(TestCase):
    """Test Store model"""
    
    def setUp(self):
        """Set up test data"""
        from core.services.user import UserService
        self.user = UserService.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_store(self):
        """Test creating a store"""
        from apps.stores.models import Store
        
        store = Store.objects.create(
            name='Test Store',
            owner=self.user,
            store_type='ecommerce'
        )
        
        self.assertEqual(store.name, 'Test Store')
        self.assertEqual(store.status, 'pending')
        self.assertIsNotNone(store.access_code)
        self.assertIsNotNone(store.verification_token)
    
    def test_slug_generation(self):
        """Test automatic slug generation"""
        from apps.stores.models import Store
        
        store = Store.objects.create(
            name='My Test Store',
            owner=self.user
        )
        
        self.assertEqual(store.slug, 'my-test-store')


class TestStoreSettings(TestCase):
    """Test StoreSettings model"""
    
    def setUp(self):
        """Set up test data"""
        from core.services.user import UserService
        self.user = UserService.create_user(
            email='test@example.com',
            password='testpass123'
        )
        from apps.stores.models import Store
        
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.user
        )
    
    def test_create_settings(self):
        """Test creating store settings"""
        from apps.stores.models import StoreSettings
        
        settings = StoreSettings.objects.create(
            store=self.store,
            site_name='My Store'
        )
        
        self.assertEqual(settings.site_name, 'My Store')
        self.assertEqual(settings.currency, 'USD')
