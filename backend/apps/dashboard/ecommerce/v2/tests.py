"""
Tests for dashboard ecommerce API v2.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.utils import timezone
from decimal import Decimal

from apps.stores.models import Store
from apps.public.ecommerce.models import (
    Product, ProductVariant, Order, OrderItem, Cart, CartItem, Customer,
    Collection, Discount, InventoryItem, StockMovement
)

User = get_user_model()


class DashboardEcommerceAPITests(APITestCase):
    """Test the dashboard ecommerce API."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.store = Store.objects.create(
            name='Test Store',
            domain='test-store.example.com',
            is_active=True
        )
        
        # Create admin user
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        self.store.users.add(self.admin)
        
        # Create test customer
        self.customer = Customer.objects.create(
            store=self.store,
            email='customer@example.com',
            first_name='Test',
            last_name='Customer'
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
        
        # Create test order
        self.order = Order.objects.create(
            store=self.store,
            customer=self.customer,
            order_number='1001',
            email='customer@example.com',
            financial_status='paid',
            fulfillment_status='unfulfilled',
            total_price='10.00',
            subtotal_price='10.00',
            total_tax='0.00',
            total_discounts='0.00',
            currency='USD'
        )
        
        # Create test order item
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            variant=self.variant,
            title='Test Product - Variant 1',
            quantity=1,
            price='10.00',
            line_price='10.00'
        )
        
        # Create test collection
        self.collection = Collection.objects.create(
            store=self.store,
            title='Test Collection',
            handle='test-collection',
            description='Test Collection Description'
        )
        
        # Create test discount
        self.discount = Discount.objects.create(
            store=self.store,
            code='TEST10',
            discount_type='percentage',
            value=Decimal('10.00'),
            min_purchase_amount=Decimal('50.00'),
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30)
        )
        
        # Create test inventory item
        self.inventory_item = InventoryItem.objects.create(
            store=self.store,
            sku='INV001',
            title='Test Inventory Item',
            quantity=100,
            cost=Decimal('5.00')
        )
        
        # Create test stock movement
        self.stock_movement = StockMovement.objects.create(
            variant=self.variant,
            quantity=10,
            previous_quantity=0,
            new_quantity=10,
            note='Initial stock',
            user=self.admin
        )
        
        # Authenticate the test client
        self.client.force_authenticate(user=self.admin)
        
        # Set store in session
        self.client.credentials(HTTP_X_STORE_ID=self.store.id)
    
    def test_get_products(self):
        """Test retrieving products."""
        url = reverse('dashboard_ecommerce_v2:dashboard_product-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['title'], self.product.title)
    
    def test_create_product(self):
        """Test creating a product."""
        url = reverse('dashboard_ecommerce_v2:dashboard_product-list')
        data = {
            'title': 'New Test Product',
            'description': 'New Test Description',
            'price': '19.99',
            'status': 'active',
            'is_available': True,
            'variants': [
                {
                    'title': 'New Variant 1',
                    'sku': 'NEW123',
                    'price_override': '19.99',
                    'inventory_quantity': 10,
                    'inventory_policy': 'deny',
                    'barcode': '1234567890123',
                    'weight': '0.5',
                    'weight_unit': 'kg',
                    'option1': 'Default',
                    'position': 1
                }
            ]
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['title'], 'New Test Product')
        self.assertEqual(len(res.data['variants']), 1)
        self.assertEqual(res.data['variants'][0]['title'], 'New Variant 1')
    
    def test_get_orders(self):
        """Test retrieving orders."""
        url = reverse('dashboard_ecommerce_v2:dashboard_order-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['order_number'], self.order.order_number)
    
    def test_update_order_status(self):
        """Test updating an order status."""
        url = reverse('dashboard_ecommerce_v2:dashboard_order-update-status', args=[self.order.id])
        data = {'status': 'fulfilled'}
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['financial_status'], 'fulfilled')


class DashboardProductServiceTests(TestCase):
    """Test the DashboardProductService."""
    
    def setUp(self):
        """Set up test data."""
        self.store = Store.objects.create(
            name='Test Store',
            domain='test-store.example.com',
            is_active=True
        )
        
        self.user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.product = Product.objects.create(
            store=self.store,
            title='Test Product',
            price='10.00',
            status='active',
            is_available=True
        )
        
        self.variant = ProductVariant.objects.create(
            product=self.product,
            title='Variant 1',
            sku='TEST123',
            price_override='10.00',
            inventory_quantity=10
        )
    
    def test_create_product(self):
        """Test creating a product with variants."""
        from ..services import DashboardProductService
        
        data = {
            'title': 'New Test Product',
            'description': 'New Test Description',
            'price': '19.99',
            'status': 'active',
            'is_available': True,
            'variants': [
                {
                    'title': 'New Variant 1',
                    'sku': 'NEW123',
                    'price_override': '19.99',
                    'inventory_quantity': 10
                }
            ]
        }
        
        product = DashboardProductService.create_product(
            store=self.store,
            user=self.user,
            data=data
        )
        
        self.assertEqual(product.title, 'New Test Product')
        self.assertEqual(product.variants.count(), 1)
        self.assertEqual(product.variants.first().title, 'New Variant 1')
    
    def test_update_product(self):
        """Test updating a product with variants."""
        from ..services import DashboardProductService
        
        data = {
            'title': 'Updated Test Product',
            'description': 'Updated Description',
            'variants': [
                {
                    'id': self.variant.id,
                    'title': 'Updated Variant',
                    'sku': 'UPDATED123',
                    'price_override': '15.00',
                    'inventory_quantity': 20
                },
                {
                    'title': 'New Variant 2',
                    'sku': 'NEW456',
                    'price_override': '25.00',
                    'inventory_quantity': 5
                }
            ]
        }
        
        product = DashboardProductService.update_product(
            product=self.product,
            user=self.user,
            data=data
        )
        
        self.assertEqual(product.title, 'Updated Test Product')
        self.assertEqual(product.variants.count(), 2)
        
        # Check updated variant
        updated_variant = product.variants.get(id=self.variant.id)
        self.assertEqual(updated_variant.title, 'Updated Variant')
        self.assertEqual(str(updated_variant.price_override), '15.00')
        
        # Check new variant
        new_variant = product.variants.exclude(id=self.variant.id).first()
        self.assertEqual(new_variant.title, 'New Variant 2')
        self.assertEqual(str(new_variant.price_override), '25.00')
