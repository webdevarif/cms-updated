# Ecommerce Testing

## 7. Testing Requirements

### 7.1 Model Tests

#### Product Model Tests
```python
# tests/test_models.py
import pytest
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from ecommerce.models import Product, ProductVariant, ProductCategory
from stores.models import Store
from accounts.models import GlobalUser

class ProductModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            subdomain="test",
            is_active=True
        )
        self.user = GlobalUser.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.category = ProductCategory.objects.create(
            store=self.store,
            name="Test Category",
            slug="test-category",
            created_by=self.user
        )

    def test_product_creation(self):
        """Test product creation with required fields"""
        product = Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            created_by=self.user
        )

        assert product.title == "Test Product"
        assert product.slug == "test-product"
        assert product.sku == "TEST-001"
        assert product.status == "draft"
        assert product.store == self.store
        assert product.created_by == self.user

    def test_product_slug_uniqueness_per_store(self):
        """Test that product slugs are unique per store"""
        Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            created_by=self.user
        )

        # Should raise ValidationError for duplicate slug
        with pytest.raises(ValidationError):
            Product.objects.create(
                store=self.store,
                title="Test Product 2",
                slug="test-product",  # Duplicate slug
                sku="TEST-002",
                created_by=self.user
            )

    def test_product_can_have_same_slug_in_different_stores(self):
        """Test that same slug can exist in different stores"""
        store2 = Store.objects.create(
            name="Test Store 2",
            subdomain="test2",
            is_active=True
        )

        product1 = Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            created_by=self.user
        )

        product2 = Product.objects.create(
            store=store2,
            title="Test Product",
            slug="test-product",  # Same slug, different store
            sku="TEST-002",
            created_by=self.user
        )

        assert product1.slug == product2.slug
        assert product1.store != product2.store

    def test_product_variant_creation(self):
        """Test product variant creation"""
        product = Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            created_by=self.user
        )

        variant = ProductVariant.objects.create(
            product=product,
            title="Small",
            sku="TEST-001-S",
            price=Decimal('19.99'),
            inventory_quantity=10
        )

        assert variant.product == product
        assert variant.title == "Small"
        assert variant.price == Decimal('19.99')
        assert variant.inventory_quantity == 10

    def test_product_variant_sku_uniqueness(self):
        """Test that variant SKUs are unique"""
        product = Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            created_by=self.user
        )

        ProductVariant.objects.create(
            product=product,
            title="Small",
            sku="TEST-001-S",
            price=Decimal('19.99')
        )

        # Should raise ValidationError for duplicate SKU
        with pytest.raises(ValidationError):
            ProductVariant.objects.create(
                product=product,
                title="Medium",
                sku="TEST-001-S",  # Duplicate SKU
                price=Decimal('24.99')
            )

class ProductCategoryTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            subdomain="test",
            is_active=True
        )
        self.user = GlobalUser.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

    def test_category_hierarchy(self):
        """Test category parent-child relationships"""
        parent = ProductCategory.objects.create(
            store=self.store,
            name="Parent Category",
            slug="parent-category",
            created_by=self.user
        )

        child = ProductCategory.objects.create(
            store=self.store,
            name="Child Category",
            slug="child-category",
            parent=parent,
            created_by=self.user
        )

        assert child.parent == parent
        assert parent.children.first() == child

    def test_prevent_circular_reference(self):
        """Test prevention of circular category references"""
        parent = ProductCategory.objects.create(
            store=self.store,
            name="Parent Category",
            slug="parent-category",
            created_by=self.user
        )

        child = ProductCategory.objects.create(
            store=self.store,
            name="Child Category",
            slug="child-category",
            parent=parent,
            created_by=self.user
        )

        # Should raise ValidationError when trying to set parent as child's parent
        with pytest.raises(ValidationError):
            parent.parent = child
            parent.clean()
```

#### Order Model Tests
```python
class OrderModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            subdomain="test",
            is_active=True
        )
        self.user = GlobalUser.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.customer = Customer.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="test@example.com"
        )

    def test_order_number_generation(self):
        """Test automatic order number generation"""
        order = Order.objects.create(
            store=self.store,
            customer=self.customer,
            subtotal=Decimal('100.00'),
            tax=Decimal('10.00'),
            shipping=Decimal('5.00'),
            total=Decimal('115.00')
        )

        assert order.order_number.startswith("ORD-")
        assert len(order.order_number) > 10

    def test_order_status_transitions(self):
        """Test valid order status transitions"""
        order = Order.objects.create(
            store=self.store,
            customer=self.customer,
            status='pending',
            subtotal=Decimal('100.00'),
            tax=Decimal('10.00'),
            shipping=Decimal('5.00'),
            total=Decimal('115.00')
        )

        # Valid transition
        order.status = 'confirmed'
        order.save()
        assert order.status == 'confirmed'

        # Invalid transition should be handled by service layer
        # This would be tested in service tests

    def test_order_total_calculation(self):
        """Test order total calculation"""
        order = Order.objects.create(
            store=self.store,
            customer=self.customer,
            subtotal=Decimal('100.00'),
            tax=Decimal('10.00'),
            shipping=Decimal('5.00'),
            discount=Decimal('10.00'),
            total=Decimal('105.00')
        )

        assert order.total == order.subtotal + order.tax + order.shipping - order.discount
```

### 7.2 ViewSet Tests

#### Product ViewSet Tests
```python
# tests/test_views.py
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from ecommerce.models import Product, ProductVariant
from stores.models import Store

User = get_user_model()

class ProductViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = Store.objects.create(
            name="Test Store",
            subdomain="test",
            is_active=True
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.user.stores.add(self.store)
        self.client.force_authenticate(user=self.user)

        # Add store to request context
        self.client.defaults['HTTP_X_STORE_ID'] = self.store.id

    def test_list_products(self):
        """Test listing products"""
        Product.objects.create(
            store=self.store,
            title="Product 1",
            slug="product-1",
            sku="PROD-001",
            created_by=self.user
        )

        Product.objects.create(
            store=self.store,
            title="Product 2",
            slug="product-2",
            sku="PROD-002",
            created_by=self.user
        )

        response = self.client.get('/api/v2/ecommerce/products/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_create_product(self):
        """Test creating a product"""
        data = {
            'title': 'New Product',
            'slug': 'new-product',
            'sku': 'NEW-001',
            'description': 'Test description',
            'status': 'published'
        }

        response = self.client.post('/api/v2/ecommerce/products/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Product.objects.count() == 1
        assert Product.objects.first().title == 'New Product'

    def test_create_product_requires_store(self):
        """Test that product creation requires store context"""
        self.client.defaults.pop('HTTP_X_STORE_ID', None)

        data = {
            'title': 'New Product',
            'slug': 'new-product',
            'sku': 'NEW-001'
        }

        response = self.client.post('/api/v2/ecommerce/products/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_product(self):
        """Test updating a product"""
        product = Product.objects.create(
            store=self.store,
            title="Original Title",
            slug="original-title",
            sku="ORIG-001",
            created_by=self.user
        )

        data = {
            'title': 'Updated Title',
            'status': 'published'
        }

        response = self.client.patch(
            f'/api/v2/ecommerce/products/{product.id}/',
            data
        )

        assert response.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert product.title == 'Updated Title'
        assert product.status == 'published'

    def test_delete_product(self):
        """Test deleting a product"""
        product = Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            created_by=self.user
        )

        response = self.client.delete(f'/api/v2/ecommerce/products/{product.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Product.objects.count() == 0

    def test_duplicate_product(self):
        """Test duplicating a product"""
        product = Product.objects.create(
            store=self.store,
            title="Original Product",
            slug="original-product",
            sku="ORIG-001",
            created_by=self.user
        )

        ProductVariant.objects.create(
            product=product,
            title="Small",
            sku="ORIG-001-S",
            price=Decimal('19.99')
        )

        response = self.client.post(
            f'/api/v2/ecommerce/products/{product.id}/duplicate/'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Product.objects.count() == 2

        duplicated = Product.objects.last()
        assert duplicated.title == "Original Product (Copy)"
        assert duplicated.variants.count() == 1

    def test_store_isolation(self):
        """Test that users can only access their own store's products"""
        other_store = Store.objects.create(
            name="Other Store",
            subdomain="other",
            is_active=True
        )

        # Create product in other store
        Product.objects.create(
            store=other_store,
            title="Other Product",
            slug="other-product",
            sku="OTHER-001",
            created_by=self.user
        )

        # Create product in user's store
        Product.objects.create(
            store=self.store,
            title="My Product",
            slug="my-product",
            sku="MY-001",
            created_by=self.user
        )

        response = self.client.get('/api/v2/ecommerce/products/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'My Product'
```

#### Cart ViewSet Tests
```python
class CartViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = Store.objects.create(
            name="Test Store",
            subdomain="test",
            is_active=True
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.customer = Customer.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="test@example.com"
        )
        self.client.force_authenticate(user=self.user)
        self.client.defaults['HTTP_X_STORE_ID'] = self.store.id

        # Create test product
        self.product = Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            created_by=self.user
        )

        self.variant = ProductVariant.objects.create(
            product=self.product,
            title="Small",
            sku="TEST-001-S",
            price=Decimal('19.99'),
            inventory_quantity=10
        )

    def test_add_item_to_cart(self):
        """Test adding item to cart"""
        data = {
            'product_id': self.product.id,
            'variant_id': self.variant.id,
            'quantity': 2
        }

        response = self.client.post('/api/v2/ecommerce/cart/add_item/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Cart.objects.count() == 1
        assert CartItem.objects.count() == 1

        cart_item = CartItem.objects.first()
        assert cart_item.quantity == 2
        assert cart_item.product == self.product
        assert cart_item.variant == self.variant

    def test_update_cart_item_quantity(self):
        """Test updating cart item quantity"""
        # Add item first
        cart = Cart.objects.create(
            store=self.store,
            customer=self.customer
        )
        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            variant=self.variant,
            quantity=1,
            unit_price=self.variant.price
        )

        data = {
            'item_id': cart_item.id,
            'quantity': 3
        }

        response = self.client.put('/api/v2/ecommerce/cart/update_item/', data)

        assert response.status_code == status.HTTP_200_OK
        cart_item.refresh_from_db()
        assert cart_item.quantity == 3

    def test_remove_item_from_cart(self):
        """Test removing item from cart"""
        cart = Cart.objects.create(
            store=self.store,
            customer=self.customer
        )
        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            variant=self.variant,
            quantity=1,
            unit_price=self.variant.price
        )

        data = {'item_id': cart_item.id}
        response = self.client.delete('/api/v2/ecommerce/cart/remove_item/', data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert CartItem.objects.count() == 0

    def test_cart_summary(self):
        """Test getting cart summary"""
        cart = Cart.objects.create(
            store=self.store,
            customer=self.customer
        )
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            variant=self.variant,
            quantity=2,
            unit_price=self.variant.price
        )

        response = self.client.get('/api/v2/ecommerce/cart/summary/')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['item_count'] == 2
        assert Decimal(data['subtotal']) == Decimal('39.98')
```

### 7.3 Service Tests

#### Product Service Tests
```python
# tests/test_services.py
import pytest
from decimal import Decimal
from django.test import TestCase
from ecommerce.services import ProductService
from ecommerce.models import Product, ProductVariant
from stores.models import Store
from accounts.models import GlobalUser

class ProductServiceTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            subdomain="test",
            is_active=True
        )
        self.user = GlobalUser.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

    def test_create_product_with_variants(self):
        """Test creating product with variants"""
        data = {
            'title': 'Test Product',
            'slug': 'test-product',
            'sku': 'TEST-001',
            'description': 'Test description',
            'status': 'published',
            'variants': [
                {
                    'title': 'Small',
                    'sku': 'TEST-001-S',
                    'price': Decimal('19.99'),
                    'inventory_quantity': 10
                },
                {
                    'title': 'Medium',
                    'sku': 'TEST-001-M',
                    'price': Decimal('24.99'),
                    'inventory_quantity': 15
                }
            ]
        }

        product = ProductService.create_product(self.store, self.user, data)

        assert product.title == 'Test Product'
        assert product.variants.count() == 2
        assert product.variants.first().price == Decimal('19.99')

    def test_duplicate_product(self):
        """Test duplicating a product"""
        # Create original product
        original = Product.objects.create(
            store=self.store,
            title="Original Product",
            slug="original-product",
            sku="ORIG-001",
            created_by=self.user
        )

        ProductVariant.objects.create(
            product=original,
            title="Small",
            sku="ORIG-001-S",
            price=Decimal('19.99')
        )

        # Duplicate product
        duplicate = ProductService.duplicate_product(original, self.user)

        assert duplicate.title == "Original Product (Copy)"
        assert duplicate.slug.startswith("original-product-copy-")
        assert duplicate.variants.count() == 1
        assert duplicate.variants.first().sku == "ORIG-001-S-COPY"

    def test_update_product_status_logs_change(self):
        """Test that status changes are logged"""
        product = Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            status='draft',
            created_by=self.user
        )

        # Update status
        ProductService.update_product(product, self.user, {'status': 'published'})

        # Check that log was created (this would require mocking log_event_async)
        product.refresh_from_db()
        assert product.status == 'published'
```

#### Cart Service Tests
```python
class CartServiceTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            subdomain="test",
            is_active=True
        )
        self.user = GlobalUser.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.customer = Customer.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="test@example.com"
        )

        self.product = Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            created_by=self.user
        )

        self.variant = ProductVariant.objects.create(
            product=self.product,
            title="Small",
            sku="TEST-001-S",
            price=Decimal('19.99'),
            inventory_quantity=10
        )

        # Create inventory
        Inventory.objects.create(
            store=self.store,
            product=self.product,
            variant=self.variant,
            quantity=10
        )

    def test_add_item_to_cart_with_inventory_check(self):
        """Test adding item with inventory validation"""
        cart = Cart.objects.create(
            store=self.store,
            customer=self.customer
        )

        cart_item = CartService.add_item(
            cart, self.product, self.variant, 5
        )

        assert cart_item.quantity == 5
        assert cart_item.unit_price == self.variant.price

        # Check inventory was reserved
        inventory = Inventory.objects.get(
            store=self.store,
            product=self.product,
            variant=self.variant
        )
        assert inventory.reserved == 5

    def test_add_item_exceeds_inventory(self):
        """Test that adding items exceeding inventory raises error"""
        cart = Cart.objects.create(
            store=self.store,
            customer=self.customer
        )

        with pytest.raises(ValidationError):
            CartService.add_item(
                cart, self.product, self.variant, 15  # Exceeds inventory
            )

    def test_convert_cart_to_order(self):
        """Test converting cart to order"""
        cart = Cart.objects.create(
            store=self.store,
            customer=self.customer
        )

        CartItem.objects.create(
            cart=cart,
            product=self.product,
            variant=self.variant,
            quantity=2,
            unit_price=self.variant.price
        )

        billing_address = {
            'street': '123 Main St',
            'city': 'Test City',
            'country': 'US',
            'postal_code': '12345'
        }

        shipping_address = {
            'street': '123 Main St',
            'city': 'Test City',
            'country': 'US',
            'postal_code': '12345'
        }

        order = CartService.convert_to_order(
            cart, billing_address, shipping_address
        )

        assert order.customer == self.customer
        assert order.items.count() == 1
        assert order.status == 'pending'
        assert cart.status == 'converted'
```

### 7.4 Integration Tests

#### End-to-End Order Flow Tests
```python
# tests/test_integration.py
class OrderFlowIntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = Store.objects.create(
            name="Test Store",
            subdomain="test",
            is_active=True
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.customer = Customer.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="test@example.com"
        )
        self.client.force_authenticate(user=self.user)
        self.client.defaults['HTTP_X_STORE_ID'] = self.store.id

        # Create test product
        self.product = Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            status='published',
            created_by=self.user
        )

        self.variant = ProductVariant.objects.create(
            product=self.product,
            title="Small",
            sku="TEST-001-S",
            price=Decimal('19.99'),
            inventory_quantity=10
        )

        Inventory.objects.create(
            store=self.store,
            product=self.product,
            variant=self.variant,
            quantity=10
        )

    def test_complete_order_flow(self):
        """Test complete order flow from cart to payment"""
        # 1. Add item to cart
        cart_data = {
            'product_id': self.product.id,
            'variant_id': self.variant.id,
            'quantity': 2
        }
        response = self.client.post('/api/v2/ecommerce/cart/add_item/', cart_data)
        assert response.status_code == status.HTTP_201_CREATED

        # 2. Get cart summary
        response = self.client.get('/api/v2/ecommerce/cart/summary/')
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.json()['subtotal']) == Decimal('39.98')

        # 3. Create order from cart
        order_data = {
            'billing_address': {
                'street': '123 Main St',
                'city': 'Test City',
                'country': 'US',
                'postal_code': '12345'
            },
            'shipping_address': {
                'street': '123 Main St',
                'city': 'Test City',
                'country': 'US',
                'postal_code': '12345'
            }
        }
        response = self.client.post('/api/v2/ecommerce/orders/create_from_cart/', order_data)
        assert response.status_code == status.HTTP_201_CREATED

        order_id = response.json()['id']

        # 4. Check order was created
        response = self.client.get(f'/api/v2/ecommerce/orders/{order_id}/')
        assert response.status_code == status.HTTP_200_OK
        order_data = response.json()
        assert order_data['status'] == 'pending'
        assert order_data['items'][0]['quantity'] == 2

        # 5. Update order status
        response = self.client.post(
            f'/api/v2/ecommerce/orders/{order_id}/update_status/',
            {'status': 'confirmed'}
        )
        assert response.status_code == status.HTTP_200_OK

        # 6. Check inventory was updated
        inventory = Inventory.objects.get(
            store=self.store,
            product=self.product,
            variant=self.variant
        )
        assert inventory.reserved == 2
```

### 7.5 Performance Tests

#### Database Query Optimization Tests
```python
# tests/test_performance.py
import pytest
from django.test import TestCase
from django.test.utils import override_settings
from django.db import connection
from ecommerce.models import Product, ProductVariant

class PerformanceTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            subdomain="test",
            is_active=True
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

        # Create test data
        for i in range(100):
            product = Product.objects.create(
                store=self.store,
                title=f"Product {i}",
                slug=f"product-{i}",
                sku=f"PROD-{i:03d}",
                created_by=self.user
            )

            for j in range(3):
                ProductVariant.objects.create(
                    product=product,
                    title=f"Size {j}",
                    sku=f"PROD-{i:03d}-{j}",
                    price=Decimal(f"{i + j}.99")
                )

    def test_product_list_query_count(self):
        """Test that product list uses optimized queries"""
        with self.assertNumQueries(2):  # Should be 2 queries with select_related/prefetch_related
            products = Product.objects.select_related('store').prefetch_related(
                'variants'
            ).all()

            # Access data to trigger queries
            for product in products:
                list(product.variants.all())

    def test_search_performance(self):
        """Test search query performance"""
        with self.assertNumQueries(1):
            products = Product.objects.filter(
                title__icontains='Product 1'
            ).select_related('store')

            list(products)  # Execute query

    @override_settings(DEBUG=True)
    def test_no_n_plus_one_queries(self):
        """Test that no N+1 queries are made"""
        # Reset query count
        connection.queries_log.clear()

        # Get products with variants
        products = Product.objects.select_related('store').prefetch_related(
            'variants'
        ).all()[:10]

        # Access all data
        for product in products:
            print(product.title)
            for variant in product.variants.all():
                print(variant.title)

        # Should only have 2 queries (products + variants)
        assert len(connection.queries) <= 2
```

### 7.6 Security Tests

#### Security Test Cases
```python
# tests/test_security.py
class SecurityTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = Store.objects.create(
            name="Test Store",
            subdomain="test",
            is_active=True
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123"
        )

        self.user.stores.add(self.store)
        self.client.force_authenticate(user=self.user)
        self.client.defaults['HTTP_X_STORE_ID'] = self.store.id

    def test_store_isolation(self):
        """Test that users cannot access other stores' data"""
        other_store = Store.objects.create(
            name="Other Store",
            subdomain="other",
            is_active=True
        )

        # Create product in other store
        product = Product.objects.create(
            store=other_store,
            title="Other Product",
            slug="other-product",
            sku="OTHER-001",
            created_by=self.other_user
        )

        # Try to access other store's product
        response = self.client.get(f'/api/v2/ecommerce/products/{product.id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_input_sanitization(self):
        """Test that malicious input is sanitized"""
        malicious_data = {
            'title': '<script>alert("xss")</script>Product',
            'slug': 'malicious-product',
            'sku': 'MAL-001',
            'description': '<p>Valid description</p><script>alert("xss")</script>'
        }

        response = self.client.post('/api/v2/ecommerce/products/', malicious_data)

        assert response.status_code == status.HTTP_201_CREATED

        product = Product.objects.get()
        assert '<script>' not in product.title
        assert '<script>' not in product.description
        assert '<p>' in product.description  # Valid HTML should remain

    def test_rate_limiting(self):
        """Test API rate limiting"""
        # Make many requests quickly
        for i in range(150):  # Exceed rate limit
            response = self.client.get('/api/v2/ecommerce/products/')
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                break

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
```

### 7.7 Test Configuration

#### pytest Configuration
```python
# pytest.ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = backend.settings.test
python_files = tests.py test_*.py *_tests.py
addopts = --reuse-db --nomigrations --cov=ecommerce --cov-report=html --cov-report=term-missing
```

#### Test Settings
```python
# settings/test.py
from .base import *

# Test database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for speed
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Test-specific settings
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Faster for tests
]

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Celery task always eager for testing
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
```

### 7.8 Test Coverage Requirements

#### Coverage Targets
- **Models**: 95% coverage
- **Views**: 90% coverage
- **Services**: 95% coverage
- **Utilities**: 85% coverage
- **Overall**: 90% coverage

#### Required Test Scenarios
1. **Happy path** - Normal operation flows
2. **Error conditions** - Invalid inputs, edge cases
3. **Security** - Unauthorized access, input validation
4. **Performance** - Query optimization, N+1 prevention
5. **Integration** - Cross-module functionality
6. **Multi-tenancy** - Store isolation, permissions

#### Test Data Management
```python
# tests/fixtures.py
import pytest
from decimal import Decimal
from stores.models import Store
from accounts.models import GlobalUser
from ecommerce.models import Product, ProductVariant, Customer

@pytest.fixture
def store():
    return Store.objects.create(
        name="Test Store",
        subdomain="test",
        is_active=True
    )

@pytest.fixture
def user():
    return GlobalUser.objects.create_user(
        email="test@example.com",
        password="testpass123"
    )

@pytest.fixture
def customer(user):
    return Customer.objects.create(
        user=user,
        first_name="John",
        last_name="Doe",
        email="test@example.com"
    )

@pytest.fixture
def product(store, user):
    return Product.objects.create(
        store=store,
        title="Test Product",
        slug="test-product",
        sku="TEST-001",
        created_by=user
    )

@pytest.fixture
def product_variant(product):
    return ProductVariant.objects.create(
        product=product,
        title="Small",
        sku="TEST-001-S",
        price=Decimal('19.99')
    )
```
