"""
Custom assertions for testing.
"""
from rest_framework.test import APIClient


def assert_permission_denied(response, expected_permission):
    """Assert that permission was denied"""
    assert response.status_code in [403, 401]
    assert "permission" in response.data.get("detail", "").lower()


def assert_authentication_required(response):
    """Assert that authentication is required"""
    assert response.status_code == 401
    assert "authentication" in response.data.get("detail", "").lower()


def assert_role_required(response, role):
    """Assert that specific role is required"""
    assert response.status_code == 403
    assert f"{role} role required" in response.data.get("detail", "").lower()
