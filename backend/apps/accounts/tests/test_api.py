"""
API tests for accounts module.
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
class UserViewSetTests:
    """User viewset tests for all roles"""
    
    @pytest.fixture
    def admin_user(self):
        """Create admin user fixture"""
        from core.services.user import UserService
        return UserService.create_user(
            email='admin@example.com',
            is_staff=True,
            is_superuser=True
        )
    
    @pytest.fixture
    def regular_user(self):
        """Create regular user fixture"""
        from core.services.user import UserService
        return UserService.create_user(email='user@example.com')
    
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
    
    # List endpoint tests
    def test_list_users_as_admin(self, authenticated_client):
        """Test listing users as admin"""
        response = authenticated_client.get('/v2/api/accounts/users/')
        assert response.status_code == 200
    
    def test_list_users_as_anonymous(self, anonymous_client):
        """Test listing users as anonymous"""
        response = anonymous_client.get('/v2/api/accounts/users/')
        assert response.status_code == 200
    
    # Create endpoint tests
    def test_create_user_as_admin(self, authenticated_client):
        """Test creating user as admin"""
        response = authenticated_client.post('/v2/api/accounts/users/', {
            'email': 'newuser@example.com',
            'password': 'testpass123'
        })
        assert response.status_code == 201
    
    def test_create_user_as_anonymous(self, anonymous_client):
        """Test creating user as anonymous (should fail)"""
        response = anonymous_client.post('/v2/api/accounts/users/', {
            'email': 'newuser@example.com',
            'password': 'testpass123'
        })
        assert response.status_code == 401
    
    # Update endpoint tests
    def test_update_user_as_admin(self, authenticated_client, regular_user):
        """Test updating user as admin"""
        response = authenticated_client.put(f'/v2/api/accounts/users/{regular_user.id}/', {
            'email': regular_user.email,
            'password': 'newpass123'
        })
        assert response.status_code == 200
    
    def test_update_user_as_anonymous(self, anonymous_client, regular_user):
        """Test updating user as anonymous (should fail)"""
        response = anonymous_client.patch(f'/v2/api/accounts/users/{regular_user.id}/', {
            'email': 'hacked@example.com'
        })
        assert response.status_code == 401
    
    # Delete endpoint tests
    def test_delete_user_as_admin(self, authenticated_client, regular_user):
        """Test deleting user as admin"""
        response = authenticated_client.delete(f'/v2/api/accounts/users/{regular_user.id}/')
        assert response.status_code == 204
    
    def test_delete_user_as_regular(self, regular_user):
        """Test deleting user as regular user (should fail)"""
        client = APIClient()
        client.force_authenticate(user=regular_user)
        
        response = client.delete(f'/v2/api/accounts/users/{regular_user.id}/')
        assert response.status_code == 403
    
    # Permission tests
    def test_unauthorized_access(self, anonymous_client, regular_user):
        """Test unauthorized access"""
        response = anonymous_client.patch(f'/v2/api/accounts/users/{regular_user.id}/', {
            'email': 'hacked@example.com'
        })
        assert response.status_code == 401
        assert 'authentication' in response.data.get('detail', '').lower()
