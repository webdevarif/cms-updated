"""
Infrastructure SearchService according to search rules.
Real Elasticsearch/OpenSearch integration.
"""
from django.utils import timezone
from django.conf import settings
import logging
from elasticsearch_dsl import Search, A, Document, Index
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, RequestError

logger = logging.getLogger(__name__)


class SearchService:
    """Infrastructure search management service"""
    
    _client = None
    
    @classmethod
    def get_client(cls):
        """Get Elasticsearch client (lazy initialization)"""
        if cls._client is None:
            try:
                cls._client = Elasticsearch(**settings.ELASTICSEARCH_SETTINGS)
                # Test connection
                cls._client.ping()
                logger.info("Elasticsearch client connected successfully")
            except (ConnectionError, RequestError) as e:
                logger.error(f"Elasticsearch connection failed: {e}")
                cls._client = None
        return cls._client
    
    @classmethod
    def get_index_name(cls, store, content_type=None):
        """Get store-scoped index name"""
        prefix = settings.ELASTICSEARCH_INDEX_PREFIX
        store_id = str(store.id)
        
        if content_type:
            return f"{prefix}_{store_id}_{content_type.lower()}"
        else:
            return f"{prefix}_{store_id}_search"
    
    @staticmethod
    def search(store, query, search_type='all', filters=None, page=1, page_size=20):
        """
        INFRASTRUCTURE PROVIDES: Search query execution with faceting
        APPLICATION MUST: Provide valid store context and search parameters
        """
        start_time = timezone.now()
        
        # Get search index - INFRASTRUCTURE PROVIDES
        from .models.infrastructure import SearchIndex
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
        
        client = SearchService.get_client()
        if not client:
            # Fallback to empty results if ES is down
            logger.warning("Elasticsearch unavailable, returning empty results")
            return {
                'total': 0,
                'results': [],
                'facets': {},
                'page': page,
                'page_size': page_size,
                'duration_ms': 0
            }
        
        try:
            # Build Elasticsearch query - INFRASTRUCTURE PROVIDES
            index_name = SearchService.get_index_name(store)
            s = Search(index=index_name)
            
            # Add query - INFRASTRUCTURE PROVIDES
            if query:
                s = s.query(
                    'multi_match',
                    query=query,
                    fields=['title^3', 'content^2', 'description^1', 'tags^1'],
                    type='best_fields',
                    fuzziness='AUTO'
                )
            
            # Add filters - INFRASTRUCTURE PROVIDES
            if filters:
                for key, value in filters.items():
                    if value:
                        s = s.filter('term', **{key: value})
            
            # Add store filter - INFRASTRUCTURE PROVIDES
            s = s.filter('term', store_id=str(store.id))
            
            # Add content type filter if specified
            if search_type != 'all':
                s = s.filter('term', type=search_type)
            
            # Add aggregations for facets - INFRASTRUCTURE PROVIDES
            for facet in index.facets:
                field = facet.get('field', 'type')
                s.aggs.bucket(facet['field'], 'terms', field=field, size=10)
            
            # Add highlighting
            s = s.highlight('title', 'content', 'description', fragment_size=150, number_of_fragments=3)
            
            # Pagination - INFRASTRUCTURE PROVIDES
            start = (page - 1) * page_size
            s = s[start:start + page_size]
            
            # Execute search - INFRASTRUCTURE PROVIDES
            response = s.execute()
            
            # Calculate duration - INFRASTRUCTURE PROVIDES
            duration_ms = int((timezone.now() - start_time).total_seconds() * 1000)
            
            # Build results - INFRASTRUCTURE PROVIDES
            results = []
            for hit in response.hits:
                result_data = {
                    'id': hit.meta.id,
                    'type': hit.get('type'),
                    'title': hit.get('title'),
                    'description': hit.get('description'),
                    'url': hit.get('url'),
                    'score': hit.meta.score
                }
                
                # Add highlighted snippets
                if hasattr(hit.meta, 'highlight'):
                    highlights = {}
                    for field in hit.meta.highlight:
                        highlights[field] = hit.meta.highlight[field]
                    result_data['highlight'] = highlights
                
                results.append(result_data)
            
            # Build facets - INFRASTRUCTURE PROVIDES
            facets = {}
            for facet in index.facets:
                field = facet.get('field', 'type')
                if field in response.aggregations:
                    buckets = response.aggregations[field].buckets
                    facets[field] = [
                        {'value': bucket.key, 'count': bucket.doc_count}
                        for bucket in buckets
                    ]
            
            return {
                'total': response.hits.total.value,
                'results': results,
                'facets': facets,
                'page': page,
                'page_size': page_size,
                'duration_ms': duration_ms
            }
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {
                'total': 0,
                'results': [],
                'facets': {},
                'page': page,
                'page_size': page_size,
                'duration_ms': 0
            }
    
    @staticmethod
    def get_facets(store, search_type='all'):
        """
        INFRASTRUCTURE PROVIDES: Available facets retrieval
        """
        from .models.infrastructure import SearchIndex
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
        INFRASTRUCTURE PROVIDES: Search suggestions
        """
        from .models.infrastructure import SearchIndex
        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()
        
        if not index:
            return []
        
        client = SearchService.get_client()
        if not client:
            return []
        
        try:
            # Build suggestion query - INFRASTRUCTURE PROVIDES
            index_name = SearchService.get_index_name(store)
            s = Search(index=index_name)
            
            # Use completion suggester for title suggestions
            s = s.suggest(
                'title_suggest',
                query,
                completion={
                    'field': 'title_suggest',
                    'size': 10,
                    'skip_duplicates': True
                }
            )
            
            # Fallback to prefix match if no completion field
            s = s.suggest(
                'prefix_suggest',
                query,
                prefix={
                    'field': 'title',
                    'size': 10
                }
            )
            
            response = s.execute()
            
            suggestions = []
            
            # Try completion suggestions first
            if response.suggest.title_suggest:
                for suggestion in response.suggest.title_suggest:
                    for option in suggestion.options:
                        suggestions.append({
                            'text': option.text,
                            'score': option.score
                        })
            
            # Fallback to prefix suggestions
            if not suggestions and response.suggest.prefix_suggest:
                for suggestion in response.suggest.prefix_suggest:
                    for option in suggestion.options:
                        suggestions.append({
                            'text': option.text,
                            'score': option.score
                        })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Suggestions error: {e}")
            return []
    
    @staticmethod
    def index_document(store, document_type, document_id, data):
        """
        INFRASTRUCTURE PROVIDES: Document indexing
        APPLICATION MUST: Provide valid document data and types
        """
        from .models.infrastructure import SearchIndex
        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()
        
        if not index:
            return False
        
        client = SearchService.get_client()
        if not client:
            return False
        
        try:
            # Add store ID to document - INFRASTRUCTURE PROVIDES
            data['store_id'] = str(store.id)
            data['type'] = document_type
            data['indexed_at'] = timezone.now().isoformat()
            
            # Get index name
            index_name = SearchService.get_index_name(store, document_type)
            
            # Ensure index exists with proper mapping
            SearchService._ensure_index_exists(index_name, document_type)
            
            # Index document - INFRASTRUCTURE PROVIDES
            client.index(
                index=index_name,
                id=document_id,
                body=data,
                refresh=False  # Don't refresh for performance
            )
            
            logger.info(f"Indexed {document_type} #{document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Indexing error: {e}")
            return False
    
    @staticmethod
    def delete_document(store, document_id):
        """
        INFRASTRUCTURE PROVIDES: Document deletion
        APPLICATION MUST: Provide valid document ID
        """
        from .models.infrastructure import SearchIndex
        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()
        
        if not index:
            return False
        
        client = SearchService.get_client()
        if not client:
            return False
        
        try:
            # Try to delete from all possible content type indices
            content_types = index.content_types or ['Product', 'Post', 'Page']
            
            for content_type in content_types:
                index_name = SearchService.get_index_name(store, content_type)
                
                try:
                    # Delete document - INFRASTRUCTURE PROVIDES
                    client.delete(
                        index=index_name,
                        id=document_id,
                        ignore=[404]  # Ignore if document doesn't exist
                    )
                except Exception:
                    continue  # Try next index
            
            logger.info(f"Deleted document #{document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Deletion error: {e}")
            return False
    
    @staticmethod
    def rebuild_index(store):
        """
        INFRASTRUCTURE PROVIDES: Complete index rebuild
        APPLICATION MUST: Trigger rebuild appropriately
        """
        from .models.infrastructure import SearchIndex
        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()
        
        if not index:
            return False
        
        client = SearchService.get_client()
        if not client:
            return False
        
        try:
            # Delete and recreate indices - INFRASTRUCTURE PROVIDES
            content_types = index.content_types or ['Product', 'Post', 'Page']
            
            for content_type in content_types:
                index_name = SearchService.get_index_name(store, content_type)
                
                # Delete existing index
                if client.indices.exists(index=index_name):
                    client.indices.delete(index=index_name)
                
                # Create index with mappings - INFRASTRUCTURE PROVIDES
                SearchService._create_index_with_mappings(index_name, content_type)
            
            # Reindex all content - INFRASTRUCTURE PROVIDES
            for content_type in content_types:
                SearchService._index_content_type(store, content_type)
            
            # Update last reindexed timestamp - INFRASTRUCTURE PROVIDES
            index.last_reindexed_at = timezone.now()
            index.save(update_fields=['last_reindexed_at'])
            
            logger.info(f"Rebuilt search index for store {store.slug}")
            return True
            
        except Exception as e:
            logger.error(f"Rebuild error: {e}")
            return False
    
    @staticmethod
    def _ensure_index_exists(index_name, content_type):
        """Ensure index exists with proper mappings"""
        client = SearchService.get_client()
        if not client:
            return False
        
        if not client.indices.exists(index=index_name):
            SearchService._create_index_with_mappings(index_name, content_type)
    
    @staticmethod
    def _create_index_with_mappings(index_name, content_type):
        """Create index with proper mappings"""
        client = SearchService.get_client()
        if not client:
            return False
        
        # Define mappings based on content type
        mappings = {
            'properties': {
                'title': {
                    'type': 'text',
                    'fields': {
                        'suggest': {'type': 'completion'},
                        'keyword': {'type': 'keyword'}
                    }
                },
                'content': {'type': 'text'},
                'description': {'type': 'text'},
                'url': {'type': 'keyword'},
                'type': {'type': 'keyword'},
                'store_id': {'type': 'keyword'},
                'created_at': {'type': 'date'},
                'indexed_at': {'type': 'date'},
                'tags': {'type': 'keyword'},
                'status': {'type': 'keyword'},
                'price': {'type': 'float'},
                'sku': {'type': 'keyword'}
            }
        }
        
        # Add content type specific mappings
        if content_type == 'Product':
            mappings['properties']['price'] = {'type': 'float'}
            mappings['properties']['sku'] = {'type': 'keyword'}
            mappings['properties']['status'] = {'type': 'keyword'}
        elif content_type == 'Post':
            mappings['properties']['excerpt'] = {'type': 'text'}
            mappings['properties']['published'] = {'type': 'boolean'}
        elif content_type == 'Page':
            mappings['properties']['meta_description'] = {'type': 'text'}
        
        client.indices.create(index=index_name, body={'mappings': mappings})
    
    @staticmethod
    def _index_content_type(store, content_type):
        """Index all content of a specific type"""
        # Import appropriate model
        if content_type == 'Product':
            from apps.ecommerce.models import Product
            queryset = Product.objects.filter(store=store)
        elif content_type == 'Post':
            from apps.posts.models import Post
            queryset = Post.objects.filter(store=store)
        elif content_type == 'Page':
            from apps.posts.models import Post
            queryset = Post.objects.filter(store=store, post_type__slug='page')
        elif content_type == 'Comment':
            from apps.posts.models import Comment
            queryset = Comment.objects.filter(store=store, is_approved=True, is_deleted=False)
        elif content_type == 'Review':
            from apps.ecommerce.models import Review
            queryset = Review.objects.filter(product__store=store, is_approved=True)
        else:
            return
        
        # Bulk index documents
        from elasticsearch.helpers import bulk
        
        actions = []
        for obj in queryset:
            data = SearchService._prepare_document_data(obj, content_type)
            action = {
                '_index': SearchService.get_index_name(store, content_type),
                '_id': str(obj.id),
                '_source': data
            }
            actions.append(action)
        
        if actions:
            client = SearchService.get_client()
            if client:
                bulk(client, actions)
                logger.info(f"Bulk indexed {len(actions)} {content_type} documents")
    
    @staticmethod
    def _prepare_document_data(obj, content_type):
        """Prepare document data for indexing"""
        data = {
            'title': getattr(obj, 'title', ''),
            'url': f'/{content_type.lower()}s/{obj.slug}/',
            'type': content_type,
            'created_at': obj.created_at.isoformat()
        }
        
        # Add content based on type
        if content_type == 'Product':
            data.update({
                'content': getattr(obj, 'description', ''),
                'description': getattr(obj, 'seo_description', '') or getattr(obj, 'description', ''),
                'price': float(obj.price),
                'sku': getattr(obj, 'sku', ''),
                'status': obj.status,
                'tags': getattr(obj, 'tags', [])
            })
        elif content_type == 'Post':
            data.update({
                'content': getattr(obj, 'content', ''),
                'description': getattr(obj, 'excerpt', ''),
                'published': getattr(obj, 'status', 'published') == 'published'
            })
        elif content_type == 'Page':
            data.update({
                'content': getattr(obj, 'content', ''),
                'description': getattr(obj, 'meta_description', '')
            })
        elif content_type == 'Comment':
            data.update({
                'content': getattr(obj, 'content', ''),
                'description': f'Comment by {obj.user.get_display_name()} on "{obj.post.title}"',
                'author_display_name': obj.user.get_display_name(),
                'post_title': obj.post.title,
                'post_url': f'/posts/{obj.post.slug}/',
                'comment_id': obj.id,
                'post_id': obj.post.id
            })
        elif content_type == 'Review':
            data.update({
                'content': getattr(obj, 'content', ''),
                'title': getattr(obj, 'title', ''),
                'description': f'Review by {obj.user.get_display_name()} on "{obj.product.title}"',
                'rating': obj.rating,
                'author_display_name': obj.user.get_display_name(),
                'product_title': obj.product.title,
                'product_url': f'/products/{obj.product.slug}/',
                'review_id': obj.id,
                'product_id': obj.product.id,
                'verified_purchase': obj.verified_purchase
            })
        
        return data
    
    @staticmethod
    def track_search(store, query, search_type, results_count, filters=None, user=None, duration_ms=None):
        """
        INFRASTRUCTURE PROVIDES: Search query tracking
        APPLICATION MUST: Call this method for analytics
        """
        from .models.infrastructure import SearchQuery
        SearchQuery.objects.create(
            store=store,
            query=query,
            search_type=search_type,
            results_count=results_count,
            filters=filters or {},
            user=user,
            duration_ms=duration_ms
        )
