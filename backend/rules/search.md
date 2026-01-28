# Search Infrastructure Rules v1.0

## Authority
- Owner: Infrastructure Lead
- Enforced By: SearchService, SearchIndex model, management commands
- Scope: Shared Infrastructure
- Authority Level: INFRASTRUCTURE STANDARD

## 🎯 Purpose
This document defines SHARED INFRASTRUCTURE rules for the **search** system in CMS-Updated backend, providing a unified search infrastructure with Elasticsearch/OpenSearch integration for faceted search across content and commerce.

---

## 🏗️ Structure
### **Infrastructure Directory Structure**
```
apps/
├── search/
│   ├── __init__.py
│   ├── services.py          # Infrastructure service layer
│   ├── tasks.py             # Async indexing tasks
│   ├── management/
│   │   └── commands/
│   │       ├── rebuild_index.py
│   │       └── index_content.py
│   └── tests/
│       ├── __init__.py
│       ├── test_services.py
│       └── test_views.py
```

---

## 📦 Data Model
### **Infrastructure SearchIndex Model**
```python
# apps/search/models.py
from django.db import models
from core.models import TenantModel

class SearchIndex(TenantModel):
    """
    INFRASTRUCTURE: Store-scoped search index configuration
    """

    # Core fields - INFRASTRUCTURE PROVIDES
    name = models.CharField(max_length=255)
    index_name = models.CharField(max_length=255, unique=True, db_index=True)

    # Index configuration - INFRASTRUCTURE PROVIDES
    content_types = models.JSONField(
        default=list,
        help_text="List of content types to index: ['Page', 'Post', 'Product']"
    )

    # Search configuration - INFRASTRUCTURE PROVIDES
    fields = models.JSONField(
        default=dict,
        help_text="Field mappings and search configuration"
    )

    # Facet configuration - INFRASTRUCTURE PROVIDES
    facets = models.JSONField(
        default=list,
        help_text="Facet configuration for filtering"
    )

    # Status - INFRASTRUCTURE PROVIDES
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
        """INFRASTRUCTURE PROVIDES: Full index name with store prefix"""
        return f"{self.store.slug}_{self.index_name}"
```

### **Infrastructure SearchQuery Model**
```python
class SearchQuery(TenantModel):
    """
    INFRASTRUCTURE: Track search queries for analytics
    """

    # Core fields - INFRASTRUCTURE PROVIDES
    query = models.CharField(max_length=255, db_index=True)

    # Search context - INFRASTRUCTURE PROVIDES
    search_type = models.CharField(
        max_length=50,
        choices=[
            ('content', 'Content'),
            ('product', 'Product'),
            ('all', 'All')
        ]
    )

    # Results - INFRASTRUCTURE PROVIDES
    results_count = models.PositiveIntegerField(default=0)

    # User tracking - INFRASTRUCTURE PROVIDES
    user = models.ForeignKey(
        'accounts.UserAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    session_id = models.CharField(max_length=100, blank=True)

    # Filters applied - INFRASTRUCTURE PROVIDES
    filters = models.JSONField(default=dict)

    # Timing - INFRASTRUCTURE PROVIDES
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

## ⚙️ Services
### **Infrastructure SearchService**
```python
# apps/search/services.py
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class SearchService:
    """Infrastructure search management service"""

    @staticmethod
    def search(store, query, search_type='all', filters=None, page=1, page_size=20):
        """
        INFRASTRUCTURE PROVIDES: Search query execution with faceting
        APPLICATION MUST: Provide valid store context and search parameters
        """
        from elasticsearch_dsl import Search, A
        import time

        start_time = time.time()

        # Get search index - INFRASTRUCTURE PROVIDES
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

        # Build Elasticsearch query - INFRASTRUCTURE PROVIDES
        s = Search(index=index.get_index_name())

        # Add query - INFRASTRUCTURE PROVIDES
        if query:
            s = s.query('multi_match', query=query, fields=['title^2', 'content', 'description'])

        # Add filters - INFRASTRUCTURE PROVIDES
        if filters:
            for key, value in filters.items():
                if value:
                    s = s.filter('term', **{key: value})

        # Add store filter - INFRASTRUCTURE PROVIDES
        s = s.filter('term', store_id=str(store.id))

        # Add aggregations for facets - INFRASTRUCTURE PROVIDES
        for facet in index.facets:
            s.aggs.bucket(facet['field'], 'terms', field=facet['field'], size=10)

        # Pagination - INFRASTRUCTURE PROVIDES
        start = (page - 1) * page_size
        s = s[start:start + page_size]

        # Execute search - INFRASTRUCTURE PROVIDES
        response = s.execute()

        # Calculate duration - INFRASTRUCTURE PROVIDES
        duration_ms = int((time.time() - start_time) * 1000)

        # Build results - INFRASTRUCTURE PROVIDES
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

        # Build facets - INFRASTRUCTURE PROVIDES
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
        """
        INFRASTRUCTURE PROVIDES: Available facets retrieval
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
        INFRASTRUCTURE PROVIDES: Search suggestions
        """
        from elasticsearch_dsl import Search

        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()

        if not index:
            return []

        # Build suggestion query - INFRASTRUCTURE PROVIDES
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
        """
        INFRASTRUCTURE PROVIDES: Document indexing
        APPLICATION MUST: Provide valid document data and types
        """
        from elasticsearch import Elasticsearch

        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()

        if not index:
            return False

        # Add store ID to document - INFRASTRUCTURE PROVIDES
        data['store_id'] = str(store.id)
        data['type'] = document_type

        # Index document - INFRASTRUCTURE PROVIDES
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
        """
        INFRASTRUCTURE PROVIDES: Document deletion
        APPLICATION MUST: Provide valid document ID
        """
        from elasticsearch import Elasticsearch

        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()

        if not index:
            return False

        # Delete document - INFRASTRUCTURE PROVIDES
        es = Elasticsearch()
        es.delete(
            index=index.get_index_name(),
            id=document_id
        )

        logger.info(f"Deleted document #{document_id}")
        return True

    @staticmethod
    def rebuild_index(store):
        """
        INFRASTRUCTURE PROVIDES: Complete index rebuild
        APPLICATION MUST: Trigger rebuild appropriately
        """
        from elasticsearch import Elasticsearch

        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()

        if not index:
            return False

        # Delete and recreate index - INFRASTRUCTURE PROVIDES
        es = Elasticsearch()
        index_name = index.get_index_name()

        # Delete existing index
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)

        # Create index with mappings - INFRASTRUCTURE PROVIDES
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

        # Reindex all content - INFRASTRUCTURE PROVIDES
        for content_type in index.content_types:
            SearchService._index_content_type(store, content_type)

        # Update last reindexed timestamp - INFRASTRUCTURE PROVIDES
        index.last_reindexed_at = timezone.now()
        index.save(update_fields=['last_reindexed_at'])

        logger.info(f"Rebuilt search index for store {store.slug}")
        return True

    @staticmethod
    def track_search(store, query, search_type, results_count, filters=None, user=None, duration_ms=None):
        """
        INFRASTRUCTURE PROVIDES: Search query tracking
        APPLICATION MUST: Call this method for analytics
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
```

---

## 🔐 Security
### **Infrastructure Security Requirements**
- INFRASTRUCTURE MUST validate all search queries and parameters
- INFRASTRUCTURE MUST enforce store isolation in all operations
- INFRASTRUCTURE MUST sanitize Elasticsearch queries
- INFRASTRUCTURE MUST prevent injection attacks
- INFRASTRUCTURE MUST validate document indexing permissions

### **Application Security Responsibilities**
- APPLICATION MUST validate user permissions before search operations
- APPLICATION MUST ensure sensitive data is not indexed
- APPLICATION MUST implement proper access controls
- APPLICATION MUST sanitize search inputs
- APPLICATION MUST respect user privacy in search results

---

## 🧪 Testing
### **Infrastructure Testing Requirements**
- **Services**: 100% code coverage
- **Integration**: Critical path testing
- **Performance**: Search response time validation
- **Elasticsearch**: Index creation and deletion testing

### **Infrastructure Test Examples**
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
            'description': 'Test description',
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

## 🚫 Forbidden Patterns
### **Infrastructure Forbidden Patterns**
- MUST NOT execute queries without store context
- MUST NOT index documents without proper validation
- MUST NOT expose internal Elasticsearch operations
- MUST NOT allow arbitrary query execution
- MUST NOT bypass security validations

### **Application Forbidden Patterns**
- MUST NOT index sensitive user data
- MUST NOT perform direct Elasticsearch operations
- MUST NOT bypass SearchService for search operations
- MUST NOT implement custom search logic
- MUST NOT ignore search result filtering

---

## 🔗 Cross-Module Dependencies
### **Infrastructure Interface Requirements**
- ALL modules MUST import from apps.search.services
- ALL modules MUST use SearchService for search operations
- ALL modules MUST use SearchIndex for configuration
- ALL modules MUST follow document indexing patterns
- ALL modules MUST respect search result formatting

### **Application Integration Examples**
```python
# APPLICATION RESPONSIBILITY: Use infrastructure service
from apps.search.services import SearchService

class ExampleService:
    @staticmethod
    def get_search_results(store, query, filters=None):
        """APPLICATION MUST: Use infrastructure service"""
        return SearchService.search(
            store=store,
            query=query,
            filters=filters
        )

    @staticmethod
    def index_content(store, content):
        """APPLICATION MUST: Prepare data and use infrastructure"""
        data = {
            'title': content.title,
            'content': content.body,
            'description': getattr(content, 'description', ''),
            'url': content.get_absolute_url(),
            'created_at': content.created_at.isoformat()
        }

        return SearchService.index_document(
            store=store,
            document_type=content.__class__.__name__,
            document_id=str(content.id),
            data=data
        )
```

---

## 📝 Notes
### **Infrastructure Management Commands**
#### Rebuild Index
```bash
# Rebuild search index for store
python manage.py rebuild_index --store=my-store
```

#### Index Content
```bash
# Index specific content type
python manage.py index_content --store=my-store --type=Page
```

---

**Version**: 1.0
**Last Updated**: 2026-01-26
**Next Review**: 2026-02-25
