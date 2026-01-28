"""Search vector updates for pages models."""
from apps.posts.models import Post
from django.contrib.postgres.search import SearchField, SearchVector
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver


class PageSearchVectorMixin:
    """Mixin to add search functionality to models."""

    def update_search_vector(self):
        """Update the search vector for this instance."""
        # Create search vector from title and content
        search_vector = SearchVector("title", "A", "B", "C", "D")

        # Add content if available
        if hasattr(self, "content"):
            search_vector += SearchVector("content", "D", "E")

        # Add meta_description if available
        if hasattr(self, "meta_description"):
            search_vector += SearchVector("meta_description", "F")

        # Update the search vector field in Page table
        Page.objects.filter(pk=self.pk).update(search_vector=search_vector)

    def save(self, *args, **kwargs):
        """Override save to update search vector after saving."""
        super().save(*args, **kwargs)
        self.update_search_vector()


# Add SearchVectorField to Page model
Page.add_to_class("search_vector", SearchVector(default=""))


@receiver(post_save, sender=Post)
def page_search_vector_handler(sender, instance, created, **kwargs):
    """
    Signal handler to update search vector when page is saved.
    """
    instance.update_search_vector()
