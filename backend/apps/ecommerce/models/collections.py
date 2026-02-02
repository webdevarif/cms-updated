"""
Product collection models for ecommerce app.
"""

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify

User = get_user_model()


class ProductCollection(models.Model):
    """
    Product collection model (categories/collections).
    """

    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="collections")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="collections/", null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)
    products = models.ManyToManyField(
        "Product", through="CollectionProduct", related_name="collections"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_collections",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecommerce_collections"
        indexes = [
            models.Index(fields=["store", "slug"]),
            models.Index(fields=["is_featured"]),
            models.Index(fields=["position"]),
        ]
        ordering = ["position", "-created_at"]
        app_label = "ecommerce"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class CollectionProduct(models.Model):
    """
    Through model for collection-product many-to-many relationship.
    """

    collection = models.ForeignKey(ProductCollection, on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "ecommerce_collection_products"
        ordering = ["position"]
        app_label = "ecommerce"
        unique_together = ["collection", "product"]
