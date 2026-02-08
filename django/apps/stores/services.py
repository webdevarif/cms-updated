"""
Services for the stores app.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .models import Store, StoreMembership

User = get_user_model()


class StoreService:
    """Service class for store-related operations."""

    @staticmethod
    def get_user_stores(user):
        """
        Get all stores that a user has access to.

        Args:
            user: User instance

        Returns:
            QuerySet of Store objects
        """
        # Get stores where user is owner
        owned_stores = Store.objects.filter(owner=user).distinct()

        # Get stores where user has membership
        member_stores = Store.objects.filter(memberships__user=user, status="active").distinct()

        # Combine and return unique stores
        return (owned_stores | member_stores).distinct()

    @staticmethod
    def create_store(name, description="", owner=None):
        """
        Create a new store.

        Args:
            name: Store name
            description: Store description (optional)
            owner: User instance who will own the store

        Returns:
            Store instance

        Raises:
            ValidationError: If validation fails
        """
        if not owner:
            raise ValidationError("Store owner is required")

        # Create store
        store = Store.objects.create(
            name=name,
            description=description,
            owner=owner,
            status="active",  # Set to active by default
        )

        # Add owner as a member with 'owner' role
        StoreMembership.objects.create(store=store, user=owner, role="owner")

        return store

    @staticmethod
    def add_member(store, user_id, role):
        """
        Add a user to a store with a specific role.

        Args:
            store: Store instance
            user_id: User ID to add
            role: Role to assign ('owner', 'admin', 'member')

        Returns:
            StoreMembership instance

        Raises:
            ValueError: If user doesn't exist or is already a member
        """
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise ValueError(f"User with ID {user_id} does not exist")

        # Check if user is already a member
        if StoreMembership.objects.filter(store=store, user=user).exists():
            raise ValueError(f"User {user.email} is already a member of store {store.name}")

        # Validate role
        valid_roles = ["owner", "admin", "member"]
        if role not in valid_roles:
            raise ValueError(f"Invalid role '{role}'. Valid roles are: {', '.join(valid_roles)}")

        # Create membership
        membership = StoreMembership.objects.create(store=store, user=user, role=role)

        return membership
