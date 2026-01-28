"""
Search vector updates for ecommerce models."""
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

from .products import Product


class ProductSearchVectorMixin:
    """Mixin to add search functionality to models."""

    def update_search_vector(self):
        """Update the search vector for this instance."""
        # Create search vector from title, description, and metafields
        search_vector = SearchVector("title", "A", "B", "C", "D")

        # Add metafields if they exist and are text-based
        if hasattr(self, "tags") and self.tags:
            # Convert JSON array to text for search
            tags_text = " ".join(self.tags) if self.tags else ""
            search_vector += SearchVector("E", tags_text)

        if hasattr(self, "metadata") and self.metadata:
            # Extract text from metadata dict
            metadata_text = " ".join(str(v) for v in self.metadata.values() if isinstance(v, str))
            if metadata_text:
                search_vector += SearchVector("F", metadata_text)

        # Update the search_vector field
        Product.objects.filter(pk=self.pk).update(search_vector=search_vector)

    def save(self, *args, **kwargs):
        """Override save to update search vector after saving."""
        super().save(*args, **kwargs)
        self.update_search_vector()


# Add SearchVectorField to Product model
Product.add_to_class("search_vector", SearchVectorField(default=""))


@receiver(post_save, sender=Product)
def product_search_vector_handler(sender, instance, created, **kwargs):
    """
    Signal handler to update search vector when product is saved.
    """
    instance.update_search_vector()
