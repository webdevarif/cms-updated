"""
Signal handlers for search indexing.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import SearchLog


@receiver(post_save)
def index_content_on_save(sender, instance, created=False, **kwargs):
    """
    Index content when it's saved.
    Triggers search vector updates for searchable models.
    """
    # Only index specific models
    searchable_models = ['Product', 'Post', 'Page']
    
    if sender.__name__ in searchable_models:
        # Update search vector if model has the method
        if hasattr(instance, 'update_search_vector'):
            try:
                instance.update_search_vector()
            except Exception as e:
                # Log error but don't fail the save
                print(f"Error updating search vector for {sender.__name__}: {e}")
        
        # Update search results cache
        try:
            # Clear cached results that might be affected
            from .models import SearchResult
            SearchResult.objects.filter(
                content_type=sender.__name__.lower(),
                object_id=instance.id
            ).delete()
        except Exception as e:
            print(f"Error clearing search cache for {sender.__name__}: {e}")


@receiver(post_delete)
def remove_content_on_delete(sender, instance, **kwargs):
    """
    Remove content from search index when deleted.
    """
    # Only handle specific models
    searchable_models = ['Product', 'Post', 'Page']
    
    if sender.__name__ in searchable_models:
        try:
            # Remove from search results cache
            from .models import SearchResult
            SearchResult.objects.filter(
                content_type=sender.__name__.lower(),
                object_id=instance.id
            ).delete()
        except Exception as e:
            print(f"Error removing from search index for {sender.__name__}: {e}")


@receiver(post_save, sender=SearchLog)
def log_search_analytics(sender, instance, created=False, **kwargs):
    """
    Process search analytics when search is logged.
    """
    if created and instance.success:
        # Could trigger analytics processing here
        # For now, just log that we have a successful search
        pass
