"""
Cart models for ecommerce app.
"""

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Cart(models.Model):
    """
    Shopping cart model.
    """

    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="carts")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="carts"
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Active"),
            ("converted", "Converted to Order"),
            ("abandoned", "Abandoned"),
        ],
        default="active",
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="USD")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecommerce_carts"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["session_key", "status"]),
            models.Index(fields=["status", "updated_at"]),
        ]
        ordering = ["-updated_at"]
        app_label = "ecommerce"

    def __str__(self):
        return f"Cart for {self.user or self.session_key}"

    @property
    def item_count(self):
        """Get total number of items in cart."""
        return self.items.aggregate(total=models.Sum("quantity"))["total"] or 0


class CartItem(models.Model):
    """
    Cart item model.
    """

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="cart_items")
    variant = models.ForeignKey(
        "ProductVariant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecommerce_cart_items"
        unique_together = ["cart", "product", "variant"]
        app_label = "ecommerce"

    def __str__(self):
        return f"{self.quantity}x {self.product.title}"

    def save(self, *args, **kwargs):
        """Calculate line total before saving."""
        self.line_total = self.price * self.quantity
        super().save(*args, **kwargs)
