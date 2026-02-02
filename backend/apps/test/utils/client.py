"""
DRF APIClient wrappers for testing.
"""

from rest_framework.test import APIClient


class TestClient:
    """Enhanced APIClient for testing"""

    def __init__(self):
        self.client = APIClient()

    def authenticate_as(self, user):
        """Authenticate as a specific user"""
        self.client.force_authenticate(user=user)
        return self

    def authenticate_as_admin(self):
        """Authenticate as admin"""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        admin, _ = User.objects.get_or_create(
            email="admin@example.com", defaults={"is_staff": True, "is_superuser": True}
        )
        return self.authenticate_as(admin)

    def authenticate_as_anonymous(self):
        """Remove authentication"""
        self.client.force_authenticate(user=None)
        return self
