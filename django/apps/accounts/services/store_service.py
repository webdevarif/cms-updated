from apps.posts.services import create_builtin_post_types_for_store
from apps.stores.models import Store, StoreMembership
from apps.themes.models import (
    ColorScheme,
    Theme,
    get_default_colors,
    get_default_dark_colors,
    get_default_typography,
)

from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class StoreService:
    """Service for handling store operations"""

    @staticmethod
    @transaction.atomic
    def create_store(name, description, owner):
        """
        Create a new store and set up owner membership, default theme, and builtin post types
        """
        store = Store.objects.create(name=name, description=description, owner=owner)

        # Create owner membership
        StoreMembership.objects.create(store=store, user=owner, role="owner")

        # Create default theme
        theme, created = Theme.objects.get_or_create(
            store=store,
            name="Default Theme",
            defaults={
                "key": "default",
                "description": "Default theme for the store",
                "is_default": True,
                "typography": get_default_typography(),
            },
        )

        # Create default color scheme
        ColorScheme.objects.get_or_create(
            theme=theme,
            key="default",
            defaults={
                "name": "Default",
                "is_default": True,
                "colors": get_default_colors(),
                "dark_colors": get_default_dark_colors(),
            },
        )

        # Create builtin post types (pages and posts)
        create_builtin_post_types_for_store(store)

        return store

    @staticmethod
    def add_store_member(store, user, role="member"):
        """
        Add a member to a store
        """
        if StoreMembership.objects.filter(store=store, user=user).exists():
            raise ValueError("User is already a member of this store")

        return StoreMembership.objects.create(store=store, user=user, role=role)

    @staticmethod
    def remove_store_member(store, user):
        """
        Remove a member from a store
        """
        try:
            membership = StoreMembership.objects.get(store=store, user=user)
            if membership.role == "owner":
                raise ValueError("Cannot remove store owner")
            membership.delete()
            return True
        except StoreMembership.DoesNotExist:
            raise ValueError("User is not a member of this store")

    @staticmethod
    def update_member_role(store, user, new_role):
        """
        Update a member's role in a store
        """
        try:
            membership = StoreMembership.objects.get(store=store, user=user)
            if membership.role == "owner" and new_role != "owner":
                raise ValueError("Cannot change owner role")
            membership.role = new_role
            membership.save()
            return membership
        except StoreMembership.DoesNotExist:
            raise ValueError("User is not a member of this store")

    @staticmethod
    def get_user_stores(user):
        """
        Get all stores where user is a member
        """
        return Store.objects.filter(memberships__user=user).distinct()

    @staticmethod
    def get_user_owned_stores(user):
        """
        Get stores owned by the user
        """
        return Store.objects.filter(owner=user)

    @staticmethod
    def can_user_access_store(user, store):
        """
        Check if user can access a store
        """
        return store.memberships.filter(user=user).exists() or store.owner == user
