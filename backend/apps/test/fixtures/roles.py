"""
Role fixtures for testing.
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def staff_user(store):
    """Create staff user fixture"""
    from apps.accounts.models import Role, StoreMember

    user = User.objects.create_user(email="staff@example.com", password="testpass123")

    # Create staff role
    role = Role.objects.create(
        store=store,
        slug="staff",
        name="Staff",
        permissions=["content.read", "ecommerce.read"],
    )

    # Assign role to user
    StoreMember.objects.create(store=store, user=user, role=role)

    return user


@pytest.fixture
def anonymous_client():
    """Create anonymous APIClient fixture"""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def authenticated_client(admin_user):
    """Create authenticated APIClient fixture"""
    from rest_framework.test import APIClient

    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client
