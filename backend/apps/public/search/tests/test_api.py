"""
API tests for search module.
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
class SearchViewSetTests:
    """Search viewset tests for all roles"""
    
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
    
    # Search endpoint tests
    def test_search_as_anonymous(self, anonymous_client):
        """Test searching as anonymous"""
        response = anonymous_client.get('/v2/api/search/')
        assert response.status_code == 200
    
    def test_search_as_admin(self, authenticated_client):
        """Test searching as admin"""
        response = authenticated_client.get('/v2/api/search/')
        assert response.status_code == 200
    
    # Search documents tests
    def test_search_documents_as_anonymous(self, anonymous_client):
        """Test searching documents as anonymous"""
        response = anonymous_client.get('/v2/api/search/documents/')
        assert response.status_code == 200
    
    # Permission tests
    def test_unauthorized_access(self, anonymous_client):
        """Test unauthorized access to protected endpoints"""
        response = anonymous_client.post('/v2/api/search/', {
            'query': 'test'
        })
        assert response.status_code == 200  # Search is public
