"""
Dashboard account services for Digital Farmers CMS.

Business logic for dashboard user management.
"""
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class DashboardAccountService:
    """Service for dashboard account operations"""
    
    @staticmethod
    def get_store_users(store):
        """
        Get all users for a store
        
        Args:
            store: Store instance
            
        Returns:
            QuerySet: Store users
        """
        from apps.accounts.models import StoreUser
        
        return StoreUser.objects.filter(
            store=store,
            is_active=True
        ).select_related('user').order_by('-created_at')
    
    @staticmethod
    def create_store_user(store, user_data, role='customer'):
        """
        Create a new user in store
        
        Args:
            store: Store instance
            user_data: User creation data
            role: Role to assign (default: customer)
            
        Returns:
            StoreUser: Created store user instance
        """
        from core.services.user import UserService
        
        # Create user using centralized service
        user = UserService.create_user(**user_data)
        
        # Add user to store
        store_user = UserService.add_user_to_store(user, store, role)
        
        logger.info(f"Created user {user.email} in store {store.name} as {role}")
        
        return store_user
    
    @staticmethod
    def update_store_user_role(store_user, new_role):
        """
        Update user role in store
        
        Args:
            store_user: StoreUser instance
            new_role: New role to assign
            
        Returns:
            StoreUser: Updated store user instance
        """
        if store_user.role == 'owner':
            raise ValidationError("Cannot change store owner role")
        
        store_user.role = new_role
        store_user.save(update_fields=['role'])
        
        logger.info(f"Updated role for user {store_user.user.email} to {new_role}")
        
        return store_user
    
    @staticmethod
    def deactivate_store_user(store_user):
        """
        Deactivate user in store
        
        Args:
            store_user: StoreUser instance
            
        Returns:
            StoreUser: Updated store user instance
        """
        if store_user.role == 'owner':
            raise ValidationError("Cannot deactivate store owner")
        
        store_user.is_active = False
        store_user.save(update_fields=['is_active'])
        
        logger.info(f"Deactivated user {store_user.user.email} in store")
        
        return store_user
    
    @staticmethod
    def get_store_roles():
        """
        Get all available roles
        
        Returns:
            list: Available roles
        """
        from apps.accounts.models import StoreUser
        
        return StoreUser.ROLE_CHOICES
    
    @staticmethod
    def get_role_permissions(role):
        """
        Get permissions for a specific role
        
        Args:
            role: Role name
            
        Returns:
            list: Role permissions
        """
        role_permissions = {
            'owner': ['all'],
            'admin': ['manage_users', 'manage_products', 'manage_orders', 'manage_settings'],
            'manager': ['manage_products', 'manage_orders', 'manage_customers'],
            'staff': ['manage_products'],
            'customer': ['view_products', 'place_orders'],
        }
        
        return role_permissions.get(role, [])
    
    @staticmethod
    def check_user_permission(user, store, permission):
        """
        Check if user has specific permission in store
        
        Args:
            user: User instance
            store: Store instance
            permission: Permission to check
            
        Returns:
            bool: True if user has permission
        """
        from apps.accounts.models import StoreUser
        
        try:
            store_user = StoreUser.objects.get(
                user=user,
                store=store,
                is_active=True
            )
            
            permissions = DashboardAccountService.get_role_permissions(
                store_user.role
            )
            
            return 'all' in permissions or permission in permissions
            
        except StoreUser.DoesNotExist:
            return False
