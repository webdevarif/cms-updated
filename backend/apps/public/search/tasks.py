"""
Tasks for search module.
"""
from celery import shared_task
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


@shared_task(bind=True, max_retries=3)
def index_document(self, store_id, document_type, document_id, data):
    """
    Async document indexing task
    """
    try:
        from .models import SearchIndex
        from .services import SearchService
        from apps.stores.models import Store
        
        store = Store.objects.get(id=store_id)
        result = SearchService.index_document(store, document_type, document_id, data)
        
        return {
            'document_id': document_id,
            'indexed': result
        }
        
    except Store.DoesNotExist:
        logger.error(f"Store #{store_id} not found")
        raise
        
    except Exception as exc:
        logger.error(f"Document indexing failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def rebuild_index(self, store_id):
    """
    Async index rebuild task
    """
    try:
        from .models import SearchIndex
        from .services import SearchService
        from apps.stores.models import Store
        
        store = Store.objects.get(id=store_id)
        result = SearchService.rebuild_index(store)
        
        return {
            'store_id': store_id,
            'rebuilt': result
        }
        
    except Store.DoesNotExist:
        logger.error(f"Store #{store_id} not found")
        return {'store_id': store_id, 'rebuilt': False}
        
    except Exception as exc:
        logger.error(f"Index rebuild failed: {exc}")
        raise self.retry(exc=exc, countdown=60)
