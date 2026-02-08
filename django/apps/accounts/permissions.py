from rest_framework import permissions
from rest_framework.permissions import BasePermission


class HasStoreAccess(BasePermission):
    """
    Custom permission to ensure users have appropriate store access and roles.
    This permission must be used after StoreRequiredPermission in the permission_classes list.
    """

    def has_permission(self, request, view):
        """
        Check permissions for list/create operations.
        StoreScopedMixin should have already resolved the store and set view.store.
        """
        store = getattr(view, "store", None)
        print(
            f"DEBUG HasStoreAccess check - user: {request.user.id if request.user.is_authenticated else 'anonymous'}, store: {store.id if store else 'None'}"
        )

        if not store:
            print("DEBUG HasStoreAccess failed: no store on view")
            return False

        # Check if user has any membership in this store OR is the store owner
        has_membership = request.user.store_memberships.filter(store=store).exists()
        is_owner = store.owner_id == request.user.id

        print(
            f"DEBUG HasStoreAccess - has_membership: {has_membership}, is_owner: {is_owner} (store.owner_id: {store.owner_id}, request.user.id: {request.user.id})"
        )

        result = has_membership or is_owner
        print(f"DEBUG HasStoreAccess result: {result}")

        if not result:
            # Debug: Raise detailed exception to show in response
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                f"Store access denied. Debug info: user_id={request.user.id}, store_id={store.id}, has_membership={has_membership}, is_owner={is_owner}, store_owner_id={store.owner_id}"
            )

        return result

    def has_object_permission(self, request, view, obj):
        """
        Check permissions for retrieve/update/delete operations on specific objects.
        """
        # For posts, check if user has membership in the post's store
        if hasattr(obj, "store"):
            store = obj.store
        else:
            return False

        # Check if user has membership in this store OR is the store owner
        membership = request.user.store_memberships.filter(store=store).first()
        is_owner = store.owner == request.user

        if not membership and not is_owner:
            return False

        # For write operations (update, delete), require owner or admin role (or store ownership)
        if request.method in ["PUT", "PATCH", "DELETE"]:
            if is_owner:
                return True
            return membership and membership.role in ["owner", "admin"]

        # For read operations, any membership or ownership is sufficient
        return True


class IsStoreOwner(permissions.BasePermission):
    """Only allow store owners to edit/delete stores"""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "owner"):
            return obj.owner == request.user
        return False


class IsStoreMember(permissions.BasePermission):
    """Only allow store members to view stores"""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "owner") and obj.owner == request.user:
            return True

        if hasattr(obj, "memberships"):
            return obj.memberships.filter(user=request.user).exists()

        return False


class IsStoreAdminOrOwner(permissions.BasePermission):
    """Only allow store admins or owners to manage memberships"""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "store"):
            store = obj.store
        elif hasattr(obj, "owner"):
            store = obj
        else:
            return False

        if store.owner == request.user:
            return True

        return store.memberships.filter(user=request.user, role__in=["admin", "owner"]).exists()
