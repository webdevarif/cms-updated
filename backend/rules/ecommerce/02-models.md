# Ecommerce Models

## 2. Core Models

### 2.1 Model Inheritance

All ecommerce models must use explicit `store` ForeignKey for store scoping:

```python
from django.db import models
```

### 2.2 Product Models

#### Product
```python
# apps/public/ecommerce/models/products.py
from django.db import models

class Product(models.Model):
    """
    Store-scoped product model with comprehensive e-commerce features
    """
    # Core Identification
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique_for_store=True)
    sku = models.CharField(max_length=100, unique=True)
    upc = models.CharField(max_length=12, blank=True, null=True, unique=True)

    # Descriptions
    description = models.TextField(blank=True)
    short_description = models.TextField(max_length=500, blank=True)

    # Pricing
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    compare_at_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Inventory
    track_inventory = models.BooleanField(default=True)
    inventory_quantity = models.IntegerField(default=0)
    allow_backorder = models.BooleanField(default=False)
    backorder_quantity = models.IntegerField(default=0, help_text="Quantity available for backorder")

    # Shipping
    requires_shipping = models.BooleanField(default=True)
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight in grams"
    )

    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    is_featured = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    # SEO
    seo_title = models.CharField(max_length=60, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    seo_keywords = models.CharField(max_length=255, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['store', 'status']),
            models.Index(fields=['store', 'is_available']),
            models.Index(fields=['store', 'is_featured']),
            models.Index(fields=['store', 'type']),
            models.Index(fields=['store', 'sku']),
            models.Index(fields=['store', 'status', 'is_available']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['store', 'sku'],
                name='unique_store_sku'
            ),
            models.UniqueConstraint(
                fields=['store', 'slug'],
                name='unique_store_slug'
            )
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure slug is unique
            queryset = self.__class__.objects.filter(
                store=self.store,
                slug__startswith=self.slug
            )
            if queryset.exists():
                self.slug = f"{self.slug}-{queryset.count() + 1}"
        super().save(*args, **kwargs)

    @property
    def is_in_stock(self):
        if not self.track_inventory:
            return True
        return self.inventory_quantity > 0

    @property
    def can_backorder(self):
        return self.allow_backorder and self.backorder_quantity > 0

    @property
    def inventory_status(self):
        """Get current inventory status"""
        if not self.is_available or self.status != 'active':
            return 'unavailable'
        if not self.track_inventory:
            return 'in_stock'
        if self.inventory_quantity > 0:
            return 'in_stock'
        if self.allow_backorder and self.backorder_quantity > 0:
            new_quantity = self.inventory_quantity - quantity
            if new_quantity < 0 and not self.allow_backorder:
                return False
            self.inventory_quantity = max(new_quantity, 0)
            if new_quantity < 0:
                self.backorder_quantity += abs(new_quantity)
        elif action == 'increase':
            self.inventory_quantity += quantity
        elif action == 'set':
            self.inventory_quantity = quantity

        self.save()
        return True

    # Media relationships
    primary_image = models.ForeignKey(
        'media.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_products'
    )

    # Relations
    categories = models.ManyToManyField(
        'Category',
        related_name='products',
        blank=True
    )
    collections = models.ManyToManyField(
        'Collection',
        related_name='products',
        blank=True
    )
    tags = models.ManyToManyField(
        'ProductTag',
        related_name='products',
        blank=True
    )

    # Digital product specific
    digital_file = models.FileField(
        upload_to='digital_products/%Y/%m/',
        null=True,
        blank=True
    )
    download_limit = models.PositiveIntegerField(
        default=3,
        help_text="Number of times the file can be downloaded"
    )
    download_expiry_days = models.PositiveIntegerField(
        default=30,
        help_text="Number of days the download link is valid"
    )

    # Inventory alerts
    low_stock_threshold = models.PositiveIntegerField(
        default=5,
        help_text="When to trigger low stock alerts"
    )

    # Advanced options
    requires_shipping_address = models.BooleanField(default=True)
    is_giftcard = models.BooleanField(default=False)
    giftcard_expiry_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of days until gift card expires"
    )

    # Type of product
    TYPE_CHOICES = [
        ('physical', 'Physical'),
        ('digital', 'Digital'),
        ('service', 'Service'),
        ('gift_card', 'Gift Card')
    ]
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='physical'
    )

    # Tax
    tax_class = models.ForeignKey(
        'TaxClass',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    seo_description = models.CharField(max_length=500, blank=True)

    # Media relationships
    featured_image = models.ForeignKey(
        'media.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='featured_products'
    )

    # Category relationships
    categories = models.ManyToManyField(
        'ProductCategory',
        blank=True,
        related_name='products'
    )

    class Meta:
        db_table = 'ecommerce_product'
        unique_together = [['store', 'slug'], ['store', 'sku']]
        indexes = [
            models.Index(fields=['store', 'status']),
            models.Index(fields=['store', 'featured']),
            models.Index(fields=['sku']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_current_price(self):
        """Get current price from variants or base price"""
        variant = self.variants.first()
        return variant.price if variant else self.base_price or 0

#### ProductVariant
```python
class ProductVariant(TenantModel):
    """
    Product variant with store scoping
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    barcode = models.CharField(max_length=50, blank=True)

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Inventory
    inventory_quantity = models.IntegerField(default=0)
    inventory_policy = models.CharField(max_length=20, choices=INVENTORY_POLICY_CHOICES, default='deny')

    # Physical attributes
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Variant options
    option1 = models.CharField(max_length=100, blank=True)
    option2 = models.CharField(max_length=100, blank=True)
    option3 = models.CharField(max_length=100, blank=True)

    # Position for ordering
    position = models.IntegerField(default=0)

    class Meta:
        db_table = 'ecommerce_product_variant'
        unique_together = [['store', 'sku'], ['product', 'sku']]
        indexes = [
            models.Index(fields=['store', 'product']),
            models.Index(fields=['product', 'position']),
            models.Index(fields=['sku']),
        ]
        ordering = ['position']
```

#### ProductCategory
```python
class ProductCategory(TenantModel):
    """
    Store-scoped product category with hierarchical structure
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)

    # Hierarchical structure
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    # Media
    image = models.ForeignKey(
        'media.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='category_images'
    )

    # SEO fields
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.CharField(max_length=500, blank=True)

    # Position and status
    position = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'ecommerce_product_category'
        unique_together = [['store', 'slug']]
        verbose_name_plural = 'Product Categories'
        indexes = [
            models.Index(fields=['store', 'parent']),
            models.Index(fields=['store', 'position']),
            models.Index(fields=['store', 'is_active']),
        ]
        ordering = ['position']

    def clean(self):
        if self.parent and self.parent.parent == self:
            raise ValidationError("Cannot create circular category reference")
```

### 2.2 Cart Models

#### Cart
```python
class Cart(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=CART_STATUS_CHOICES, default='active')
    currency = models.CharField(max_length=3, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['store', 'session_key']
        indexes = [
            models.Index(fields=['store', 'customer']),
            models.Index(fields=['store', 'session_key']),
            models.Index(fields=['status']),
        ]

    def get_item_count(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    def get_subtotal(self):
        return sum(item.get_total() for item in self.items.all())

    def get_tax(self):
        # Tax calculation logic
        return Decimal('0.00')

    def get_shipping(self):
        # Shipping calculation logic
        return Decimal('0.00')

    def get_total(self):
        return self.get_subtotal() + self.get_tax() + self.get_shipping()
```

#### CartItem
```python
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cart', 'product', 'variant']
        indexes = [
            models.Index(fields=['cart', 'product']),
            models.Index(fields=['cart', 'variant']),
        ]

    def clean(self):
        if self.variant and self.variant.product != self.product:
            raise ValidationError("Variant must belong to the specified product")

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def get_total(self):
        return self.total_price
```

### 2.3 Order Models

#### Order
```python
class Order(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    fulfillment_status = models.CharField(max_length=20, choices=FULFILLMENT_STATUS_CHOICES, default='unfulfilled')
    currency = models.CharField(max_length=3, default='USD')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    shipping = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Address fields
    billing_address = models.JSONField(default=dict)
    shipping_address = models.JSONField(default=dict)

    # Additional fields
    notes = models.TextField(blank=True)
    customer_notes = models.TextField(blank=True)
    tags = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['store', 'status']),
            models.Index(fields=['store', 'customer']),
            models.Index(fields=['order_number']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        random_str = ''.join(random.choices(string.digits, k=4))
        return f"ORD-{timestamp}-{random_str}"

    def calculate_totals(self):
        self.subtotal = sum(item.get_total() for item in self.items.all())
        self.tax = self.calculate_tax()
        self.shipping = self.calculate_shipping()
        self.discount = self.calculate_discount()
        self.total = self.subtotal + self.tax + self.shipping - self.discount

    def is_paid(self):
        return self.payment_status == 'paid'

    def is_fulfilled(self):
        return self.fulfillment_status == 'fulfilled'
```

#### OrderItem
```python
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['order', 'product']),
            models.Index(fields=['order', 'variant']),
        ]

    def get_total(self):
        return self.total_price
```

### 2.4 Customer Models

#### Customer
```python
class Customer(models.Model):
    user = models.OneToOneField(GlobalUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)

    # Marketing preferences
    email_marketing = models.BooleanField(default=True)
    sms_marketing = models.BooleanField(default=False)

    # Statistics
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_count = models.IntegerField(default=0)
    last_order_at = models.DateTimeField(null=True, blank=True)

    # Addresses
    default_billing_address = models.JSONField(default=dict)
    default_shipping_address = models.JSONField(default=dict)

    # Metadata
    tags = models.JSONField(default=list)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['total_spent']),
            models.Index(fields=['order_count']),
            models.Index(fields=['last_order_at']),
        ]

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def update_statistics(self):
        orders = Order.objects.filter(customer=self)
        self.order_count = orders.count()
        self.total_spent = orders.aggregate(total=models.Sum('total'))['total'] or 0
        last_order = orders.order_by('-created_at').first()
        self.last_order_at = last_order.created_at if last_order else None
        self.save()
```

### 2.3 Product Variants and Options

#### OptionType
```python
class OptionType(models.Model):
    """Product option types (e.g., Size, Color)"""
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    display_name = models.CharField(max_length=50)
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ['position']
        unique_together = ['store', 'name']
        indexes = [
            models.Index(fields=['store', 'position']),
        ]

class OptionValue(models.Model):
    """Values for product options (e.g., Red, Blue, Large, Small)"""
    option_type = models.ForeignKey(OptionType, on_delete=models.CASCADE, related_name='values')
    name = models.CharField(max_length=100)
    presentation = models.CharField(max_length=100)
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ['position']

class ProductVariant(models.Model):
    """Product variants for different options"""
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    sku = models.CharField(max_length=100, unique=True)
    barcode = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    inventory_quantity = models.IntegerField(default=0)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    requires_shipping = models.BooleanField(default=True)
    position = models.IntegerField(default=0)
    option_values = models.ManyToManyField(OptionValue, related_name='variants')

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f"{self.product.title} - {self.sku}"
```

### 2.4 Inventory Management

```python
class InventoryItem(models.Model):
    """Tracks individual inventory items for better stock control"""
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    sku = models.CharField(max_length=100, unique=True)
    product_variant = models.OneToOneField(
        ProductVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    quantity = models.IntegerField(default=0)
    committed = models.IntegerField(default=0)  # Reserved in carts/orders
    available = models.IntegerField(default=0)  # quantity - committed
    last_counted = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['store', 'sku']),
            models.Index(fields=['store', 'product_variant']),
        ]

    def update_available_quantity(self):
        """Update available quantity based on current stock and commitments"""
        self.available = max(0, self.quantity - self.committed)
        self.save(update_fields=['available', 'updated_at'])
        return self.available

class StockMovement(models.Model):
    """Tracks all inventory changes"""
    MOVEMENT_TYPES = [
        ('purchase', 'Purchase Order'),
        ('sale', 'Sale'),
        ('return', 'Return'),
        ('adjustment', 'Adjustment'),
        ('damaged', 'Damaged'),
        ('found', 'Found'),
        ('lost', 'Lost'),
    ]

    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='movements')
    quantity = models.IntegerField()
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    reference = models.CharField(max_length=100, blank=True)  # PO#, Order#, etc.
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['inventory_item', 'created_at']),
        ]
```

### 2.5 Collection Models

#### Collection
```python
class Collection(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ForeignKey('media.MediaFile', on_delete=models.SET_NULL, null=True, blank=True)
    is_smart = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.CharField(max_length=20, choices=SORT_ORDER_CHOICES, default='manual')
    created_by = models.ForeignKey(GlobalUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['store', 'slug']
        indexes = [
            models.Index(fields=['store', 'is_active']),
            models.Index(fields=['store', 'is_smart']),
        ]
```

#### CollectionCondition
```python
class CollectionCondition(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='conditions')
    field = models.CharField(max_length=50, choices=CONDITION_FIELD_CHOICES)
    operator = models.CharField(max_length=20, choices=CONDITION_OPERATOR_CHOICES)
    value = models.JSONField()
    position = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['collection', 'position']),
        ]
```

### 2.6 Coupon Models

#### CouponCampaign
```python
class CouponCampaign(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(GlobalUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['store', 'is_active']),
            models.Index(fields=['starts_at', 'ends_at']),
        ]
```

#### Coupon
```python
class Coupon(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    campaign = models.ForeignKey(CouponCampaign, on_delete=models.CASCADE, null=True, blank=True)
    code = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=20, choices=COUPON_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usage_limit = models.IntegerField(null=True, blank=True)
    usage_limit_per_customer = models.IntegerField(null=True, blank=True)
    used_count = models.IntegerField(default=0)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(GlobalUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['store', 'code']),
            models.Index(fields=['store', 'is_active']),
            models.Index(fields=['starts_at', 'ends_at']),
        ]

    def is_valid(self, customer=None, cart_total=0):
        now = timezone.now()

        if not self.is_active:
            return False, "Coupon is inactive"

        if now < self.starts_at:
            return False, "Coupon not yet active"

        if now > self.ends_at:
            return False, "Coupon has expired"

        if cart_total < self.minimum_order_amount:
            return False, f"Minimum order amount of {self.minimum_order_amount} required"

        if self.usage_limit and self.used_count >= self.usage_limit:
            return False, "Coupon usage limit reached"

        if customer and self.usage_limit_per_customer:
            customer_usage = Order.objects.filter(
                customer=customer,
                coupons__code=self.code
            ).count()
            if customer_usage >= self.usage_limit_per_customer:
                return False, "Customer usage limit reached"

        return True, "Valid"

    def apply_discount(self, cart_total):
        if self.type == 'fixed_amount':
            return min(self.value, cart_total)
        elif self.type == 'percentage':
            return cart_total * (self.value / 100)
        elif self.type == 'free_shipping':
            return 0  # Handled separately in shipping calculation
        return 0
```

### 2.7 Inventory Models

#### Inventory
```python
class Inventory(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    reserved = models.IntegerField(default=0)
    available = models.IntegerField(default=0)
    location = models.CharField(max_length=100, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['store', 'product', 'variant']
        indexes = [
            models.Index(fields=['store', 'product']),
            models.Index(fields=['store', 'variant']),
        ]

    def save(self, *args, **kwargs):
        self.available = self.quantity - self.reserved
        super().save(*args, **kwargs)

    def reserve(self, quantity):
        if self.available >= quantity:
            self.reserved += quantity
            self.save()
            return True
        return False

    def release(self, quantity):
        if self.reserved >= quantity:
            self.reserved -= quantity
            self.save()
            return True
        return False

    def deduct(self, quantity):
        if self.reserved >= quantity:
            self.reserved -= quantity
            self.quantity -= quantity
            self.save()
            return True
        return False
```

#### InventoryTransaction
```python
class InventoryTransaction(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(GlobalUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['inventory', 'type']),
            models.Index(fields=['created_at']),
        ]
```

### 2.8 Payment Models

#### PaymentMethod
```python
class PaymentMethod(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['store', 'is_active']),
        ]
```

#### Payment
```python
class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=255, blank=True)
    gateway_response = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['order', 'status']),
            models.Index(fields=['transaction_id']),
        ]
```
