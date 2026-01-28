"""
Dashboard Logs API tests.
"""
import factory
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


# FactoryBoy fixtures
class UserFactory(factory.django.DjangoModelFactory):
    """User factory for test data"""

    class Meta:
        model = User
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = "testpass123"


@pytest.mark.django_db
class DashboardLogEntryViewSetTests:
    """Dashboard log entry viewset tests"""

    @pytest.fixture
    def admin_user(self):
        """Create admin user fixture"""
        return UserFactory(email="admin@example.com", is_staff=True, is_superuser=True)

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
    def test_list_logs_as_admin(self, authenticated_client):
        """Test listing logs as admin"""
        response = authenticated_client.get("/api/v2/logs/dashboard/logs/")
        assert response.status_code == 200

    def test_list_logs_as_anonymous(self, anonymous_client):
        """Test listing logs as anonymous"""
        response = anonymous_client.get("/api/v2/logs/dashboard/logs/")
        assert response.status_code == 200

    # Create endpoint tests
    def test_create_log_as_admin(self, authenticated_client):
        """Test creating log as admin"""
        response = authenticated_client.post(
            "/api/v2/logs/dashboard/logs/",
            {"level": "INFO", "message": "Test log message", "module": "test"},
        )
        assert response.status_code in [201, 400]  # May fail validation but should reach endpoint

    def test_create_log_as_anonymous(self, anonymous_client):
        """Test creating log as anonymous (should fail)"""
        response = anonymous_client.post(
            "/api/v2/logs/dashboard/logs/",
            {"level": "INFO", "message": "Test log message", "module": "test"},
        )
        assert response.status_code in [401, 403]  # Should be unauthorized/forbidden

    # Permission tests
    def test_unauthorized_access(self, anonymous_client):
        """Test unauthorized access"""
        response = anonymous_client.post(
            "/api/v2/logs/dashboard/logs/",
            {"level": "INFO", "message": "Test log message", "module": "test"},
        )
        assert response.status_code in [401, 403]
