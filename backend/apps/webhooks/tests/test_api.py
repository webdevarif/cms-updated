"""
API tests for webhooks module.
"""
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
import factory

User = get_user_model()


# FactoryBoy fixtures
class UserFactory(factory.django.DjangoModelFactory):
    """User factory for test data"""
    class Meta:
        model = User
        django_get_or_create = ('email',)
    
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    password = 'testpass123'


class StoreFactory(factory.django.DjangoModelFactory):
    """Store factory for test data"""
    class Meta:
        model = 'stores.Store'
        django_get_or_create = ('slug',)
    
    name = factory.Sequence(lambda n: f'Store {n}')
    slug = factory.Sequence(lambda n: f'store-{n}')
    owner = factory.SubFactory(UserFactory)
    store_type = 'ecommerce'


@pytest.mark.django_db
class WebhookViewSetTests:
    """Webhook viewset tests for all roles"""
    
    @pytest.fixture
    def admin_user(self):
        """Create admin user fixture"""
        return UserFactory(
            email='admin@example.com',
            is_staff=True,
            is_superuser=True
        )
    
    @pytest.fixture
    def store_owner(self):
        """Create store owner user fixture"""
        user = UserFactory(email='owner@example.com')
        store = StoreFactory(owner=user)
        return store
    
    @pytest.fixture
    def anonymous_client(self):
        """Create anonymous APIClient fixture"""
        return APIClient()
    
    @pytest.fixture
    def authenticated_client(self, admin_user):
        """Create authenticated APIClient fixture"""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        return client
    
    @pytest.fixture
    def webhook(self, store_owner):
        """Create webhook fixture"""
        from ..models import Webhook
        from core.services.webhook import WebhookService
        
        return WebhookService.create_webhook(
            store=store_owner,
            name='Test Webhook',
            url='https://example.com/webhook',
            events=['order.created']
        )
    
    # List endpoint tests
    def test_list_webhooks_as_anonymous(self, anonymous_client):
        """Test listing webhooks as anonymous"""
        response = anonymous_client.get('/v2/api/webhooks/')
        assert response.status_code == 200
    
    def test_list_webhooks_as_admin(self, authenticated_client):
        """Test listing webhooks as admin"""
        response = authenticated_client.get('/v2/api/webhooks/')
        assert response.status_code == 200
    
    # Create endpoint tests
    def test_create_webhook_as_admin(self, authenticated_client, store_owner):
        """Test creating webhook as admin"""
        response = authenticated_client.post('/v2/api/webhooks/', {
            'name': 'Test Webhook',
            'url': 'https://example.com/webhook'
        })
        assert response.status_code == 201
    
    def test_create_webhook_as_anonymous(self, anonymous_client):
        """Test creating webhook as anonymous (should fail)"""
        response = anonymous_client.post('/v2/api/webhooks/', {
            'name': 'Test Webhook',
            'url': 'https://example.com/webhook'
        })
        assert response.status_code == 401
    
    # Custom action tests
    def test_test_webhook_as_admin(self, authenticated_client, webhook):
        """Test triggering webhook test"""
        response = authenticated_client.post(f'/v2/api/webhooks/{webhook.id}/test/')
        assert response.status_code == 200
    
    def test_test_webhook_as_anonymous(self, anonymous_client, webhook):
        """Test triggering webhook test as anonymous (should fail)"""
        response = anonymous_client.post(f'/v2/api/webhooks/{webhook.id}/test/')
        assert response.status_code == 401
    
    # Permission tests
    def test_unauthorized_access(self, anonymous_client, webhook):
        """Test unauthorized access"""
        response = anonymous_client.patch(f'/v2/api/webhooks/{webhook.id}/', {
            'name': 'Hacked Webhook'
        })
        assert response.status_code == 401
        assert 'authentication' in response.data.get('detail', '').lower()
