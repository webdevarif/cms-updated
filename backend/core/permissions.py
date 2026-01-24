"""
Permission classes for Digital Farmers CMS.

Store-scoped permissions for role-based access control.
"""
from rest_framework.permissions import BasePermission


class IsStoreOwner(BasePermission):
    """Allow access only to store owners"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and
            hasattr(request, 'store') and
            request.store
        )
    
    def has_object_permission(self, request, view, obj):
        # For user objects, check if they're the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # For other objects, check store ownership
        return hasattr(obj, 'store') and obj.store == request.store


class IsStoreAdmin(BasePermission):
    """Allow access only to store admins (owners + admin users)"""
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        if not hasattr(request, 'store') or not request.store:
            return False
        
        # Check if user has admin role in this store
        try:
            from apps.stores.models import StoreMember
            membership = StoreMember.objects.get(
                user=request.user,
                store=request.store,
                role__in=['admin', 'owner']
            )
            return True
        except StoreMember.DoesNotExist:
            return False
    
    def has_object_permission(self, request, view, obj):
        # For forms, check if user created the form or is admin
        if hasattr(obj, 'created_by') and obj.created_by == request.user:
            return True
        
        # Check store admin permission
        return hasattr(obj, 'store') and obj.store == request.store


class IsStoreUser(BasePermission):
    """Allow access only to authenticated store users"""
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        if not hasattr(request, 'store') or not request.store:
            return False
        
        # Check if user has any role in this store
        try:
            from apps.stores.models import StoreMember
            StoreMember.objects.get(
                user=request.user,
                store=request.store
            )
            return True
        except StoreMember.DoesNotExist:
            return False


class IsFormOwner(BasePermission):
    """Allow access only to form creators or store admins"""
    
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Check if user created the form
        if hasattr(obj, 'created_by') and obj.created_by == request.user:
            return True
        
        # Check if user is store admin
        if hasattr(obj, 'store'):
            try:
                from apps.stores.models import StoreMember
                membership = StoreMember.objects.get(
                    user=request.user,
                    store=obj.store,
                    role__in=['admin', 'owner']
                )
                return True
            except StoreMember.DoesNotExist:
                pass
        
        return False


class CanViewFormSubmissions(BasePermission):
    """Allow access to view form submissions"""
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        if not hasattr(request, 'store') or not request.store:
            return False
        
        # Check if user has admin role in this store
        try:
            from apps.stores.models import StoreMember
            membership = StoreMember.objects.get(
                user=request.user,
                store=request.store,
                role__in=['admin', 'owner']
            )
            return True
        except StoreMember.DoesNotExist:
            return False
    
    def has_object_permission(self, request, view, obj):
        # For form objects, check store admin permission
        return hasattr(obj, 'store') and obj.store == request.store
