"""
Public account services for Digital Farmers CMS.

Business logic for public authentication endpoints.
"""
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)


class PublicAuthService:
    """Service for public authentication operations"""
    
    @staticmethod
    def register_user(validated_data):
        """
        Register a new user and add to store if context exists
        
        Args:
            validated_data: Validated registration data
            
        Returns:
            tuple: (user, tokens)
        """
        from core.services.user import UserService
        
        # Create user using centralized service
        user = UserService.create_user(**validated_data)
        
        # Generate JWT tokens
        tokens = PublicAuthService.generate_tokens(user)
        
        logger.info(f"User registered: {user.email}")
        
        return user, tokens
    
    @staticmethod
    def login_user(email, password):
        """
        Authenticate user and return tokens
        
        Args:
            email: User email
            password: User password
            
        Returns:
            tuple: (user, tokens) or (None, None) if failed
        """
        user = authenticate(username=email, password=password)
        
        if not user:
            return None, None
        
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {email}")
            return None, None
        
        # Generate JWT tokens
        tokens = PublicAuthService.generate_tokens(user)
        
        logger.info(f"User logged in: {user.email}")
        
        return user, tokens
    
    @staticmethod
    def generate_tokens(user):
        """
        Generate JWT tokens for user
        
        Args:
            user: User instance
            
        Returns:
            dict: Access and refresh tokens
        """
        refresh = RefreshToken.for_user(user)
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    @staticmethod
    def add_user_to_store(user, store, role='customer'):
        """
        Add user to store with specified role
        
        Args:
            user: User instance
            store: Store instance
            role: Role to assign (default: customer)
        """
        from apps.accounts.models import StoreUser
        
        store_user, created = StoreUser.objects.get_or_create(
            user=user,
            store=store,
            defaults={'role': role, 'is_active': True}
        )
        
        if created:
            logger.info(f"Added user {user.email} to store {store.name} as {role}")
        else:
            logger.info(f"User {user.email} already exists in store {store.name}")
        
        return store_user
    
    @staticmethod
    def logout_user(refresh_token):
        """
        Blacklist refresh token
        
        Args:
            refresh_token: Refresh token to blacklist
        """
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info("User logged out successfully")
        except Exception as e:
            logger.error(f"Logout error: {e}")
    
    @staticmethod
    def change_password(user, current_password, new_password):
        """
        Change user password
        
        Args:
            user: User instance
            current_password: Current password for verification
            new_password: New password to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not user.check_password(current_password):
            logger.warning(f"Failed password change attempt for user: {user.email}")
            return False
        
        user.set_password(new_password)
        user.save(update_fields=['password'])
        
        logger.info(f"Password changed for user: {user.email}")
        
        return True
