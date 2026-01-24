import pytest
from django.contrib.auth import get_user_model
from apps.stores.models import Store
from apps.public.ecommerce.models import Product, ProductVariant, Inventory, Payment, Order, PaymentMethod

User = get_user_model()

@pytest.fixture
def store_a(db):
    """Create store A using centralized service"""
    from core.services.user import UserService
    from core.services.store import StoreService
    
    user = UserService.create_user('user_a', email='a@example.com', password='pass123')
    return StoreService.create_store(name='Store A', slug='store-a', owner=user)

@pytest.fixture
def store_b(db):
    """Create store B using centralized service"""
    from core.services.user import UserService
    from core.services.store import StoreService
    
    user = UserService.create_user('user_b', email='b@example.com', password='pass123')
    return StoreService.create_store(name='Store B', slug='store-b', owner=user)

@pytest.mark.django_db
def test_product_store_isolation(store_a, store_b):
    """Test Product is isolated by store using centralized services"""
    from ..services import ProductService
    
    product_a = ProductService.create_product(store_a, title='Product A', sku='SKU-A')
    product_b = ProductService.create_product(store_b, title='Product B', sku='SKU-B')
    
    # Store A should only see its own products
    assert Product.objects.filter(store=store_a).count() == 1
    assert Product.objects.filter(store=store_b).count() == 1
    assert Product.objects.filter(store=store_a).first() == product_a
    assert Product.objects.filter(store=store_b).first() == product_b

@pytest.mark.django_db
def test_productvariant_store_isolation(store_a, store_b):
    """Test ProductVariant is isolated by store using centralized services"""
    from ..services import ProductService
    from ..models import ProductVariant
    
    product_a = ProductService.create_product(store_a, title='Product A', sku='SKU-A')
    variant_a = ProductVariant.objects.create(store=store_a, product=product_a, sku='SKU-A-V1')
    
    product_b = ProductService.create_product(store_b, title='Product B', sku='SKU-B')
    variant_b = ProductVariant.objects.create(store=store_b, product=product_b, sku='SKU-B-V1')
    
    # Store A should only see its own variants
    assert ProductVariant.objects.filter(store=store_a).count() == 1
    assert ProductVariant.objects.filter(store=store_b).count() == 1
    assert ProductVariant.objects.filter(store=store_a).first() == variant_a
    assert ProductVariant.objects.filter(store=store_b).first() == variant_b

@pytest.mark.django_db
def test_inventory_store_isolation(store_a, store_b):
    """Test Inventory is isolated by store using centralized services"""
    from ..services import ProductService
    from ..models import Inventory
    
    product_a = ProductService.create_product(store_a, title='Product A', sku='SKU-A')
    inventory_a = Inventory.objects.create(store=store_a, product=product_a)
    
    product_b = ProductService.create_product(store_b, title='Product B', sku='SKU-B')
    inventory_b = Inventory.objects.create(store=store_b, product=product_b)
    
    # Store A should only see its own inventory
    assert Inventory.objects.filter(store=store_a).count() == 1
    assert Inventory.objects.filter(store=store_b).count() == 1
    assert Inventory.objects.filter(store=store_a).first() == inventory_a
    assert Inventory.objects.filter(store=store_b).first() == inventory_b

@pytest.mark.django_db
def test_payment_store_isolation(store_a, store_b):
    """Test Payment is isolated by store using centralized services"""
    from ..services import OrderService
    from ..models import Order, PaymentMethod, Payment
    
    # Create orders and payment methods using centralized services
    order_a = OrderService.create_order(store_a, None, {'subtotal': 100, 'total': 100})
    order_b = OrderService.create_order(store_b, None, {'subtotal': 200, 'total': 200})
    
    payment_method_a = PaymentMethod.objects.create(store=store_a, name='Credit Card', provider='stripe')
    payment_method_b = PaymentMethod.objects.create(store=store_b, name='Credit Card', provider='stripe')
    
    payment_a = Payment.objects.create(store=store_a, order=order_a, payment_method=payment_method_a, amount=100)
    payment_b = Payment.objects.create(store=store_b, order=order_b, payment_method=payment_method_b, amount=200)
    
    # Store A should only see its own payments
    assert Payment.objects.filter(store=store_a).count() == 1
    assert Payment.objects.filter(store=store_b).count() == 1
    assert Payment.objects.filter(store=store_a).first() == payment_a
    assert Payment.objects.filter(store=store_b).first() == payment_b

@pytest.mark.django_db
def test_cross_store_ecommerce_data_leak(store_a, store_b):
    """Test that stores cannot access each other's ecommerce data using centralized services"""
    from ..services import ProductService
    from ..models import ProductVariant, Inventory
    
    product_a = ProductService.create_product(store_a, title='Product A', sku='SKU-A')
    variant_a = ProductVariant.objects.create(store=store_a, product=product_a, sku='SKU-A-V1')
    inventory_a = Inventory.objects.create(store=store_a, product=product_a)
    
    # Store B should not see Store A's data
    assert Product.objects.filter(store=store_b).count() == 0
    assert ProductVariant.objects.filter(store=store_b).count() == 0
    assert Inventory.objects.filter(store=store_b).count() == 0
    
    # Verify data exists for Store A
    assert Product.objects.filter(store=store_a).count() == 1
    assert ProductVariant.objects.filter(store=store_a).count() == 1
    assert Inventory.objects.filter(store=store_a).count() == 1
