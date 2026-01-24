"""
API tests for translations module.
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
class TranslationViewSetTests:
    """Translation viewset tests for all roles"""
    
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
    
    # List endpoint tests
    def test_list_translations_as_anonymous(self, anonymous_client):
        """Test listing translations as anonymous"""
        response = anonymous_client.get('/v2/api/translations/')
        assert response.status_code == 200
    
    def test_list_translations_as_admin(self, authenticated_client):
        """Test listing translations as admin"""
        response = authenticated_client.get('/v2/api/translations/')
        assert response.status_code == 200
    
    # Create endpoint tests
    def test_create_translation_as_admin(self, authenticated_client):
        """Test creating translation as admin"""
        response = authenticated_client.post('/v2/api/translations/', {
            'key': 'test',
            'text': 'Test'
        })
        assert response.status_code == 201
    
    def test_create_translation_as_anonymous(self, anonymous_client):
        """Test creating translation as anonymous (should fail)"""
        response = anonymous_client.post('/v2/api/translations/', {
            'key': 'test',
            'text': 'Test'
        })
        assert response.status_code == 401
    
    # Permission tests
    def test_unauthorized_access(self, anonymous_client):
        """Test unauthorized access"""
        response = anonymous_client.post('/v2/api/translations/', {
            'key': 'test',
            'text': 'Test'
        })
        assert response.status_code == 401
        assert 'authentication' in response.data.get('detail', '').lower()
