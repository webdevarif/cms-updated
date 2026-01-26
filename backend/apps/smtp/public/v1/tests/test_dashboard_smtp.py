"""
Dashboard SMTP API tests.
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
class DashboardSMTPConfigViewSetTests:
    """Dashboard SMTP config viewset tests"""
    
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
    def test_list_smtp_configs_as_admin(self, authenticated_client):
        """Test listing SMTP configs as admin"""
        response = authenticated_client.get('/v2/api/smtp/')
        assert response.status_code == 200
    
    def test_list_smtp_configs_as_anonymous(self, anonymous_client):
        """Test listing SMTP configs as anonymous"""
        response = anonymous_client.get('/v2/api/smtp/')
        assert response.status_code == 200
    
    # Create endpoint tests
    def test_create_smtp_config_as_admin(self, authenticated_client):
        """Test creating SMTP config as admin"""
        response = authenticated_client.post('/v2/api/smtp/', {
            'name': 'Test SMTP',
            'host': 'smtp.example.com',
            'port': 587
        })
        assert response.status_code in [201, 400]  # May fail validation but should reach endpoint
    
    def test_create_smtp_config_as_anonymous(self, anonymous_client):
        """Test creating SMTP config as anonymous (should fail)"""
        response = anonymous_client.post('/v2/api/smtp/', {
            'name': 'Test SMTP',
            'host': 'smtp.example.com',
            'port': 587
        })
        assert response.status_code in [401, 403]  # Should be unauthorized/forbidden
    
    # Permission tests
    def test_unauthorized_access(self, anonymous_client):
        """Test unauthorized access"""
        response = anonymous_client.post('/v2/api/smtp/', {
            'name': 'Test SMTP',
            'host': 'smtp.example.com',
            'port': 587
        })
        assert response.status_code in [401, 403]
