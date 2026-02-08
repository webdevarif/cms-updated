"""
Store fixtures for testing.
"""

import pytest

from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def store_owner():
    """Create store owner user fixture"""
    from apps.stores.models import Store

    user = User.objects.create_user(email="owner@example.com", password="testpass123")
    store = Store.objects.create(name="Test Store", slug="test-store", owner=user)
    return store


@pytest.fixture
def store(store_owner):
    """Store fixture"""
    return store_owner
