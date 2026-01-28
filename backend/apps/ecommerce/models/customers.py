"""
Customer models for ecommerce app.
"""
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class CustomerProfile(models.Model):
    """
    Extended customer profile for ecommerce.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="ecommerce_profile")
    store = models.ForeignKey(
        "stores.Store", on_delete=models.CASCADE, related_name="customer_profiles"
    )
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=[
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
            ("prefer_not_to_say", "Prefer not to say"),
        ],
        blank=True,
    )
    marketing_consent = models.BooleanField(default=False)
    email_marketing_consent = models.BooleanField(default=False)
    sms_marketing_consent = models.BooleanField(default=False)
    total_orders = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_order_date = models.DateTimeField(null=True, blank=True)
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecommerce_customer_profiles"
        unique_together = ["user", "store"]
        app_label = "ecommerce"

    def __str__(self):
        return f"{self.user.email} - {self.store.name}"

    @property
    def full_name(self):
        """Get customer's full name."""
        return f"{self.first_name} {self.last_name}".strip()
