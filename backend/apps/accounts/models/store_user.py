"""
StoreUser model for Digital Farmers CMS.

Store-specific user roles and permissions.
"""
from django.contrib.auth import get_user_model
from django.db import models

from .user import User

User = get_user_model()


class StoreUser(models.Model):
    """Store-specific user roles and permissions"""

    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("staff", "Staff"),
        ("customer", "Customer"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="store_users")
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="store_users")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["user", "store"]]
        indexes = [
            models.Index(fields=["store", "role"]),
            models.Index(fields=["user", "role"]),
        ]
        db_table = "accounts_store_user"

    def __str__(self):
        return f"{self.user.email} - {self.store.name} ({self.role})"

    @property
    def is_owner(self):
        """Check if user is store owner"""
        return self.role == "owner"

    @property
    def is_admin(self):
        """Check if user is admin"""
        return self.role in ["owner", "admin"]

    @property
    def is_staff_role(self):
        """Check if user has staff role"""
        return self.role in ["owner", "admin", "manager", "staff"]
