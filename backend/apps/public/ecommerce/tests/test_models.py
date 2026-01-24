"""
Tests for ecommerce models.
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestProductModel:
    """Test Product model"""
    
    def setUp(self):
        """Set up test data using centralized services"""
        from core.services.user import UserService
        from core.services.store import StoreService
        
        user = UserService.create_user(email='test@example.com', password='pass')
        self.store = StoreService.create_store(name='Test Store', owner=user)
        
        # Use centralized product creation
        from ..services import ProductService
        self.product = ProductService.create_product(
            store=self.store,
            title='Test Product',
            sku='TEST-001',
            base_price=99.99,
            status='active'
        )

    def test_product_creation(self):
        """Test product creation with required fields"""
        self.assertEqual(self.product.title, 'Test Product')
        self.assertEqual(self.product.sku, 'TEST-001')
        self.assertEqual(self.product.base_price, 99.99)
        self.assertEqual(self.product.status, 'active')
        self.assertEqual(self.product.store, self.store)

    def test_product_str_representation(self):
        """Test product string representation"""
        expected = f"{self.product.title} ({self.product.sku})"
        self.assertEqual(str(self.product), expected)


@pytest.mark.django_db
class TestCartModel:
    """Test Cart model"""
    
    def setUp(self):
        """Set up test data using centralized services"""
        from core.services.user import UserService
        from core.services.store import StoreService
        
        user = UserService.create_user(email='test@example.com', password='pass')
        self.store = StoreService.create_store(name='Test Store', owner=user)
        self.user = user
        
        # Use centralized product creation
        from ..services import ProductService
        self.product = ProductService.create_product(
            store=self.store,
            title='Test Product',
            sku='TEST-001',
            base_price=99.99,
            status='active'
        )

    def test_cart_creation(self):
        """Test cart creation using centralized services"""
        from ..services import CartService
        
        cart = CartService.get_or_create_cart(store=self.store, user=self.user)
        self.assertEqual(cart.store, self.store)
        self.assertEqual(cart.user, self.user)
        self.assertEqual(cart.status, 'active')
