"""
Payment models for ecommerce app.
"""
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class PaymentMethod(models.Model):
    """
    Payment method model for ecommerce.
    """

    METHOD_TYPES = [
        ("credit_card", "Credit Card"),
        ("debit_card", "Debit Card"),
        ("bank_transfer", "Bank Transfer"),
        ("paypal", "PayPal"),
        ("stripe", "Stripe"),
        ("cash_on_delivery", "Cash on Delivery"),
        ("bank_deposit", "Bank Deposit"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(
        "stores.Store", on_delete=models.CASCADE, related_name="payment_methods"
    )
    name = models.CharField(max_length=255)
    method_type = models.CharField(max_length=50, choices=METHOD_TYPES)

    # Configuration
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    # Gateway configuration
    gateway_config = models.JSONField(default=dict)

    # Display settings
    display_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    icon = models.URLField(blank=True)

    # Processing fees
    processing_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    processing_fee_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecommerce_payment_method"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["store", "is_active"]),
            models.Index(fields=["method_type"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.method_type})"

    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure only one default payment method per store
            PaymentMethod.objects.filter(store=self.store, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Payment(models.Model):
    """
    Payment transaction model for ecommerce.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
        ("partially_refunded", "Partially Refunded"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="payments")
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.SET_NULL, null=True, related_name="payments"
    )

    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")

    # Gateway information
    gateway_transaction_id = models.CharField(max_length=255, blank=True)
    gateway_response = models.JSONField(default=dict)

    # Status and timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    # Customer information
    customer_email = models.EmailField()
    customer_ip = models.GenericIPAddressField(null=True, blank=True)

    # Notes
    notes = models.TextField(blank=True)
    failure_reason = models.TextField(blank=True)

    # Refund information
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_reason = models.TextField(blank=True)

    class Meta:
        db_table = "ecommerce_payment"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order", "status"]),
            models.Index(fields=["payment_method", "status"]),
            models.Index(fields=["gateway_transaction_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Payment {self.id} - {self.amount} {self.currency}"

    @property
    def is_successful(self):
        """Check if payment was successful"""
        return self.status == "completed"

    @property
    def can_refund(self):
        """Check if payment can be refunded"""
        return self.status == "completed" and self.refunded_amount < self.amount

    def mark_as_completed(self, transaction_id=None, response_data=None):
        """Mark payment as completed"""
        self.status = "completed"
        self.completed_at = timezone.now()
        if transaction_id:
            self.gateway_transaction_id = transaction_id
        if response_data:
            self.gateway_response = response_data
        self.save(
            update_fields=["status", "completed_at", "gateway_transaction_id", "gateway_response"]
        )

    def mark_as_failed(self, reason=None, response_data=None):
        """Mark payment as failed"""
        self.status = "failed"
        self.failed_at = timezone.now()
        if reason:
            self.failure_reason = reason
        if response_data:
            self.gateway_response = response_data
        self.save(update_fields=["status", "failed_at", "failure_reason", "gateway_response"])

    def refund(self, amount, reason=None):
        """Process refund"""
        if not self.can_refund:
            raise ValueError("Payment cannot be refunded")

        if amount > (self.amount - self.refunded_amount):
            raise ValueError("Refund amount exceeds available amount")

        self.refunded_amount += amount
        if reason:
            self.refund_reason = reason

        if self.refunded_amount >= self.amount:
            self.status = "refunded"
        else:
            self.status = "partially_refunded"

        self.save(update_fields=["refunded_amount", "refund_reason", "status"])
