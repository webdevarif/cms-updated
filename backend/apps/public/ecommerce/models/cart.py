"""
Cart and Order models for ecommerce.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from .constants import StatusChoices

User = get_user_model()


class Cart(models.Model):
    """Shopping cart for anonymous and authenticated users"""
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts'
    )
    session_key = models.CharField(max_length=100, blank=True)
    
    # Status and currency
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.get_cart_choices(),
        default=StatusChoices.ACTIVE
    )
    currency = models.CharField(max_length=3, default='USD')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'ecommerce'
        db_table = 'ecommerce_cart'
        indexes = [
            models.Index(fields=['store', 'user']),
            models.Index(fields=['store', 'session_key']),
        ]
    
    def __str__(self):
        return f"Cart {self.id} - {self.store.name}"
    
    def get_item_count(self):
        """Get total item count in cart"""
        from django.db.models import Sum
        return self.items.aggregate(total=Sum('quantity'))['total'] or 0
    
    def get_subtotal(self):
        """Get subtotal of all items"""
        return sum(item.total_price for item in self.items.all())
    
    def get_tax(self):
        """Get tax amount"""
        return 0
    
    def get_shipping(self):
        """Get shipping amount"""
        return 0
    
    def get_total(self):
        """Get total amount"""
        return self.get_subtotal() + self.get_tax() + self.get_shipping()


class CartItem(models.Model):
    """Item in shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('ecommerce.Product', on_delete=models.CASCADE)
    variant = models.ForeignKey(
        'ecommerce.ProductVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'ecommerce'
        db_table = 'ecommerce_cart_item'
        unique_together = [['cart', 'product', 'variant']]
    
    def save(self, *args, **kwargs):
        """Calculate total price before saving"""
        price = self.variant.get_price() if self.variant else self.product.base_price
        self.unit_price = price
        self.total_price = price * self.quantity
        super().save(*args, **kwargs)
    
    @property
    def total_price(self):
        """Get total price"""
        return self.unit_price * self.quantity


class Order(models.Model):
    """Order model"""
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='orders')
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    customer = models.ForeignKey(
        'ecommerce.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    cart = models.ForeignKey(
        Cart,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Order details
    order_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.get_order_choices(),
        default=StatusChoices.PENDING
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[
            (StatusChoices.PENDING, 'Pending'),
            ('paid', 'Paid'),
            (StatusChoices.FAILED, 'Failed'),
            (StatusChoices.REFUNDED, 'Refunded')
        ],
        default=StatusChoices.PENDING
    )
    fulfillment_status = models.CharField(
        max_length=20,
        choices=StatusChoices.get_fulfillment_choices(),
        default=StatusChoices.UNFULFILLED
    )
    currency = models.CharField(max_length=3, default='USD')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Customer info
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True)
    
    # Shipping address
    shipping_name = models.CharField(max_length=255)
    shipping_address1 = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100)
    
    # Billing address
    billing_name = models.CharField(max_length=255)
    billing_address1 = models.CharField(max_length=255)
    billing_address2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100)
    billing_state = models.CharField(max_length=100)
    billing_postal_code = models.CharField(max_length=20)
    billing_country = models.CharField(max_length=100)
    
    # Additional fields
    notes = models.TextField(blank=True)
    customer_notes = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'ecommerce'
        db_table = 'ecommerce_order'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['store', 'status']),
            models.Index(fields=['order_number']),
        ]
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def save(self, *args, **kwargs):
        """Generate order number if not set"""
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Generate unique order number"""
        import random
        import string
        from django.utils import timezone
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        random_str = ''.join(random.choices(string.digits, k=4))
        return f"ORD-{timestamp}-{random_str}"
    
    def calculate_totals(self):
        """Calculate order totals"""
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.tax = 0
        self.shipping = 0
        self.discount = 0
        self.total = self.subtotal + self.tax + self.shipping - self.discount
    
    def is_paid(self):
        """Check if order is paid"""
        return self.payment_status == 'paid'
    
    def is_fulfilled(self):
        """Check if order is fulfilled"""
        return self.fulfillment_status == 'fulfilled'


class OrderItem(models.Model):
    """Item in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('ecommerce.Product', on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey(
        'ecommerce.ProductVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'ecommerce'
        db_table = 'ecommerce_order_item'
    
    @property
    def total_price(self):
        return self.unit_price * self.quantity
