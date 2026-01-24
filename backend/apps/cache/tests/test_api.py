"""
API tests for cache module.
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


@pytest.mark.django_db
class CacheViewSetTests:
    """Cache viewset tests for all roles"""
    
    @pytest.fixture
    def admin_user(self):
        """Create admin user fixture"""
        return UserFactory(
            email='admin@example.com',
            is_staff=True,
            is_superuser=True
        )
    
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
    
    # Get endpoint tests
    def test_get_cache_as_anonymous(self, anonymous_client):
        """Test getting cache as anonymous"""
        response = anonymous_client.get('/v2/api/cache/get/?key=test')
        assert response.status_code in [200, 404]
    
    # Set endpoint tests
    def test_set_cache_as_anonymous(self, anonymous_client):
        """Test setting cache as anonymous (should fail)"""
        response = anonymous_client.post('/v2/api/cache/set/', {
            'key': 'test',
            'value': 'test'
        })
        assert response.status_code == 401
    
    def test_set_cache_as_admin(self, authenticated_client):
        """Test setting cache as admin"""
        response = authenticated_client.post('/v2/api/cache/set/', {
            'key': 'test',
            'value': 'test'
        })
        assert response.status_code in [200, 201]
    
    # Delete endpoint tests
    def test_delete_cache_as_anonymous(self, anonymous_client):
        """Test deleting cache as anonymous (should fail)"""
        response = anonymous_client.delete('/v2/api/cache/delete/?key=test')
        assert response.status_code == 401
    
    def test_delete_cache_as_admin(self, authenticated_client):
        """Test deleting cache as admin"""
        response = authenticated_client.delete('/v2/api/cache/delete/?key=test')
        assert response.status_code in [200, 204]
    
    # Permission tests
    def test_unauthorized_access(self, anonymous_client):
        """Test unauthorized access"""
        response = anonymous_client.post('/v2/api/cache/set/', {
            'key': 'test',
            'value': 'test'
        })
        assert response.status_code == 401
        assert 'authentication' in response.data.get('detail', '').lower()
