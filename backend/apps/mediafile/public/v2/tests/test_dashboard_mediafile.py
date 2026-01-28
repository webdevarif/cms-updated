"""
Dashboard mediafile API tests - endpoint-focused only.
"""
import factory
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


class DashboardMediafileAPITests(APIClient):
    """Dashboard mediafile API tests"""

    def setUp(self):
        """Set up test client and user"""
        super().setUp()
        self.user = UserFactory.create()


# FactoryBoy fixtures
class UserFactory(factory.django.DjangoModelFactory):
    """User factory for test data"""

    class Meta:
        model = User
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = "testpass123"


@pytest.mark.django_db
class MediaFileViewSetTests:
    """Media file viewset tests for all roles"""

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
    def test_list_media_as_admin(self, authenticated_client):
        """Test listing media files as admin"""
        response = authenticated_client.get("/v2/api/media/")
        assert response.status_code == 200

    def test_list_media_as_anonymous(self, anonymous_client):
        """Test listing media files as anonymous"""
        response = anonymous_client.get("/v2/api/media/")
        assert response.status_code == 200

    # Upload endpoint tests
    def test_upload_media_as_admin(self, authenticated_client):
        """Test uploading media as admin"""
        from io import BytesIO

        from PIL import Image

        # Create test image
        image = Image.new("RGB", (100, 100), color="red")
        image_file = BytesIO()
        image.save(image_file, "JPEG")
        image_file.seek(0)

        response = authenticated_client.post(
            "/v2/api/media/", {"file": image_file, "name": "test.jpg"}, format="multipart"
        )

        assert response.status_code in [201, 200]

    def test_upload_media_as_anonymous(self, anonymous_client):
        """Test uploading media as anonymous (should fail)"""
        response = anonymous_client.post("/v2/api/media/", {"file": "test.txt"})
        assert response.status_code == 401

    # Permission tests
    def test_unauthorized_access(self, anonymous_client):
        """Test unauthorized access"""
        response = anonymous_client.post("/v2/api/media/", {"file": "test.txt"})
        assert response.status_code == 401
        assert "authentication" in response.data.get("detail", "").lower()
