"""
Test fixtures for accounts app.
"""
import pytest
from django.contrib.auth import get_user_model
from core.services.user import UserService
from apps.stores.models import Store
from apps.accounts.models import StoreUser, Role, UserPreferences

User = get_user_model()


@pytest.fixture
def user():
    """Create a regular user fixture"""
    return UserService.create_user(
        email='test@example.com',
        username='testuser',
        password='testpass123',
        first_name='John',
        last_name='Doe'
    )


@pytest.fixture
def admin_user():
    """Create an admin user fixture"""
    return UserService.create_user(
        email='admin@example.com',
        username='admin',
        password='adminpass123',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def store():
    """Create a store fixture"""
    owner = UserService.create_user(
        email='owner@example.com',
        username='owner',
        password='ownerpass123'
    )
    
    return Store.objects.create(
        name='Test Store',
        slug='test-store',
        owner=owner
    )


@pytest.fixture
def store_with_owner():
    """Create a store with owner and return both"""
    owner = UserService.create_user(
        email='owner@example.com',
        username='owner',
        password='ownerpass123'
    )
    
    store = Store.objects.create(
        name='Test Store',
        slug='test-store',
        owner=owner
    )
    
    # Create store user relationship
    StoreUser.objects.create(
        user=owner,
        store=store,
        role='owner',
        is_active=True
    )
    
    return store, owner


@pytest.fixture
def store_user(user, store):
    """Create a store user fixture"""
    return StoreUser.objects.create(
        user=user,
        store=store,
        role='customer',
        is_active=True
    )


@pytest.fixture
def store_admin(store_with_owner):
    """Create a store admin fixture"""
    store, owner = store_with_owner
    
    admin = UserService.create_user(
        email='admin@store.com',
        username='storeadmin',
        password='adminpass123'
    )
    
    return StoreUser.objects.create(
        user=admin,
        store=store,
        role='admin',
        is_active=True
    )


@pytest.fixture
def store_staff(store_with_owner):
    """Create a store staff fixture"""
    store, owner = store_with_owner
    
    staff = UserService.create_user(
        email='staff@store.com',
        username='storestaff',
        password='staffpass123'
    )
    
    return StoreUser.objects.create(
        user=staff,
        store=store,
        role='staff',
        is_active=True
    )


@pytest.fixture
def store_customer(store_with_owner):
    """Create a store customer fixture"""
    store, owner = store_with_owner
    
    customer = UserService.create_user(
        email='customer@store.com',
        username='storecustomer',
        password='customerpass123'
    )
    
    return StoreUser.objects.create(
        user=customer,
        store=store,
        role='customer',
        is_active=True
    )


@pytest.fixture
def user_preferences(user):
    """Create user preferences fixture"""
    return UserPreferences.objects.create(
        user=user,
        email_notifications=False,
        theme='dark',
        language='es',
        show_email=True,
        show_online_status=False
    )


@pytest.fixture
def store_role(store_with_owner):
    """Create a store role fixture"""
    store, owner = store_with_owner
    
    return Role.objects.create(
        store=store,
        name='custom_role',
        permissions={
            'can_view_reports': True,
            'can_manage_products': False,
            'can_manage_orders': True
        },
        is_active=True
    )


@pytest.fixture
def multiple_stores_with_users():
    """Create multiple stores with different user types"""
    # Store A
    owner_a = UserService.create_user(
        email='owner_a@example.com',
        username='owner_a',
        password='pass123'
    )
    store_a = Store.objects.create(
        name='Store A',
        slug='store-a',
        owner=owner_a
    )
    
    admin_a = UserService.create_user(
        email='admin_a@example.com',
        username='admin_a',
        password='pass123'
    )
    StoreUser.objects.create(user=admin_a, store=store_a, role='admin')
    
    customer_a = UserService.create_user(
        email='customer_a@example.com',
        username='customer_a',
        password='pass123'
    )
    StoreUser.objects.create(user=customer_a, store=store_a, role='customer')
    
    # Store B
    owner_b = UserService.create_user(
        email='owner_b@example.com',
        username='owner_b',
        password='pass123'
    )
    store_b = Store.objects.create(
        name='Store B',
        slug='store-b',
        owner=owner_b
    )
    
    admin_b = UserService.create_user(
        email='admin_b@example.com',
        username='admin_b',
        password='pass123'
    )
    StoreUser.objects.create(user=admin_b, store=store_b, role='admin')
    
    customer_b = UserService.create_user(
        email='customer_b@example.com',
        username='customer_b',
        password='pass123'
    )
    StoreUser.objects.create(user=customer_b, store=store_b, role='customer')
    
    return {
        'store_a': store_a,
        'store_b': store_b,
        'owners': [owner_a, owner_b],
        'admins': [admin_a, admin_b],
        'customers': [customer_a, customer_b]
    }


@pytest.fixture
def authenticated_client(user):
    """Create an authenticated client fixture"""
    from rest_framework.test import APIClient
    from apps.accounts.v2.services import AuthService
    
    client = APIClient()
    tokens = AuthService.generate_token(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    return client


@pytest.fixture
def store_admin_client(store_admin):
    """Create an authenticated store admin client"""
    from rest_framework.test import APIClient
    from apps.accounts.v2.services import AuthService
    
    client = APIClient()
    tokens = AuthService.generate_token(store_admin.user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    return client


@pytest.fixture
def store_customer_client(store_customer):
    """Create an authenticated store customer client"""
    from rest_framework.test import APIClient
    from apps.accounts.v2.services import AuthService
    
    client = APIClient()
    tokens = AuthService.generate_token(store_customer.user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    return client


@pytest.fixture
def mock_email_service():
    """Mock email service for testing"""
    from unittest.mock import Mock, patch
    
    with patch('apps.smtp.services.SmtpEmailService.send_email_async.delay') as mock:
        mock.return_value = Mock()
        yield mock


@pytest.fixture
def mock_log_event():
    """Mock log event for testing"""
    from unittest.mock import Mock, patch
    
    with patch('core.libs.logging.log_event_async.delay') as mock:
        mock.return_value = Mock()
        yield mock
