"""
User model for Digital Farmers CMS.

Global user model - exists across all stores with JWT authentication.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class GlobalUserManager(BaseUserManager):
    """Global user manager - users exist across all stores"""

    def create_user(self, email, username=None, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        # Generate username if not provided
        if not username:
            username = email.split("@")[0]

        email = self.normalize_email(email)

        # Check global uniqueness
        if self.model.objects.filter(email=email).exists():
            raise ValueError(f"User with email '{email}' already exists")
        if self.model.objects.filter(username=username).exists():
            raise ValueError(f"User with username '{username}' already exists")

        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        # Log user creation
        from apps.logs.tasks import log_event_async

        log_event_async.delay(
            {
                "event_type": "create_user_accounts",
                "message": f"User created: {email}",
                "user_id": user.id,
                "object_id": user.id,
                "metadata": {
                    "email": email,
                    "username": username,
                    "is_superuser": extra_fields.get("is_superuser", False),
                },
            }
        )

        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Global user model - exists across all stores"""

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    # Global fields (no store)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Fix reverse accessor conflicts
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        related_name="custom_user_groups",
        related_query_name="custom_user",
        help_text="The groups this user belongs to.",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        related_name="custom_user_permissions",
        related_query_name="custom_user",
        help_text="Specific permissions for this user.",
    )

    objects = GlobalUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "accounts_user"

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Return the user's short name"""
        return self.first_name or self.username

    def has_role(self, role_name, store=None):
        """Check if user has a specific role in a store"""
        if not store:
            # If no store specified, check if user has any global roles
            return self.is_superuser or self.is_staff

        try:
            from apps.stores.models import StoreMember

            StoreMember.objects.get(user=self, store=store, role=role_name, is_active=True)
            return True
        except StoreMember.DoesNotExist:
            return False

    def get_store_role(self, store):
        """Get user's role in a specific store"""
        try:
            from apps.stores.models import StoreMember

            membership = StoreMember.objects.get(user=self, store=store, is_active=True)
            return membership.role
        except StoreMember.DoesNotExist:
            return None

    def get_store_roles(self):
        """Get all store roles for this user"""
        try:
            from apps.stores.models import StoreMember

            memberships = StoreMember.objects.filter(user=self, is_active=True).select_related(
                "store"
            )
            return {membership.store.slug: membership.role for membership in memberships}
        except Exception:
            return {}

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_email = None

        if not is_new:
            old_instance = User.objects.get(pk=self.pk)
            old_email = old_instance.email

        super().save(*args, **kwargs)

        # Log user updates (but not creation - that's handled in manager)
        if not is_new and old_email != self.email:
            from apps.logs.tasks import log_event_async

            log_event_async.delay(
                {
                    "event_type": "update_user_accounts",
                    "message": f"User updated: {old_email} → {self.email}",
                    "user_id": self.id,
                    "object_id": self.id,
                    "metadata": {
                        "old_email": old_email,
                        "new_email": self.email,
                        "username": self.username,
                    },
                }
            )
