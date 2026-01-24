"""
Tests for customer ecommerce API v2.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.stores.models import Store
from apps.public.ecommerce.models import (
    Product, ProductVariant, Cart, CartItem, Order, Customer
)
from ..serializers import CustomerProductSerializer, CustomerCartSerializer, CustomerOrderSerializer

User = get_user_model()


class CustomerEcommerceAPITests(APITestCase):
    """Test the customer ecommerce API."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.store = Store.objects.create(
            name='Test Store',
            domain='test-store.example.com',
            is_active=True
        )
        
        # Create test user
        self.user = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Customer'
        )
        self.store.users.add(self.user)
        
        # Create customer profile
        self.customer = Customer.objects.create(
            user=self.user,
            store=self.store,
            email=self.user.email,
            first_name=self.user.first_name,
            last_name=self.user.last_name
        )
        
        # Create test product
        self.product = Product.objects.create(
            store=self.store,
            title='Test Product',
            description='Test Description',
            price='10.00',
            status='active',
            is_available=True
        )
        
        # Create test variant
        self.variant = ProductVariant.objects.create(
            product=self.product,
            title='Variant 1',
            sku='TEST123',
            price_override='10.00',
            inventory_quantity=10
        )
        
        # Create test cart
        self.cart = Cart.objects.create(
            store=self.store,
            user=self.user,
            status='active'
        )
        
        # Create test order
        self.order = Order.objects.create(
            store=self.store,
            customer=self.customer,
            order_number='1001',
            email=self.user.email,
            financial_status='paid',
            fulfillment_status='fulfilled',
            total_price='10.00',
            subtotal_price='10.00',
            total_tax='0.00',
            total_discounts='0.00',
            currency='USD'
        )
        
        # Authenticate the test client
        self.client.force_authenticate(user=self.user)
        
        # Set store in session
        self.client.credentials(HTTP_X_STORE_ID=self.store.id)
    
    def test_retrieve_products(self):
        """Test retrieving products."""
        url = reverse('customer_ecommerce_v2:product-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('results', res.data)
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['title'], self.product.title)
    
    def test_retrieve_single_product(self):
        """Test retrieving a single product."""
        url = reverse('customer_ecommerce_v2:product-detail', args=[self.product.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], str(self.product.id))
        self.assertEqual(res.data['title'], self.product.title)
    
    def test_get_cart(self):
        """Test retrieving the customer's cart."""
        url = reverse('customer_ecommerce_v2:customer_cart-detail', args=['current'])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], str(self.cart.id))
    
    def test_add_item_to_cart(self):
        """Test adding an item to the cart."""
        url = reverse('customer_ecommerce_v2:customer_cart-add-item', args=[self.cart.id])
        data = {
            'product_id': self.product.id,
            'variant_id': self.variant.id,
            'quantity': 1
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('items', res.data)
        self.assertEqual(len(res.data['items']), 1)
        self.assertEqual(res.data['items'][0]['quantity'], 1)
    
    def test_get_orders(self):
        """Test retrieving customer orders."""
        url = reverse('customer_ecommerce_v2:customer_order-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['order_number'], self.order.order_number)
    
    def test_get_single_order(self):
        """Test retrieving a single order."""
        url = reverse('customer_ecommerce_v2:customer_order-detail', args=[self.order.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], str(self.order.id))
        self.assertEqual(res.data['order_number'], self.order.order_number)


class CustomerProductServiceTests(TestCase):
    """Test the CustomerProductService."""
    
    def setUp(self):
        """Set up test data."""
        self.store = Store.objects.create(
            name='Test Store',
            domain='test-store.example.com',
            is_active=True
        )
        
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.product1 = Product.objects.create(
            store=self.store,
            title='Test Product 1',
            price='10.00',
            status='active',
            is_available=True
        )
        
        self.product2 = Product.objects.create(
            store=self.store,
            title='Test Product 2',
            price='20.00',
            status='draft',  # Inactive product
            is_available=True
        )
        
        self.variant1 = ProductVariant.objects.create(
            product=self.product1,
            title='Variant 1',
            sku='TEST123',
            price_override='10.00',
            inventory_quantity=10
        )
    
    def test_get_available_products(self):
        """Test getting available products."""
        from ..services import CustomerProductService
        
        products = CustomerProductService.get_available_products(
            store=self.store,
            user=self.user
        )
        
        self.assertEqual(products.count(), 1)
        self.assertEqual(products.first().title, 'Test Product 1')
    
    def test_get_product_variants(self):
        """Test getting product variants."""
        from ..services import CustomerProductService
        
        variants = CustomerProductService.get_product_variants(
            product=self.product1,
            user=self.user
        )
        
        self.assertEqual(variants.count(), 1)
        self.assertEqual(variants.first().title, 'Variant 1')
