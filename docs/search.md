# Search App Rules v1.0

## 🎯 Purpose

This document defines strict development rules for the **search** app in CMS-Updated backend, implementing a centralized, store-scoped search system with Elasticsearch/OpenSearch integration for faceted search across content and commerce.

---

## 🏗️ Search App Structure

### **Fixed Directory Structure**
```
apps/
├── search/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── admin.py
│   ├── services.py
│   ├── tasks.py
│   ├── management/
│   │   └── commands/
│   │       ├── rebuild_index.py
│   │       └── index_content.py
│   ├── migrations/
│   ├── v2/
│   │   ├── __init__.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── tests/
│       ├── __init__.py
│       ├── test_services.py
│       └── test_views.py
```

---

## 📋 Core Models

### **Model Inheritance**
All search models must inherit from `TenantModel` for store scoping:

```python
from core.models import TenantModel
from django.db import models

class SearchIndex(TenantModel):
    # Store-scoped search index model
    pass
```

### **SearchIndex Model**
```python
# apps/search/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import TenantModel

User = get_user_model()

class SearchIndex(TenantModel):
    """
    Store-scoped search index configuration
    """

    # Core fields
    name = models.CharField(max_length=255)
    index_name = models.CharField(max_length=255, unique=True, db_index=True)

    # Index configuration
    content_types = models.JSONField(
        default=list,
        help_text="List of content types to index: ['Page', 'Post', 'Product']"
    )

    # Search configuration
    fields = models.JSONField(
        default=dict,
        help_text="Field mappings and search configuration"
    )

    # Facet configuration
    facets = models.JSONField(
        default=list,
        help_text="Facet configuration for filtering"
    )

    # Status
    is_active = models.BooleanField(default=True)
    last_reindexed_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = 'search_index'
        unique_together = [['store', 'name']]
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.index_name}"

    def get_index_name(self):
        """Get full index name with store prefix"""
        return f"{self.store.slug}_{self.index_name}"
```

### **SearchQuery Model**
```python
class SearchQuery(TenantModel):
    """
    Track search queries for analytics
    """

    # Core fields
    query = models.CharField(max_length=255, db_index=True)

    # Search context
    search_type = models.CharField(
        max_length=50,
        choices=[
            ('content', 'Content'),
            ('product', 'Product'),
            ('all', 'All')
        ]
    )

    # Results
    results_count = models.PositiveIntegerField(default=0)

    # User tracking
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    session_id = models.CharField(max_length=100, blank=True)

    # Filters applied
    filters = models.JSONField(default=dict)

    # Timing
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta(TenantModel.Meta):
        db_table = 'search_query'
        indexes = [
            models.Index(fields=['store', 'query']),
            models.Index(fields=['created_at']),
            models.Index(fields=['search_type']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.query} - {self.results_count} results"
```

---

## 🔌 API Endpoints

### **V2-Only Implementation**
All search endpoints must be V2-only with clean architecture:

#### SearchViewSet
```python
# apps/search/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from elasticsearch_dsl import Q

class SearchViewSet(TenantViewSet):
    """
    Search endpoints for public, customer, and dashboard
    """
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Override to return empty queryset (search uses Elasticsearch)"""
        return SearchIndex.objects.none()

    @extend_schema(
        summary="Search",
        description="Full-text search with faceting",
        responses={200: SearchResultsSerializer}
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Perform search query"""
        query = request.query_params.get('q', '')
        search_type = request.query_params.get('type', 'all')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))

        # Get filters
        filters = {
            k: v for k, v in request.query_params.items()
            if k not in ['q', 'type', 'page', 'page_size']
        }

        # Perform search
        from services.search import SearchService
        results = SearchService.search(
            store=request.store,
            query=query,
            search_type=search_type,
            filters=filters,
            page=page,
            page_size=page_size
        )

        # Track search query
        SearchService.track_search(
            store=request.store,
            query=query,
            search_type=search_type,
            results_count=results['total'],
            filters=filters,
            user=request.user if request.user.is_authenticated else None,
            duration_ms=results.get('duration_ms')
        )

        serializer = SearchResultsSerializer(results)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Get Facets",
        description="Get available facets for filtering",
        responses={200: FacetsSerializer}
    )
    @action(detail=False, methods=['get'])
    def facets(self, request):
        """Get available facets"""
        search_type = request.query_params.get('type', 'all')

        from services.search import SearchService
        facets = SearchService.get_facets(
            store=request.store,
            search_type=search_type
        )

        serializer = FacetsSerializer(facets)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Get Suggestions",
        description="Get search suggestions",
        responses={200: SuggestionsSerializer}
    )
    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """Get search suggestions"""
        query = request.query_params.get('q', '')

        from services.search import SearchService
        suggestions = SearchService.get_suggestions(
            store=request.store,
            query=query
        )

        serializer = SuggestionsSerializer(suggestions)
        return Response(serializer.data, status=status.HTTP_200_OK)
```

---

## 🛠️ Services Layer

### **Business Logic Centralization**
All search business logic must be in services.py:

#### SearchService
```python
# apps/search/services.py
from django.utils import timezone
import logging
import time

logger = logging.getLogger(__name__)

class SearchService:
    """Shared search management service"""

    @staticmethod
    def search(store, query, search_type='all', filters=None, page=1, page_size=20):
        """
        Perform search query with faceting
        """
        from elasticsearch_dsl import Search, A

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
                'page_size': page_size
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
        response = s.execute()

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Build results
        results = []
        for hit in response.hits:
            results.append({
                'id': hit.meta.id,
                'type': hit.get('type'),
                'title': hit.get('title'),
                'description': hit.get('description'),
                'url': hit.get('url'),
                'score': hit.meta.score
            })

        # Build facets
        facets = {}
        for facet in index.facets:
            field = facet['field']
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

    @staticmethod
    def get_facets(store, search_type='all'):
        """Get available facets"""
        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()

        if not index:
            return []

        return index.facets

    @staticmethod
    def get_suggestions(store, query):
        """Get search suggestions"""
        from elasticsearch_dsl import Search

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
        """Index a document"""
        from elasticsearch import Elasticsearch

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

        logger.info(f"Indexed {document_type} #{document_id}")
        return True

    @staticmethod
    def delete_document(store, document_id):
        """Delete a document from index"""
        from elasticsearch import Elasticsearch

        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()

        if not index:
            return False

        # Delete document
        es = Elasticsearch()
        es.delete(
            index=index.get_index_name(),
            id=document_id
        )

        logger.info(f"Deleted document #{document_id}")
        return True

    @staticmethod
    def rebuild_index(store):
        """Rebuild entire search index"""
        from elasticsearch import Elasticsearch

        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()

        if not index:
            return False

        # Delete and recreate index
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
        """Index all documents of a content type"""
        # Get model based on content type
        if content_type == 'Page':
            from apps.pages.models import Page
            queryset = Page.objects.filter(store=store, status='published')
        elif content_type == 'Post':
            from apps.posts.models import Post
            queryset = Post.objects.filter(store=store, status='published')
        elif content_type == 'Product':
            from apps.ecommerce.models import Product
            queryset = Product.objects.filter(store=store, is_active=True)
        else:
            return

        # Index each document
        for item in queryset:
            data = {
                'title': item.title,
                'content': getattr(item, 'content', ''),
                'description': getattr(item, 'description', ''),
                'url': item.get_absolute_url(),
                'created_at': item.created_at.isoformat()
            }

            SearchService.index_document(
                store=store,
                document_type=content_type,
                document_id=str(item.id),
                data=data
            )

    @staticmethod
    def track_search(store, query, search_type, results_count, filters=None, user=None, duration_ms=None):
        """Track search query for analytics"""
        SearchQuery.objects.create(
            store=store,
            query=query,
            search_type=search_type,
            results_count=results_count,
            filters=filters or {},
            user=user,
            duration_ms=duration_ms
        )
```

---

## 🔄 Celery Tasks

### **Async Indexing**
```python
# apps/search/tasks.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def index_document(self, store_id, document_type, document_id, data):
    """
    Async document indexing
    """
    from .models import SearchIndex
    from .services import SearchService

    try:
        store = Store.objects.get(id=store_id)
        result = SearchService.index_document(
            store=store,
            document_type=document_type,
            document_id=document_id,
            data=data
        )

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

@shared_task
def rebuild_index(store_id):
    """
    Async index rebuild
    """
    from .models import SearchIndex
    from .services import SearchService

    try:
        store = Store.objects.get(id=store_id)
        result = SearchService.rebuild_index(store)

        return {
            'store_id': store_id,
            'rebuilt': result
        }

    except Store.DoesNotExist:
        logger.error(f"Store #{store_id} not found")
        return {'store_id': store_id, 'rebuilt': False}
```

---

## 🔒 Security Rules

### **Search Security**
- **Store Isolation**: All searches must be store-scoped
- **Query Validation**: Validate all search queries
- **Rate Limiting**: Implement rate limiting on search endpoints
- **Result Filtering**: Filter results based on permissions
- **No Sensitive Data**: Never index sensitive information
- **Access Control**: Respect user permissions in results
- **SQL Injection Prevention**: Use parameterized queries
- **XSS Protection**: Sanitize search results

---

## 📊 Performance Rules

### **Search Optimization**
- **Async Indexing**: All indexing must be asynchronous
- **Batch Operations**: Use bulk operations for indexing
- **Query Optimization**: Use efficient Elasticsearch queries
- **Caching**: Cache search results where appropriate
- **Index Optimization**: Optimize Elasticsearch indexes

### **Database Optimization**
- **Indexes**: Add indexes on frequently queried fields
- **Query Optimization**: Use `select_related` for lookups
- **Bulk Operations**: Use bulk operations for indexing
- **Partitioning**: Consider partitioning large search tables

---

## 🧪 Testing Rules

### **Required Coverage**
- **Services**: 100% code coverage
- **Views**: 90% code coverage
- **Integration**: Critical path testing

### **Test Examples**
```python
# apps/search/tests/test_services.py
from django.test import TestCase
from ..services import SearchService

class SearchServiceTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', slug='test-store')
        self.index = SearchIndex.objects.create(
            store=self.store,
            name='Test Index',
            index_name='test_index',
            content_types=['Page'],
            fields={'title': 'text', 'content': 'text'},
            facets=[{'field': 'type', 'label': 'Type'}]
        )

    def test_search(self):
        """Test search functionality"""
        results = SearchService.search(
            store=self.store,
            query='test',
            search_type='content'
        )

        self.assertIn('results', results)
        self.assertIn('facets', results)

    def test_index_document(self):
        """Test document indexing"""
        data = {
            'title': 'Test Page',
            'content': 'Test content',
            'url': '/test-page'
        }

        result = SearchService.index_document(
            store=self.store,
            document_type='Page',
            document_id='1',
            data=data
        )

        self.assertTrue(result)
```

---

## 🔗 Integration Rules

### **Required Integrations**
- **stores.md**: Store scoping
- **logs.md**: Activity logging
- **core.md**: TenantModel and TenantViewSet

### **Integration Examples**
```python
# Integration with pages.md for page indexing
from signals import page_published

@receiver(page_published)
def index_page(sender, instance, **kwargs):
    """Index published page"""
    data = {
        'title': instance.title,
        'content': instance.content,
        'description': instance.description,
        'url': instance.get_absolute_url(),
        'created_at': instance.created_at.isoformat()
    }

    from services.search import SearchService
    SearchService.index_document(
        store=instance.store,
        document_type='Page',
        document_id=str(instance.id),
        data=data
    )

# Integration with ecommerce.md for product indexing
from signals import product_updated

@receiver(product_updated)
def index_product(sender, instance, **kwargs):
    """Index product"""
    data = {
        'title': instance.title,
        'content': instance.description,
        'description': instance.short_description,
        'url': instance.get_absolute_url(),
        'created_at': instance.created_at.isoformat()
    }

    from services.search import SearchService
    SearchService.index_document(
        store=instance.store,
        document_type='Product',
        document_id=str(instance.id),
        data=data
    )
```

---

## 📈 Search Configuration

### **Index Mappings**
```python
# Example Elasticsearch index mappings
MAPPINGS = {
    'properties': {
        'title': {
            'type': 'text',
            'fields': {
                'suggest': {'type': 'completion'}
            }
        },
        'content': {'type': 'text'},
        'description': {'type': 'text'},
        'url': {'type': 'keyword'},
        'type': {'type': 'keyword'},
        'store_id': {'type': 'keyword'},
        'created_at': {'type': 'date'}
    }
}
```

### **Facet Configuration**
```python
# Example facet configuration
FACETS = [
    {
        'field': 'type',
        'label': 'Type',
        'type': 'terms'
    },
    {
        'field': 'category_id',
        'label': 'Category',
        'type': 'terms'
    },
    {
        'field': 'price',
        'label': 'Price Range',
        'type': 'range',
        'ranges': [
            {'to': 50, 'label': 'Under $50'},
            {'from': 50, 'to': 100, 'label': '$50 - $100'},
            {'from': 100, 'label': '$100+'}
        ]
    }
]
```

---

## 🚀 Deployment Notes

### **Required Dependencies**
```python
# requirements.txt
elasticsearch>=8.0.0
elasticsearch-dsl>=8.0.0
celery>=5.3.0
```

### **Elasticsearch Configuration**
```python
# settings.py
ELASTICSEARCH_HOSTS = ['http://localhost:9200']
ELASTICSEARCH_TIMEOUT = 30
```

### **Monitoring**
- Monitor search query performance
- Track search query analytics
- Alert on high query times
- Monitor index sizes

---

## 📚 Best Practices

1. **Always use async indexing** - Never block on indexing
2. **Validate all queries** - Prevent injection attacks
3. **Respect store isolation** - Never cross store boundaries
4. **Log search queries** - Maintain analytics
5. **Rate limit endpoints** - Prevent abuse
6. **Optimize indexes** - Regular index optimization
7. **Monitor performance** - Track query times
8. **Use suggestions** - Improve user experience
9. **Implement faceting** - Enable advanced filtering
10. **Test search queries** - Ensure relevance

---

## 🔧 Management Commands

### **Rebuild Index**
```bash
python manage.py rebuild_index --store=test-store
```

### **Index Content**
```bash
python manage.py index_content --type=Page
```

---

## 📝 API Documentation

### **Base URL**
```
/v2/api/search/
```

### **Endpoints**

#### Search
- `GET /v2/api/search/search/` - Perform search
- `GET /v2/api/search/facets/` - Get available facets
- `GET /v2/api/search/suggestions/` - Get search suggestions

### **Query Parameters**

#### Search
- `q` - Search query
- `type` - Search type (content, product, all)
- `page` - Page number (default: 1)
- `page_size` - Results per page (default: 20)
- `*` - Additional filters

#### Facets
- `type` - Facet type (content, product, all)

#### Suggestions
- `q` - Search query for suggestions

---

## 🎯 Implementation Checklist

- [ ] Create SearchIndex, SearchQuery models
- [ ] Implement SearchService
- [ ] Create API endpoints (SearchViewSet)
- [ ] Implement Elasticsearch integration
- [ ] Add faceting support
- [ ] Implement search suggestions
- [ ] Create Celery tasks for async indexing
- [ ] Add admin interface
- [ ] Create tests (services, views)
- [ ] Add monitoring and logging
- [ ] Implement index management
- [ ] Create management commands
- [ ] Add integration examples
- [ ] Document search configuration

---

## 📖 Version History

- **v1.0** - Initial version with Elasticsearch integration
