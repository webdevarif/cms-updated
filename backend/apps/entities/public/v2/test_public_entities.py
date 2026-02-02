"""
Public Entities API tests.
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
class PublicEntityViewSetTests:
    """Public entity viewset tests"""

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
    def test_list_entities_as_admin(self, authenticated_client):
        """Test listing entities as admin"""
        response = authenticated_client.get("/v2/api/entities/")
        assert response.status_code == 200

    def test_list_entities_as_anonymous(self, anonymous_client):
        """Test listing entities as anonymous"""
        response = anonymous_client.get("/v2/api/entities/")
        assert response.status_code == 200

    # Retrieve endpoint tests
    def test_retrieve_entity_as_admin(self, authenticated_client):
        """Test retrieving entity as admin"""
        response = authenticated_client.get("/v2/api/entities/1/")
        assert response.status_code in [
            200,
            404,
        ]  # May not exist but should reach endpoint

    def test_retrieve_entity_as_anonymous(self, anonymous_client):
        """Test retrieving entity as anonymous"""
        response = anonymous_client.get("/v2/api/entities/1/")
        assert response.status_code in [
            200,
            404,
        ]  # May not exist but should reach endpoint

    # Permission tests
    def test_unauthorized_create(self, anonymous_client):
        """Test unauthorized create (should fail)"""
        response = anonymous_client.post(
            "/v2/api/entities/", {"name": "Test Entity", "type": "test"}
        )
        assert response.status_code in [
            401,
            403,
            405,
        ]  # Should be unauthorized/forbidden/method not allowed
