"""
Product models for ecommerce app.
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


class ProductCategory(models.Model):
    """
    Product category model for ecommerce.
    """

    store = models.ForeignKey(
        "stores.Store", on_delete=models.CASCADE, related_name="product_categories"
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True)

    # Hierarchy
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    # Display settings
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)

    # SEO
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecommerce_product_category"
        verbose_name_plural = "Product Categories"
        ordering = ["position", "name"]
        indexes = [
            models.Index(fields=["store", "slug"]),
            models.Index(fields=["parent"]),
            models.Index(fields=["is_active"]),
        ]
        unique_together = [["store", "slug"]]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def get_full_path(self):
        """Get full category path"""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return " > ".join(path)


class Product(models.Model):
    """
    Product model for ecommerce.
    """

    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="products")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    # Category
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sku = models.CharField(max_length=100, blank=True)
    barcode = models.CharField(max_length=100, blank=True)
    track_quantity = models.BooleanField(default=True)
    quantity = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[("active", "Active"), ("draft", "Draft"), ("archived", "Archived")],
        default="draft",
    )
    is_featured = models.BooleanField(default=False)
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_products",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecommerce_products"
        indexes = [
            models.Index(fields=["store", "slug"]),
            models.Index(fields=["status"]),
            models.Index(fields=["is_featured"]),
        ]
        ordering = ["-created_at"]
        app_label = "ecommerce"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def is_available(self):
        """Check if product is available for purchase."""
        if not self.track_quantity:
            return self.status == "active"
        return self.status == "active" and self.quantity > 0


class ProductVariant(models.Model):
    """
    Product variant model (sizes, colors, etc.).
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sku = models.CharField(max_length=100, blank=True)
    barcode = models.CharField(max_length=100, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    position = models.PositiveIntegerField(default=0)
    options = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "ecommerce_product_variants"
        ordering = ["position"]
        app_label = "ecommerce"

    def __str__(self):
        return f"{self.product.title} - {self.title}"

    @property
    def effective_price(self):
        """Get the effective price (variant price or product price)."""
        return self.price or self.product.price


class ProductImage(models.Model):
    """
    Product image model.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=255, blank=True)
    position = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = "ecommerce_product_images"
        ordering = ["position"]
        app_label = "ecommerce"

    def __str__(self):
        return f"Image for {self.product.title}"
