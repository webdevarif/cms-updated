"""
Role management services for store RBAC
"""

from apps.stores.models import Store, StoreAPIKey, StoreRole, StoreUserRole
from rest_framework_api_key.models import APIKey

from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify


class RoleService:
    """Service for managing store roles and permissions"""

    # Define available actions for roles
    AVAILABLE_ACTIONS = [
        "manage_products",  # Create, update, delete products
        "view_orders",  # View orders and order details
        "manage_orders",  # Update order status, process refunds
        "manage_settings",  # Store settings, configurations
        "manage_staff",  # Assign/remove roles, manage staff
        "view_analytics",  # View store analytics and reports
        "manage_content",  # Manage pages, blog posts, content
        "view_customers",  # View customer information
        "manage_inventory",  # Manage stock levels, inventory
        "manage_discounts",  # Create and manage discount codes
    ]

    @staticmethod
    def create_role(store, name, actions, description="", created_by=None):
        """
        Create a new role for a store

        Args:
            store: Store instance
            name: Role name (e.g., "Manager", "Support Staff")
            actions: List of allowed actions
            description: Optional description
            created_by: User creating the role

        Returns:
            StoreRole instance
        """
        # Validate actions
        invalid_actions = set(actions) - set(RoleService.AVAILABLE_ACTIONS)
        if invalid_actions:
            raise ValueError(f"Invalid actions: {invalid_actions}")

        # Generate unique slug
        base_slug = slugify(name)
        slug = base_slug
        counter = 1

        while StoreRole.objects.filter(store=store, slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        role = StoreRole.objects.create(
            store=store, name=name, slug=slug, description=description, actions=actions
        )

        return role

    @staticmethod
    def update_role(role, name=None, actions=None, description=None):
        """
        Update an existing role

        Args:
            role: StoreRole instance
            name: New name (optional)
            actions: New actions list (optional)
            description: New description (optional)

        Returns:
            Updated StoreRole instance
        """
        if name is not None:
            role.name = name
            # Update slug if name changed
            base_slug = slugify(name)
            slug = base_slug
            counter = 1

            while (
                StoreRole.objects.filter(store=role.store, slug=slug).exclude(pk=role.pk).exists()
            ):
                slug = f"{base_slug}-{counter}"
                counter += 1

            role.slug = slug

        if actions is not None:
            # Validate actions
            invalid_actions = set(actions) - set(RoleService.AVAILABLE_ACTIONS)
            if invalid_actions:
                raise ValueError(f"Invalid actions: {invalid_actions}")
            role.actions = actions

        if description is not None:
            role.description = description

        role.save()
        return role

    @staticmethod
    def delete_role(role):
        """
        Delete a role (only if no users are assigned)

        Args:
            role: StoreRole instance

        Returns:
            bool indicating success
        """
        if role.user_assignments.exists():
            raise ValueError("Cannot delete role with assigned users")

        role.delete()
        return True

    @staticmethod
    def assign_role(user, store, role, assigned_by=None):
        """
        Assign a role to a user for a specific store

        Args:
            user: User instance
            store: Store instance
            role: StoreRole instance
            assigned_by: User making the assignment

        Returns:
            StoreUserRole instance
        """
        # Remove any existing role assignments for this user/store
        StoreUserRole.objects.filter(user=user, store=store).delete()

        assignment = StoreUserRole.objects.create(
            user=user, store=store, role=role, assigned_by=assigned_by
        )

        return assignment

    @staticmethod
    def remove_role(user, store):
        """
        Remove all role assignments for a user in a store

        Args:
            user: User instance
            store: Store instance

        Returns:
            Number of assignments removed
        """
        count, _ = StoreUserRole.objects.filter(user=user, store=store).delete()
        return count

    @staticmethod
    def user_has_action(user, store, action):
        """
        Check if a user has permission for a specific action in a store

        Args:
            user: User instance
            store: Store instance
            action: Action to check

        Returns:
            bool indicating permission
        """
        # Store owners have all permissions
        if store.owner == user:
            return True

        # Check user role assignments
        user_roles = StoreUserRole.objects.filter(user=user, store=store).select_related("role")

        for user_role in user_roles:
            if action in user_role.role.actions:
                return True

        return False

    @staticmethod
    def get_user_actions(user, store):
        """
        Get all actions a user can perform in a store

        Args:
            user: User instance
            store: Store instance

        Returns:
            Set of allowed actions
        """
        actions = set()

        # Store owners have all permissions
        if store.owner == user:
            actions.update(RoleService.AVAILABLE_ACTIONS)
            return actions

        # Get actions from role assignments
        user_roles = StoreUserRole.objects.filter(user=user, store=store).select_related("role")

        for user_role in user_roles:
            actions.update(user_role.role.actions)

        return actions

    @staticmethod
    def get_store_users_with_roles(store):
        """
        Get all users with their roles for a store

        Args:
            store: Store instance

        Returns:
            QuerySet of StoreUserRole with related data
        """
        return (
            StoreUserRole.objects.filter(store=store)
            .select_related("user", "role")
            .order_by("user__email")
        )


class APIKeyService:
    """Service for managing store API keys"""

    @staticmethod
    def create_api_key(store, name, actions, created_by=None):
        """
        Create a new API key for a store

        Args:
            store: Store instance
            name: Human-readable name for the key
            actions: List of allowed actions
            created_by: User creating the key

        Returns:
            tuple: (StoreAPIKey instance, API key string)
        """
        # Validate actions
        invalid_actions = set(actions) - set(RoleService.AVAILABLE_ACTIONS)
        if invalid_actions:
            raise ValueError(f"Invalid actions: {invalid_actions}")

        api_key, key = StoreAPIKey.objects.create_key(
            store=store, name=name, actions=actions, created_by=created_by
        )

        return api_key, key

    @staticmethod
    def update_api_key(api_key, name=None, actions=None):
        """
        Update an existing API key

        Args:
            api_key: StoreAPIKey instance
            name: New name (optional)
            actions: New actions list (optional)

        Returns:
            Updated StoreAPIKey instance
        """
        if name is not None:
            api_key.name = name

        if actions is not None:
            # Validate actions
            invalid_actions = set(actions) - set(RoleService.AVAILABLE_ACTIONS)
            if invalid_actions:
                raise ValueError(f"Invalid actions: {invalid_actions}")
            api_key.actions = actions

        api_key.save()
        return api_key

    @staticmethod
    def revoke_api_key(api_key):
        """
        Revoke an API key

        Args:
            api_key: StoreAPIKey instance

        Returns:
            bool indicating success
        """
        api_key.revoked = True
        api_key.save()
        return True

    @staticmethod
    def update_last_used(api_key):
        """
        Update the last used timestamp for an API key

        Args:
            api_key: StoreAPIKey instance
        """
        api_key.last_used_at = timezone.now()
        api_key.save(update_fields=["last_used_at"])

    @staticmethod
    def get_store_api_keys(store):
        """
        Get all API keys for a store

        Args:
            store: Store instance

        Returns:
            QuerySet of StoreAPIKey
        """
        return StoreAPIKey.objects.filter(store=store).order_by("-created")
