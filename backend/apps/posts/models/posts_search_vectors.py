"""Search vector updates for posts models."""
from django.db.models.signals import post_save
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db.models import F
from django.dispatch import receiver
from .posts import Post


class PostSearchVectorMixin:
    """Mixin to add search functionality to models."""
    
    def update_search_vector(self):
        """Update the search vector for this instance."""
        # Create search vector from title and content
        search_vector = SearchVector('title', 'A', 'B', 'C', 'D')
        
        # Add excerpt if available
        if hasattr(self, 'content'):
            search_vector += SearchVector('content', 'D', 'E')
        
        # Update the search vector field in Post table
        Post.objects.filter(pk=self.pk).update(search_vector=search_vector)
    
    def save(self, *args, **kwargs):
        """Override save to update search vector after saving."""
        super().save(*args, **kwargs)
        self.update_search_vector()


# Add SearchVectorField to Post model
Post.add_to_class('search_vector', SearchVectorField(default=''))


@receiver(post_save, sender=Post)
def post_search_vector_handler(sender, instance, created, **kwargs):
    """
    Signal handler to update search vector when post is saved.
    """
    instance.update_search_vector()
