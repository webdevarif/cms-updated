"""
GiftCard model for giftcards app.
"""

import secrets
import uuid

from core.models import TenantModel
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class GiftCard(TenantModel):
    """
    Store-scoped gift card model for store gift card management.
    """

    GIFT_CARD_TYPES = [
        ("digital", "Digital"),
        ("physical", "Physical"),
        ("promotional", "Promotional"),
        ("refund", "Refund"),
        ("loyalty", "Loyalty"),
    ]

    STATUS_CHOICES = [
        ("inactive", "Inactive"),
        ("active", "Active"),
        ("redeemed", "Redeemed"),
        ("expired", "Expired"),
        ("voided", "Voided"),
    ]

    # Core fields
    code = models.CharField(max_length=12, unique=True, db_index=True)
    initial_balance = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    current_balance = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    currency = models.CharField(max_length=3, default="USD")
    gift_card_type = models.CharField(max_length=20, choices=GIFT_CARD_TYPES, default="digital")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="inactive")

    # Recipient information
    recipient_name = models.CharField(max_length=100, blank=True)
    recipient_email = models.EmailField(blank=True)

    # Sender information
    sender_name = models.CharField(max_length=100, blank=True)
    sender_email = models.EmailField(blank=True)

    # Additional fields
    message = models.TextField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_gift_cards",
    )

    class Meta(TenantModel.Meta):
        db_table = "giftcards_gift_card"
        unique_together = [["store", "code"]]
        indexes = [
            models.Index(fields=["store", "code"]),
            models.Index(fields=["store", "status"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["code"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} - {self.current_balance} {self.currency}"

    @property
    def is_expired(self):
        """Check if gift card is expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @property
    def is_redeemable(self):
        """Check if gift card can be redeemed."""
        return self.status == "active" and not self.is_expired and self.current_balance > 0

    def save(self, *args, **kwargs):
        """Generate code if not set."""
        if not self.code:
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)

    @classmethod
    def generate_unique_code(cls):
        """Generate a unique gift card code."""
        while True:
            code = secrets.token_hex(6).upper()
            if not cls.objects.filter(code=code).exists():
                return code
