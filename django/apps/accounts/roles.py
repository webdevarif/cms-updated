"""
Role-based access control using rest-framework-roles
"""

from apps.stores.models import Store, StoreAPIKey, StoreUserRole
from rest_framework_roles.roles import is_admin, is_anon, is_user

from django.shortcuts import get_object_or_404


def is_store_owner(request, view):
    """Check if user is the owner of the current store"""
    if not request.user.is_authenticated:
        return False

    # Try to get store from different sources
    store = None

    # From view kwargs
    if hasattr(view, "kwargs") and "store_pk" in view.kwargs:
        store = get_object_or_404(Store, pk=view.kwargs["store_pk"])
    # From URL parameters
    elif "store_id" in view.kwargs:
        store = get_object_or_404(Store, pk=view.kwargs["store_id"])
    # From object
    elif hasattr(view, "get_object"):
        try:
            obj = view.get_object()
            if hasattr(obj, "store"):
                store = obj.store
            elif hasattr(obj, "owner"):
                store = obj
        except:
            pass

    if not store:
        return False

    return store.owner == request.user


def is_store_staff_with_action(action):
    """Factory function to create role checkers for specific actions"""

    def checker(request, view):
        if not request.user.is_authenticated:
            return False

        # Get store from various sources
        store = None
        if hasattr(view, "kwargs") and "store_pk" in view.kwargs:
            store = get_object_or_404(Store, pk=view.kwargs["store_pk"])
        elif "store_id" in view.kwargs:
            store = get_object_or_404(Store, pk=view.kwargs["store_id"])
        elif hasattr(view, "get_object"):
            try:
                obj = view.get_object()
                if hasattr(obj, "store"):
                    store = obj.store
                elif hasattr(obj, "owner"):
                    store = obj
            except:
                pass

        if not store:
            return False

        # Check if user has a role with the required action
        user_roles = StoreUserRole.objects.filter(user=request.user, store=store).select_related(
            "role"
        )

        for user_role in user_roles:
            if action in user_role.role.actions:
                return True

        return False

    return checker


def is_store_admin(request, view):
    """Check if user has admin role for the store"""
    return is_store_staff_with_action("manage_settings")(request, view)


def is_store_manager(request, view):
    """Check if user can manage products"""
    return is_store_staff_with_action("manage_products")(request, view)


def can_view_orders(request, view):
    """Check if user can view orders"""
    return is_store_staff_with_action("view_orders")(request, view)


def can_manage_staff(request, view):
    """Check if user can manage staff"""
    return is_store_staff_with_action("manage_staff")(request, view)


def can_view_analytics(request, view):
    """Check if user can view analytics"""
    return is_store_staff_with_action("view_analytics")(request, view)


def has_api_key_with_action(action):
    """Factory function to check API key permissions"""

    def checker(request, view):
        if not hasattr(request, "auth") or not hasattr(request.auth, "store"):
            return False

        api_key = request.auth
        return api_key.has_permission(action)

    return checker


# Role mapping for rest-framework-roles
ROLES = {
    "admin": is_admin,
    "user": is_user,
    "anon": is_anon,
    "store_owner": is_store_owner,
    "store_admin": is_store_admin,
    "store_manager": is_store_manager,
    "can_view_orders": can_view_orders,
    "can_manage_staff": can_manage_staff,
    "can_view_analytics": can_view_analytics,
    # API key roles
    "api_key_manage_products": has_api_key_with_action("manage_products"),
    "api_key_view_orders": has_api_key_with_action("view_orders"),
    "api_key_manage_settings": has_api_key_with_action("manage_settings"),
    "api_key_manage_staff": has_api_key_with_action("manage_staff"),
    "api_key_view_analytics": has_api_key_with_action("view_analytics"),
}


# Define role hierarchies (higher roles inherit lower roles)
ROLE_HIERARCHY = {
    "store_owner": ["store_admin", "store_manager", "can_view_orders", "can_view_analytics"],
    "store_admin": ["store_manager", "can_view_orders", "can_view_analytics"],
    "store_manager": ["can_view_orders"],
}
