# Account services module
# Add account-related business logic here

"""
TODO: TARGET DESIGN - Single AccountService

This file currently contains three separate service classes:
- PublicAuthService: JWT tokens, user creation
- CustomerAccountService: Profile management, password changes
- DashboardAccountService: Store user management, role updates

TARGET: Merge into a single AccountService class that internally handles:
1. Public auth operations (login, register, tokens)
2. Customer profile operations (update profile, password)
3. Dashboard user management (store users, roles, permissions)

This will eliminate duplication and provide a single source of truth for all account operations.
"""

import logging

from django.contrib.auth import login, logout
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)


class PublicAuthService:
    """Service for public authentication operations"""

    @staticmethod
    def generate_token(user):
        """Generate JWT token for user"""
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    @staticmethod
    def verify_token(token):
        """Verify JWT token"""
        try:
            from rest_framework_simplejwt.tokens import AccessToken

            access_token = AccessToken(token)
            return access_token.payload
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None

    @staticmethod
    def create_user(email, password, first_name="", last_name="", **extra_fields):
        """Create new user account"""
        from apps.accounts.models.user import User

        username = (
            email.split("@")[0] if not extra_fields.get("username") else extra_fields["username"]
        )

        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            **extra_fields,
        )

        logger.info(f"Created new user: {email}")
        return user


class CustomerAccountService:
    """Service for customer account operations"""

    @staticmethod
    def update_profile(user, data):
        """Update user profile"""
        allowed_fields = ["first_name", "last_name"]
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])

        user.save(update_fields=allowed_fields)
        logger.info(f"Updated profile for user: {user.email}")
        return user

    @staticmethod
    def change_password(user, current_password, new_password):
        """Change user password"""
        if not user.check_password(current_password):
            raise ValueError("Current password is incorrect")

        user.set_password(new_password)
        user.save(update_fields=["password"])
        logger.info(f"Changed password for user: {user.email}")

    @staticmethod
    def get_user_activity(user, limit=10):
        """Get user activity log"""
        from apps.accounts.models.activity import UserActivity

        return UserActivity.objects.filter(user=user).order_by("-created_at")[:limit]


class DashboardAccountService:
    """Service for dashboard account operations"""

    @staticmethod
    def create_store_user(store, user, role="customer"):
        """Create store user association"""
        from apps.accounts.models.store_user import StoreUser

        store_user, created = StoreUser.objects.get_or_create(
            user=user, store=store, defaults={"role": role}
        )

        if created:
            logger.info(f"Created store user: {user.email} - {store.name} ({role})")

        return store_user

    @staticmethod
    def update_user_role(store_user, new_role):
        """Update user role"""
        if store_user.role == "owner":
            raise ValueError("Cannot change owner role")

        store_user.role = new_role
        store_user.save(update_fields=["role"])
        logger.info(f"Updated role for {store_user.user.email} to {new_role}")

    @staticmethod
    def deactivate_user(store_user):
        """Deactivate user"""
        store_user.is_active = False
        store_user.save(update_fields=["is_active"])
        logger.info(f"Deactivated user: {store_user.user.email}")

    @staticmethod
    def get_store_users(store):
        """Get all users for a store"""
        from apps.accounts.models.store_user import StoreUser

        return StoreUser.objects.filter(store=store).select_related("user")

    @staticmethod
    def get_user_stats(store):
        """Get user statistics for a store"""
        from apps.accounts.models.store_user import StoreUser

        users = StoreUser.objects.filter(store=store)
        return {
            "total_users": users.count(),
            "active_users": users.filter(is_active=True).count(),
            "owners": users.filter(role="owner").count(),
            "admins": users.filter(role="admin").count(),
            "managers": users.filter(role="manager").count(),
            "staff": users.filter(role="staff").count(),
            "customers": users.filter(role="customer").count(),
        }
