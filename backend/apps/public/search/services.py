"""
Services for search module.
"""
import time
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A
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
        
        # Get search index
        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()
        
        if not index:
            return {
                'total': 0,
                'results': [],
                'facets': {},
                'page': page,
                'page_size': page_size,
                'duration_ms': 0
            }
        
        # Build Elasticsearch query
        s = Search(index=index.get_index_name())
        
        # Add query
        if query:
            s = s.query('multi_match', query=query, fields=['title^2', 'content', 'description'])
        
        # Add filters
        if filters:
            for key, value in filters.items():
                if value:
                    s = s.filter('term', **{key: value})
        
        # Add store filter
        s = s.filter('term', store_id=str(store.id))
        
        # Add aggregations for facets
        for facet in index.facets:
            s.aggs.bucket(facet['field'], 'terms', field=facet['field'], size=10)
        
        # Pagination
        start = (page - 1) * page_size
        s = s[start:start + page_size]
        
        # Execute search
        es = Elasticsearch()
        response = s.execute()
        
        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Build results
        results = []
        for hit in response:
            results.append({
                'id': hit.meta.id,
                'title': hit.title,
                'content': hit.content[:200] + '...' if len(hit.content) > 200 else hit.content,
                'url': hit.get('url', ''),
                'type': hit.get('type', ''),
                'score': hit.meta.score
            })
        
        # Build facets
        facets = {}
        for facet in index.facets:
            field = facet['field']
            if hasattr(response.aggs, field):
                bucket = getattr(response.aggs, field)
                facets[field] = [
                    {'key': item.key, 'count': item.doc_count}
                    for item in bucket
                ]
        
        return {
            'total': response.hits.total.value,
            'results': results,
            'facets': facets,
            'page': page,
            'page_size': page_size,
            'duration_ms': duration_ms
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
        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()
        
        if not index:
            return []
        
        # Build suggestion query
        s = Search(index=index.get_index_name())
        s = s.suggest(
            'title_suggest',
            query,
            completion={
                'field': 'title_suggest',
                'size': 10
            }
        )
        
        es = Elasticsearch()
        response = s.execute()
        
        suggestions = []
        if response.suggest.title_suggest:
            for suggestion in response.suggest.title_suggest[0].options:
                suggestions.append({
                    'text': suggestion.text,
                    'score': suggestion.score
                })
        
        return suggestions
    
    @staticmethod
    def index_document(store, document_type, document_id, data):
        """
        Index a document in Elasticsearch
        """
        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()
        
        if not index:
            return False
        
        # Add store ID to document
        data['store_id'] = str(store.id)
        data['type'] = document_type
        
        # Index document
        es = Elasticsearch()
        es.index(
            index=index.get_index_name(),
            id=document_id,
            body=data
        )
        
        logger.info(f"Indexed document {document_id} of type {document_type}")
        return True
    
    @staticmethod
    def rebuild_index(store):
        """
        Rebuild search index for a store
        """
        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()
        
        if not index:
            return False
        
        es = Elasticsearch()
        index_name = index.get_index_name()
        
        # Delete existing index
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
        
        # Create index with mappings
        mappings = {
            'properties': {
                'title': {'type': 'text', 'fields': {'suggest': {'type': 'completion'}}},
                'content': {'type': 'text'},
                'description': {'type': 'text'},
                'url': {'type': 'keyword'},
                'type': {'type': 'keyword'},
                'store_id': {'type': 'keyword'},
                'created_at': {'type': 'date'}
            }
        }
        
        es.indices.create(index=index_name, body={'mappings': mappings})
        
        # Reindex all content
        for content_type in index.content_types:
            SearchService._index_content_type(store, content_type)
        
        # Update last reindexed timestamp
        index.last_reindexed_at = timezone.now()
        index.save(update_fields=['last_reindexed_at'])
        
        logger.info(f"Rebuilt search index for store {store.slug}")
        return True
    
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
