"""
Services for search module.
"""
import time
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
# from elasticsearch import Elasticsearch
# from elasticsearch_dsl import Search, A
import logging

logger = logging.getLogger(__name__)


class SearchService:
    """Core service for search operations"""
    
    @staticmethod
    def search(store, query, search_type='all', filters=None, page=1, page_size=20):
        """
        Perform search query with Elasticsearch
        """
        start_time = time.time()
        
        # TODO: Implement Elasticsearch search
        # For now, return empty results to avoid connection errors
        return {
            'results': [],
            'total': 0,
            'page': page,
            'page_size': page_size,
            'facets': {},
            'suggestions': [],
            'duration_ms': 0
        }
    
    @staticmethod
    def get_facets(store, search_type='all'):
        """
        Get available facets for filtering
        """
        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()
        
        if not index:
            return []
        
        return index.facets
    
    @staticmethod
    def get_suggestions(store, query):
        """
        Get search suggestions
        """
        # TODO: Implement Elasticsearch suggestions
        return []
    
    @staticmethod
    def index_document(store, document_type, document_id, data):
        """
        Index a document in Elasticsearch
        """
        # TODO: Implement Elasticsearch indexing
        return False
    
    @staticmethod
    def rebuild_index(store):
        """
        Rebuild search index for a store
        """
        # TODO: Implement Elasticsearch index rebuilding
        return False
    
    @staticmethod
    def _index_content_type(store, content_type):
        """
        Index all documents of a content type
        """
        # Get model based on content type
        if content_type == 'Page':
            # Note: pages app doesn't exist yet, this is for future implementation
            return []
        elif content_type == 'Post':
            from apps.posts.models import Post
            queryset = Post.objects.filter(store=store, status='published')
        elif content_type == 'Product':
            from apps.public.ecommerce.models import Product
            queryset = Product.objects.filter(store=store, is_active=True)
        else:
            return
        
        # Index each document
        for item in queryset:
            data = {
                'title': item.title,
                'content': getattr(item, 'content', ''),
                'description': getattr(item, 'description', ''),
                'url': getattr(item, 'get_absolute_url', lambda: '')(),
                'created_at': item.created_at.isoformat()
            }
            
            SearchService.index_document(store, content_type, str(item.id), data)
    
    @staticmethod
    def track_search(store, query, search_type, results_count, filters=None, user=None, duration_ms=None):
        """
        Track search query for analytics
        """
        SearchQuery.objects.create(
            store=store,
            query=query,
            search_type=search_type,
            results_count=results_count,
            filters=filters or {},
            user=user,
            duration_ms=duration_ms
        )
    
    @staticmethod
    def index_content(search_index, content_object):
        """
        Legacy method - kept for backward compatibility
        """
        content_type = ContentType.objects.get_for_model(content_object)
        
        # Get title and content
        title = getattr(content_object, 'title', str(content_object))
        content = getattr(content_object, 'description', '') or getattr(content_object, 'content', '') or str(content_object)
        
        # Index in Elasticsearch
        data = {
            'title': title,
            'content': content,
            'description': getattr(content_object, 'description', ''),
            'url': getattr(content_object, 'get_absolute_url', lambda: '')(),
            'created_at': content_object.created_at.isoformat()
        }
        
        SearchService.index_document(search_index.store, content_type.model, str(content_object.id), data)
        
        return True
