import secrets
import string

from core.libs.utils import generate_unique_id, generate_unique_slug
from rest_framework_api_key.models import AbstractAPIKey

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify

User = get_user_model()


class Store(models.Model):
    """Store model for multi-tenant functionality"""

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("pending", "Pending"),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_stores")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    access_code = models.CharField(max_length=6, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_store"  # Keep existing table name
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.access_code:
            self.access_code = generate_unique_id(6)
        super().save(*args, **kwargs)


class StoreMembership(models.Model):
    """Store membership model for managing access permissions"""

    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("member", "Member"),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="store_memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_storemembership"  # Keep existing table name
        unique_together = ["store", "user"]
        ordering = ["role", "joined_at"]

    def __str__(self):
        return f"{self.user.email} - {self.store.name} ({self.role})"


class StoreRole(models.Model):
    """Custom roles for stores with granular permissions"""

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="roles")
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    actions = models.JSONField(default=list, help_text="List of allowed actions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_storerole"  # Keep existing table name
        unique_together = ["store", "slug"]
        ordering = ["name"]

    def __str__(self):
        return f"{self.store.name} - {self.name}"


class StoreUserRole(models.Model):
    """Assign users to specific roles within stores"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="store_roles")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="user_role_assignments")
    role = models.ForeignKey(StoreRole, on_delete=models.CASCADE, related_name="user_assignments")
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="role_assignments_made"
    )

    class Meta:
        db_table = "accounts_storeuserrole"  # Keep existing table name
        unique_together = ["user", "store", "role"]
        ordering = ["user__email", "assigned_at"]

    def __str__(self):
        return f"{self.user.email} - {self.store.name} ({self.role.name})"


class StoreAPIKey(AbstractAPIKey):
    """Store-specific API keys with action permissions"""

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="api_keys")
    name = models.CharField(max_length=100, help_text="Human-readable name for the API key")
    actions = models.JSONField(default=list, help_text="List of allowed actions")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="api_keys_created"
    )
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "accounts_storeapikey"  # Keep existing table name
        ordering = ["-created"]

    def __str__(self):
        return f"{self.store.name} - {self.name}"

    def has_permission(self, action):
        """Check if API key has permission for specific action"""
        return action in self.actions
