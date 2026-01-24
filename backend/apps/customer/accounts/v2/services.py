"""
Customer account services for Digital Farmers CMS.

Business logic for customer account management.
"""
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class CustomerAccountService:
    """Service for customer account operations"""
    
    @staticmethod
    def get_customer_profile(user):
        """
        Get customer profile
        
        Args:
            user: User instance
            
        Returns:
            dict: Customer profile data
        """
        from apps.accounts.models import UserPreferences
        
        preferences, created = UserPreferences.objects.get_or_create(
            user=user
        )
        
        return {
            'user': user,
            'preferences': preferences
        }
    
    @staticmethod
    def update_customer_profile(user, validated_data):
        """
        Update customer profile
        
        Args:
            user: User instance
            validated_data: Validated profile data
            
        Returns:
            User: Updated user instance
        """
        for field, value in validated_data.items():
            setattr(user, field, value)
        
        user.save()
        
        logger.info(f"Profile updated for user: {user.email}")
        
        return user
    
    @staticmethod
    def update_customer_preferences(user, validated_data):
        """
        Update customer preferences
        
        Args:
            user: User instance
            validated_data: Validated preferences data
            
        Returns:
            UserPreferences: Updated preferences instance
        """
        from apps.accounts.models import UserPreferences
        
        preferences, created = UserPreferences.objects.get_or_create(
            user=user,
            defaults=validated_data
        )
        
        if not created:
            for field, value in validated_data.items():
                setattr(preferences, field, value)
            preferences.save()
        
        logger.info(f"Preferences updated for user: {user.email}")
        
        return preferences
    
    @staticmethod
    def change_customer_password(user, current_password, new_password):
        """
        Change customer password
        
        Args:
            user: User instance
            current_password: Current password
            new_password: New password
            
        Returns:
            tuple: (success, message)
        """
        if not user.check_password(current_password):
            return False, "Current password is incorrect"
        
        user.set_password(new_password)
        user.save(update_fields=['password'])
        
        logger.info(f"Password changed for customer: {user.email}")
        
        return True, "Password changed successfully"
    
    @staticmethod
    def get_customer_orders(user, store):
        """
        Get customer order history
        
        Args:
            user: User instance
            store: Store instance
            
        Returns:
            QuerySet: Customer orders
        """
        from apps.ecommerce.models import Order
        
        return Order.objects.filter(
            user=user,
            store=store
        ).order_by('-created_at')
    
    @staticmethod
    def get_customer_addresses(user, store):
        """
        Get customer addresses
        
        Args:
            user: User instance
            store: Store instance
            
        Returns:
            QuerySet: Customer addresses
        """
        from apps.ecommerce.models import Address
        
        return Address.objects.filter(
            user=user,
            store=store
        ).order_by('-is_default', '-created_at')
