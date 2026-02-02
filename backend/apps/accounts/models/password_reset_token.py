"""
Password reset token model for secure password resets.
"""

import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class PasswordResetToken(models.Model):
    """
    Password reset token for secure password resets.

    Stores tokens that expire after a configured time period
    and can only be used once.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="password_reset_tokens"
    )
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "accounts_password_reset_token"
        indexes = [
            models.Index(fields=["token", "expires_at"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["expires_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Password reset token for {self.user.email}"

    @classmethod
    def generate_token(cls, user):
        """
        Generate a secure token for password reset.

        Args:
            user: User instance

        Returns:
            PasswordResetToken instance
        """
        # Generate secure token
        token = secrets.token_urlsafe(32)

        # Calculate expiration time
        expires_at = timezone.now() + timedelta(
            seconds=getattr(settings, "PASSWORD_RESET_TIMEOUT", 3600)
        )

        # Create token instance
        reset_token = cls.objects.create(user=user, token=token, expires_at=expires_at)

        return reset_token

    def is_valid(self):
        """
        Check if token is valid (not used and not expired).

        Returns:
            bool: True if token is valid
        """
        if self.used_at is not None:
            return False

        if timezone.now() > self.expires_at:
            return False

        return True

    def mark_as_used(self):
        """Mark token as used."""
        self.used_at = timezone.now()
        self.save(update_fields=["used_at"])

    @classmethod
    def get_valid_token(cls, token):
        """
        Get valid token by token string.

        Args:
            token: Token string

        Returns:
            PasswordResetToken instance or None
        """
        try:
            reset_token = cls.objects.get(token=token)
            if reset_token.is_valid():
                return reset_token
        except cls.DoesNotExist:
            pass

        return None
