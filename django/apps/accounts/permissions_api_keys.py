"""
Custom permission classes for API key access control
"""

from apps.stores.models import Store, StoreAPIKey
from rest_framework.permissions import BasePermission
from rest_framework_api_key.permissions import HasAPIKey

from django.shortcuts import get_object_or_404


class HasStoreAPIKey(BasePermission):
    """
    Custom permission class that checks for valid store API key
    """

    def has_permission(self, request, view):
        """Check if request has valid API key"""
        if not hasattr(request, "auth") or not isinstance(request.auth, StoreAPIKey):
            return False

        # API key must not be revoked
        if request.auth.revoked:
            return False

        # Update last used timestamp
        from .services.roles import APIKeyService

        APIKeyService.update_last_used(request.auth)

        return True

    def has_object_permission(self, request, view, obj):
        """Check if API key has access to the specific object"""
        if not self.has_permission(request, view):
            return False

        api_key = request.auth

        # Check if object belongs to the same store as the API key
        if hasattr(obj, "store"):
            return obj.store == api_key.store
        elif hasattr(obj, "owner"):
            return obj == api_key.store
        elif hasattr(obj, "pk"):
            # Try to determine store from view context
            if hasattr(view, "kwargs") and "store_pk" in view.kwargs:
                store = get_object_or_404(Store, pk=view.kwargs["store_pk"])
                return store == api_key.store

        return False


class HasStoreAPIKeyOrIsAuthenticated(BasePermission):
    """
    Allow access if user is authenticated OR has valid store API key
    """

    def has_permission(self, request, view):
        """Check if request has valid authentication"""
        # Check for regular authentication first
        if request.user and request.user.is_authenticated:
            return True

        # Check for API key authentication
        if hasattr(request, "auth") and isinstance(request.auth, StoreAPIKey):
            if not request.auth.revoked:
                # Update last used timestamp
                from .services.roles import APIKeyService

                APIKeyService.update_last_used(request.auth)
                return True

        return False

    def has_object_permission(self, request, view, obj):
        """Check if authentication has access to the specific object"""
        if not self.has_permission(request, view):
            return False

        # If user is authenticated, use existing permission logic
        if request.user and request.user.is_authenticated:
            return True

        # If API key, check store access
        if hasattr(request, "auth") and isinstance(request.auth, StoreAPIKey):
            api_key = request.auth

            # Check if object belongs to the same store as the API key
            if hasattr(obj, "store"):
                return obj.store == api_key.store
            elif hasattr(obj, "owner"):
                return obj == api_key.store
            elif hasattr(obj, "pk"):
                # Try to determine store from view context
                if hasattr(view, "kwargs") and "store_pk" in view.kwargs:
                    store = get_object_or_404(Store, pk=view.kwargs["store_pk"])
                    return store == api_key.store

        return False


class HasStoreAPIKeyWithAction(BasePermission):
    """
    Custom permission class that checks for valid API key with specific action
    """

    def __init__(self, action):
        self.action = action

    def has_permission(self, request, view):
        """Check if request has valid API key with required action"""
        if not hasattr(request, "auth") or not isinstance(request.auth, StoreAPIKey):
            return False

        api_key = request.auth

        # API key must not be revoked
        if api_key.revoked:
            return False

        # Check if API key has the required action
        if not api_key.has_permission(self.action):
            return False

        # Update last used timestamp
        from .services.roles import APIKeyService

        APIKeyService.update_last_used(api_key)

        return True

    def has_object_permission(self, request, view, obj):
        """Check if API key has access to the specific object"""
        if not self.has_permission(request, view):
            return False

        api_key = request.auth

        # Check if object belongs to the same store as the API key
        if hasattr(obj, "store"):
            return obj.store == api_key.store
        elif hasattr(obj, "owner"):
            return obj == api_key.store
        elif hasattr(obj, "pk"):
            # Try to determine store from view context
            if hasattr(view, "kwargs") and "store_pk" in view.kwargs:
                store = get_object_or_404(Store, pk=view.kwargs["store_pk"])
                return store == api_key.store

        return False


# Factory functions for common action-based permissions
def can_manage_products_via_api():
    """Permission class for managing products via API key"""
    return HasStoreAPIKeyWithAction("manage_products")


def can_view_orders_via_api():
    """Permission class for viewing orders via API key"""
    return HasStoreAPIKeyWithAction("view_orders")


def can_manage_settings_via_api():
    """Permission class for managing settings via API key"""
    return HasStoreAPIKeyWithAction("manage_settings")


def can_manage_staff_via_api():
    """Permission class for managing staff via API key"""
    return HasStoreAPIKeyWithAction("manage_staff")


def can_view_analytics_via_api():
    """Permission class for viewing analytics via API key"""
    return HasStoreAPIKeyWithAction("view_analytics")
