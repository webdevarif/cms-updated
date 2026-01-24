"""
Tests for public ecommerce API v2.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.stores.models import Store
from ..models import Product, ProductVariant, Cart, CartItem, Order

User = get_user_model()


class PublicEcommerceAPITests(TestCase):
    """Test the public ecommerce API."""

    def setUp(self):
        """Set up test data using centralized services."""
        self.client = APIClient()
        
        # Use centralized store creation
        from core.services.store import StoreService
        self.store = StoreService.create_store(
            name='Test Store',
            domain='test-store.example.com',
            is_active=True
        )
        
        # Use centralized product creation
        from ..services import ProductService
        self.product = ProductService.create_product(
            store=self.store,
            title='Test Product',
            description='Test Description',
            sku='TEST-001',
            base_price=99.99,
            status='active',
            is_available=True
        )
        
        # Use centralized variant creation
        from ..models import ProductVariant
        self.variant = ProductVariant.objects.create(
            product=self.product,
            title='Variant 1',
            sku='TEST123',
            price=99.99
        )

    def test_retrieve_products(self):
        """Test retrieving products."""
        url = reverse('ecommerce_v2:product-list')
        res = self.client.get(url, HTTP_X_STORE_ID=self.store.id)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('results', res.data)
        self.assertEqual(len(res.data['results']), 1)

    def test_retrieve_single_product(self):
        """Test retrieving a single product."""
        url = reverse('ecommerce_v2:product-detail', args=[self.product.id])
        res = self.client.get(url, HTTP_X_STORE_ID=self.store.id)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], str(self.product.id))

    def test_create_cart(self):
        """Test creating a cart."""
        url = reverse('ecommerce_v2:cart-list')
        data = {}
        res = self.client.post(url, data, HTTP_X_STORE_ID=self.store.id)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', res.data)
        self.assertEqual(res.data['status'], 'active')

    def test_add_item_to_cart(self):
        """Test adding an item to cart."""
        # First create a cart
        cart_url = reverse('ecommerce_v2:cart-list')
        cart_res = self.client.post(cart_url, {}, HTTP_X_STORE_ID=self.store.id)
        cart_id = cart_res.data['id']
        
        # Add item to cart
        add_item_url = reverse('ecommerce_v2:cart-add-item', args=[cart_id])
        data = {
            'product_id': self.product.id,
            'variant_id': self.variant.id,
            'quantity': 1
        }
        res = self.client.post(add_item_url, data, HTTP_X_STORE_ID=self.store.id)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('items', res.data)
        self.assertEqual(len(res.data['items']), 1)
        self.assertEqual(res.data['items'][0]['quantity'], 1)
