"""
Product models for ecommerce.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify


class Product(models.Model):
    """
    Store-scoped product model with comprehensive e-commerce features
    """
    
    class Meta:
        app_label = 'ecommerce'
    
    # Core Identification
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    sku = models.CharField(max_length=100)
    upc = models.CharField(max_length=12, blank=True, null=True)
    
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
    backorder_quantity = models.IntegerField(default=0)
    
    # Shipping
    requires_shipping = models.BooleanField(default=True)
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
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
    
    # Product Type
    TYPE_CHOICES = [
        ('physical', 'Physical'),
        ('digital', 'Digital'),
        ('service', 'Service'),
        ('gift_card', 'Gift Card')
    ]
    product_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='physical'
    )
    
    # Digital Product
    digital_file = models.FileField(
        upload_to='digital_products/%Y/%m/',
        null=True,
        blank=True
    )
    digital_file_media = models.ForeignKey(
        'mediafile.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='digital_products',
        help_text="Digital product file stored via MediaService"
    )
    download_limit = models.PositiveIntegerField(
        default=3,
        null=True,
        blank=True
    )
    download_expiry_days = models.PositiveIntegerField(
        default=30,
        null=True,
        blank=True
    )
    
    # Gift Card
    is_giftcard = models.BooleanField(default=False)
    giftcard_expiry_days = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    
    # Tax
    tax_class = models.ForeignKey(
        'TaxClass',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # SEO
    seo_title = models.CharField(max_length=60, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    seo_keywords = models.CharField(max_length=255, blank=True)
    
    # Media
    primary_image = models.ForeignKey(
        'mediafile.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_products'
    )
    featured_image = models.ForeignKey(
        'mediafile.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='featured_products'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'ecommerce'
        db_table = 'ecommerce_product'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['store', 'status']),
            models.Index(fields=['store', 'is_available']),
            models.Index(fields=['store', 'is_featured']),
            models.Index(fields=['store', 'sku']),
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
        super().save(*args, **kwargs)
    
    def set_primary_image_from_upload(self, uploaded_file, uploaded_by=None):
        """Set primary image using MediaService upload"""
        from core.media_utils import upload_to_mediafile
        
        media_file = upload_to_mediafile(
            store=self.store,
            file_obj=uploaded_file,
            uploaded_by=uploaded_by,
            folder_name='product_images',
            alt_text=f"Primary image for {self.title}",
            description=f"Primary image for product: {self.title}"
        )
        
        self.primary_image = media_file
        self.save(update_fields=['primary_image'])
        return media_file
    
    def set_featured_image_from_upload(self, uploaded_file, uploaded_by=None):
        """Set featured image using MediaService upload"""
        from core.media_utils import upload_to_mediafile
        
        media_file = upload_to_mediafile(
            store=self.store,
            file_obj=uploaded_file,
            uploaded_by=uploaded_by,
            folder_name='product_images',
            alt_text=f"Featured image for {self.title}",
            description=f"Featured image for product: {self.title}"
        )
        
        self.featured_image = media_file
        self.save(update_fields=['featured_image'])
        return media_file
    
    def upload_digital_file(self, uploaded_file, uploaded_by=None):
        """Upload digital product file using MediaService"""
        from core.media_utils import upload_to_mediafile
        
        media_file = upload_to_mediafile(
            store=self.store,
            file_obj=uploaded_file,
            uploaded_by=uploaded_by,
            folder_name='digital_products',
            alt_text=f"Digital file for {self.title}",
            description=f"Digital product file: {self.title}",
            metadata={'product_id': self.id, 'is_digital': True}
        )
        
        # Store reference to MediaFile instead of direct file
        self.digital_file_media = media_file
        self.save(update_fields=['digital_file_media'])
        return media_file
    
    def toggle_favorite(self, user):
        """Toggle product favorite using EntityService"""
        from apps.entities.v2.services import EntityService
        
        return EntityService.toggle_action(
            user=user,
            content_object=self,
            action_slug='favorite',
            store=self.store
        )
    
    def get_favorite_count(self):
        """Get total favorites using EntityService"""
        from apps.entities.v2.services import EntityService
        
        return EntityService.get_interaction_count(
            content_object=self,
            action_slug='favorite',
            store=self.store
        )
    
    def user_favorited(self, user):
        """Check if user favorited this product"""
        from apps.entities.v2.services import EntityService
        
        interactions = EntityService.get_user_interactions(
            user=user,
            content_object=self,
            store=self.store
        )
        return interactions.filter(action__slug='favorite').exists()
    
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
        if not self.is_available or self.status != 'active':
            return 'unavailable'
        if not self.track_inventory:
            return 'in_stock'
        if self.inventory_quantity > 0:
            return 'in_stock'
        if self.allow_backorder and self.backorder_quantity > 0:
            return 'available_for_backorder'
        return 'out_of_stock'


class ProductVariant(models.Model):
    """
    Product variant with size, color, etc.
    """

    class Meta:
        app_label = 'ecommerce'
        db_table = 'ecommerce_product_variant'
        unique_together = [['product', 'sku']]
        ordering = ['position']

    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    barcode = models.CharField(max_length=50, blank=True)
    
    # Pricing
    price_override = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    compare_at_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Inventory
    inventory_quantity = models.IntegerField(default=0)
    
    INVENTORY_POLICY_CHOICES = [
        ('deny', 'Deny'),
        ('continue', 'Continue'),
        ('manual', 'Manual')
    ]
    inventory_policy = models.CharField(
        max_length=20,
        choices=INVENTORY_POLICY_CHOICES,
        default='deny'
    )
    
    # Physical attributes
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Variant options
    option1 = models.CharField(max_length=100, blank=True)
    option2 = models.CharField(max_length=100, blank=True)
    option3 = models.CharField(max_length=100, blank=True)
    
    # Position for ordering
    position = models.IntegerField(default=0)
    
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.product.title} - {self.title}"
    
    def get_price(self):
        """Get current price"""
        return self.price_override if self.price_override else self.product.base_price


class ProductCategory(models.Model):
    """
    Hierarchical product categories
    """
    
    class Meta:
        app_label = 'ecommerce'
        db_table = 'ecommerce_product_category'
        unique_together = [['store', 'slug']]
        verbose_name_plural = 'Product Categories'
        indexes = [
            models.Index(fields=['store', 'parent']),
            models.Index(fields=['store', 'position']),
            models.Index(fields=['store', 'is_active']),
        ]
        ordering = ['position']
    
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    
    # Position for ordering
    position = models.PositiveIntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Hierarchical structure
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    
    # Media
    image = models.ForeignKey(
        'mediafile.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_images'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class ProductTag(models.Model):
    """
    Product tags for categorization
    """
    
    class Meta:
        app_label = 'ecommerce'
        db_table = 'ecommerce_product_tag'
        unique_together = [['store', 'slug']]
    
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    
    def __str__(self):
        return self.name


class TaxClass(models.Model):
    """
    Tax class for products
    """
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=4)
    
    class Meta:
        app_label = 'ecommerce'
        db_table = 'ecommerce_tax_class'
        unique_together = [['store', 'name']]
    
    def __str__(self):
        return f"{self.name} ({self.rate}%)"
