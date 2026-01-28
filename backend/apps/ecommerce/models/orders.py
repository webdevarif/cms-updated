"""
Order models for ecommerce app.
"""
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Order(models.Model):
    """
    Order model for ecommerce.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="orders")
    customer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Customer information
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True)

    # Shipping information
    shipping_address = models.JSONField(default=dict)
    billing_address = models.JSONField(default=dict)

    # Notes
    notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "ecommerce_order"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["store", "status"]),
            models.Index(fields=["customer", "status"]),
            models.Index(fields=["order_number"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Order {self.order_number}"

    @property
    def is_paid(self):
        """Check if order is paid"""
        return self.payments.filter(status="completed").exists()

    @property
    def can_cancel(self):
        """Check if order can be cancelled"""
        return self.status in ["pending", "confirmed"]

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate unique order number
            last_order = Order.objects.filter(store=self.store).order_by("order_number").last()
            if last_order:
                last_number = int(last_order.order_number.split("-")[-1])
                self.order_number = f"{self.store.slug.upper()}-{last_number + 1:06d}"
            else:
                self.order_number = f"{self.store.slug.upper()}-000001"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """
    Order item model for ecommerce.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("Product", on_delete=models.SET_NULL, null=True)
    product_variant = models.ForeignKey(
        "ProductVariant", on_delete=models.SET_NULL, null=True, blank=True
    )

    # Product information at time of order
    product_name = models.CharField(max_length=255)
    product_sku = models.CharField(max_length=100, blank=True)
    product_image = models.URLField(blank=True)

    # Pricing
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Product data snapshot
    product_data = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecommerce_order_item"
        ordering = ["order", "created_at"]
        indexes = [
            models.Index(fields=["order", "product"]),
            models.Index(fields=["product", "created_at"]),
        ]

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    def save(self, *args, **kwargs):
        # Calculate total price
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
