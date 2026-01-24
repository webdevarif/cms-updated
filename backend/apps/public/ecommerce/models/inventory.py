"""
Inventory and Payment models.
"""
from django.db import models


class Inventory(models.Model):
    """Inventory tracking for products"""
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    product = models.ForeignKey('ecommerce.Product', on_delete=models.CASCADE, related_name='inventory')
    quantity = models.IntegerField(default=0)
    reserved_quantity = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=10)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'ecommerce'
        db_table = 'ecommerce_inventory'

    def __str__(self):
        return f"{self.product.title} - {self.quantity}"


class InventoryTransaction(models.Model):
    """Track inventory changes"""
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='transactions')

    TRANSACTION_TYPES = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('return', 'Return'),
        ('adjustment', 'Adjustment'),
    ]
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'ecommerce'
        db_table = 'ecommerce_inventory_transaction'
        ordering = ['-created_at']


class PaymentMethod(models.Model):
    """Payment methods for store"""
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    provider = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'ecommerce'
        db_table = 'ecommerce_payment_method'

    def __str__(self):
        return f"{self.name} ({self.provider})"


class Payment(models.Model):
    """Payment record"""
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    order = models.ForeignKey('ecommerce.Order', on_delete=models.CASCADE, related_name='payments')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    transaction_id = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'ecommerce'
        db_table = 'ecommerce_payment'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.id} - {self.amount}"
