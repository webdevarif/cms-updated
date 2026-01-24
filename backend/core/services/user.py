"""
User management services for Digital Farmers CMS.

Shared user management service.
"""
from django.core.exceptions import ValidationError
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Shared user management service"""
    
    @staticmethod
    def create_user(email, username=None, password=None, **extra_fields):
        """
        Centralized user creation method
        Replaces all direct User.objects.create_user() calls
        """
        from apps.accounts.models import User
        
        # Generate username if not provided
        if not username:
            username = email.split('@')[0]
        
        return User.objects.create_user(
            email=email,
            username=username,
            password=password,
            **extra_fields
        )
    
    @staticmethod
    def get_user(email=None, user_id=None, **filters):
        """
        Centralized user retrieval method
        Replaces all direct User.objects.get() calls
        """
        from apps.accounts.models import User
        
        if email:
            return User.objects.get(email=email, **filters)
        elif user_id:
            return User.objects.get(id=user_id, **filters)
        else:
            return User.objects.get(**filters)
    
    @staticmethod
    def get_user_or_none(email=None, user_id=None, **filters):
        """
        Centralized user retrieval method (safe)
        """
        from apps.accounts.models import User
        
        if email:
            return User.objects.filter(email=email, **filters).first()
        elif user_id:
            return User.objects.filter(id=user_id, **filters).first()
        else:
            return User.objects.filter(**filters).first()
    
    @staticmethod
    def update_user(user, **fields):
        """
        Centralized user update method
        Replaces all direct user.save() calls
        """
        for field, value in fields.items():
            setattr(user, field, value)
        user.save()
        return user
    
    @staticmethod
    def delete_user(user):
        """
        Centralized user deletion method
        Replaces all direct user.delete() calls
        """
        user.delete()
    
    @staticmethod
    def filter_users(**filters):
        """
        Centralized user filtering method
        Replaces all direct User.objects.filter() calls
        """
        from apps.accounts.models import User
        return User.objects.filter(**filters)
    
    @staticmethod
    def create_user_store_owner(store, email, username, password):
        """Create store owner user"""
        with transaction.atomic():
            from apps.accounts.models import User, StoreUser
            
            # Create user using centralized method
            user = UserService.create_user(
                email=email,
                username=username,
                password=password,
                is_verified=True,  # Auto-verify store owners
            )
            
            # Create store user with owner role
            StoreUser.objects.create(
                user=user,
                store=store,
                role='owner',
                is_active=True
            )
            
            logger.info(f"Created store owner user {email} for store {store.name}")
            
            return user
    
    @staticmethod
    def update_user_role(user, store, new_role):
        """Update user role with permission validation"""
        from apps.accounts.models import StoreUser
        
        try:
            store_user = StoreUser.objects.get(user=user, store=store)
            
            if store_user.role == 'owner':
                raise ValidationError("Cannot change store owner role")
            
            store_user.role = new_role
            store_user.save(update_fields=['role'])
            
            logger.info(f"Updated user {user.email} role to {new_role} in store {store.name}")
            
        except StoreUser.DoesNotExist:
            raise ValidationError("User not found in this store")
    
    @staticmethod
    def deactivate_user(user, store):
        """Safely deactivate user"""
        from apps.accounts.models import StoreUser
        
        try:
            store_user = StoreUser.objects.get(user=user, store=store)
            
            if store_user.role == 'owner':
                raise ValidationError("Cannot deactivate store owner")
            
            store_user.is_active = False
            store_user.save(update_fields=['is_active'])
            
            logger.info(f"Deactivated user {user.email} in store {store.name}")
            
        except StoreUser.DoesNotExist:
            raise ValidationError("User not found in this store")
    
    @staticmethod
    def add_user_to_store(user, store, role='customer'):
        """Add user to store with specified role"""
        from apps.accounts.models import StoreUser
        
        store_user, created = StoreUser.objects.get_or_create(
            user=user,
            store=store,
            defaults={'role': role, 'is_active': True}
        )
        
        if created:
            logger.info(f"Added user {user.email} to store {store.name} with role {role}")
        else:
            logger.info(f"User {user.email} already exists in store {store.name}")
        
        return store_user
    
    @staticmethod
    def get_store_user(user, store):
        """Get store user relationship"""
        from apps.accounts.models import StoreUser
        
        try:
            return StoreUser.objects.get(user=user, store=store)
        except StoreUser.DoesNotExist:
            return None
    
    @staticmethod
    def get_store_user_or_none(user, store):
        """Get store user relationship (safe)"""
        from apps.accounts.models import StoreUser
        
        return StoreUser.objects.filter(user=user, store=store).first()
    
    @staticmethod
    def update_store_user_role(user, store, new_role):
        """Update store user role"""
        from apps.accounts.models import StoreUser
        
        try:
            store_user = StoreUser.objects.get(user=user, store=store)
            
            if store_user.role == 'owner':
                raise ValidationError("Cannot change store owner role")
            
            store_user.role = new_role
            store_user.save(update_fields=['role'])
            
            logger.info(f"Updated user {user.email} role to {new_role} in store {store.name}")
            
        except StoreUser.DoesNotExist:
            raise ValidationError("User not found in this store")
    
    @staticmethod
    def deactivate_store_user(user, store):
        """Safely deactivate store user"""
        from apps.accounts.models import StoreUser
        
        try:
            store_user = StoreUser.objects.get(user=user, store=store)
            
            if store_user.role == 'owner':
                raise ValidationError("Cannot deactivate store owner")
            
            store_user.is_active = False
            store_user.save(update_fields=['is_active'])
            
            logger.info(f"Deactivated user {user.email} in store {store.name}")
            
        except StoreUser.DoesNotExist:
            raise ValidationError("User not found in this store")
    
    @staticmethod
    def activate_store_user(user, store):
        """Activate store user"""
        from apps.accounts.models import StoreUser
        
        try:
            store_user = StoreUser.objects.get(user=user, store=store)
            store_user.is_active = True
            store_user.save(update_fields=['is_active'])
            
            logger.info(f"Activated user {user.email} in store {store.name}")
            
        except StoreUser.DoesNotExist:
            raise ValidationError("User not found in this store")
    
    @staticmethod
    def filter_store_users(store, **filters):
        """Filter store users"""
        from apps.accounts.models import StoreUser
        
        return StoreUser.objects.filter(store=store, **filters)
    
    @staticmethod
    def get_store_users_by_role(store, role):
        """Get store users by role"""
        from apps.accounts.models import StoreUser
        
        return StoreUser.objects.filter(store=store, role=role, is_active=True)
    
    @staticmethod
    def get_store_owners(store):
        """Get store owners"""
        return UserService.get_store_users_by_role(store, 'owner')
    
    @staticmethod
    def get_store_staff(store):
        """Get store staff (owners + admin + manager + staff)"""
        from apps.accounts.models import StoreUser
        
        return StoreUser.objects.filter(
            store=store,
            role__in=['owner', 'admin', 'manager', 'staff'],
            is_active=True
        )
    
    @staticmethod
    def get_store_customers(store):
        """Get store customers"""
        return UserService.get_store_users_by_role(store, 'customer')
