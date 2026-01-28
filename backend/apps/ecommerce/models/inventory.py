"""
Inventory models for ecommerce app.
"""
from django.db import models


class Inventory(models.Model):
    """
    Inventory tracking model.
    """

    product = models.OneToOneField("Product", on_delete=models.CASCADE, related_name="inventory")
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    track_quantity = models.BooleanField(default=True)
    allow_backorders = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecommerce_inventory"
        app_label = "ecommerce"

    def __str__(self):
        return f"Inventory for {self.product.title}"

    @property
    def available_quantity(self):
        """Get available quantity (total - reserved)."""
        return max(0, self.quantity - self.reserved_quantity)

    @property
    def is_low_stock(self):
        """Check if product is low on stock."""
        return self.track_quantity and self.available_quantity <= self.low_stock_threshold

    @property
    def is_out_of_stock(self):
        """Check if product is out of stock."""
        return self.track_quantity and self.available_quantity <= 0
