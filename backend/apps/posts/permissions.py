"""
Permissions for posts app.
"""
from rest_framework import permissions


class PostPermissions(permissions.BasePermission):
    """
    Permission class for posts with store-level access control.
    """

    def has_permission(self, request, view):
        """Check authentication, permission flags, and store access"""
        user = request.user
        if not user.is_authenticated:
            return False

        # Users must hold at least one posts permission
        perm_required = (
            "posts.view_post" if request.method in permissions.SAFE_METHODS else "posts.change_post"
        )
        if not user.has_perm(perm_required):
            return False

        return self._store_access(user, getattr(request, "store", None))

    def has_object_permission(self, request, view, obj):
        """Check if user has permission for specific post object"""
        # User must have access to the store
        return self._store_access(request.user, getattr(obj, "store", None))

    def _store_access(self, user, store):
        if not store or not user.is_authenticated:
            return False
        return user.stores.filter(id=store.id).exists()
