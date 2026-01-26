"""
Signal handlers for search indexing.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from .models import SearchIndex
# from .services import SearchService
# from .tasks import index_document


@receiver(post_save)
def index_content_on_save(sender, instance, created=False, **kwargs):
    """
    Index content when it's saved
    """
    # TODO: Implement Elasticsearch indexing
    # Only index specific models
    if sender.__name__ not in ['Post', 'Product']:
        return
    
    # Temporarily disabled to avoid Elasticsearch connection errors
    pass
    
    # Get store from instance
    if not hasattr(instance, 'store'):
        return
    
    store = instance.store
    
    # Check if there's an active search index for this content type
    index = SearchIndex.objects.filter(
        store=store,
        is_active=True,
        content_types__contains=[sender.__name__]
    ).first()
    
    if not index:
        return
    
    # Prepare document data
    data = {
        'title': instance.title,
        'content': getattr(instance, 'content', ''),
        'description': getattr(instance, 'description', ''),
        'url': getattr(instance, 'get_absolute_url', lambda: '')(),
        'created_at': instance.created_at.isoformat()
    }
    
    # Index asynchronously
    index_document.delay(
        store_id=store.id,
        document_type=sender.__name__,
        document_id=str(instance.id),
        data=data
    )


@receiver(post_delete)
def remove_content_on_delete(sender, instance, **kwargs):
    """
    Remove content from search index when it's deleted
    """
    # TODO: Implement Elasticsearch deletion
    # Only handle specific models
    if sender.__name__ not in ['Post', 'Product']:
        return
    
    # Temporarily disabled to avoid Elasticsearch connection errors
    pass

    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to remove document from search index")
