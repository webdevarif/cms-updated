"""
User fixtures for testing.
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def admin_user():
    """Create admin user fixture"""
    return User.objects.create_user(
        email='admin@example.com',
        password='testpass123',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def regular_user():
    """Create regular user fixture"""
    return User.objects.create_user(
        email='user@example.com',
        password='testpass123'
    )
