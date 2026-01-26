"""
Search service for unified search functionality with real Elasticsearch tuning.
Provides advanced search features: field boosting, highlighting, suggestions, facets, and logging.
"""
import logging
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q, A
from django.conf import settings
from .infrastructure import SearchService as InfrastructureSearchService

logger = logging.getLogger(__name__)

class SearchService:
    """
    Application-level search service with real Elasticsearch tuning.
    Provides advanced search features: field boosting, highlighting, suggestions, facets.
    """

    # Elasticsearch field boosting weights
    FIELD_BOOSTS = {
        'title': 5,
        'content': 3,
        'excerpt': 2,
        'tags': 2,
        'metafields': 1,
        'sku': 3,  # For products
        'description': 2,
    }

    @staticmethod
    def search(query, types=None, store=None, limit=20, offset=0, user=None, comment_type=None, min_rating=None):
        """
        Advanced search with real Elasticsearch tuning.

        Args:
            query: Search query string
            types: List of content types (products, posts, pages, comments, reviews)
            store: Store instance for scoping
            limit: Maximum results to return
            offset: Results offset for pagination
            user: User instance for personalization
            comment_type: Filter by 'comment' or 'review' or None for all
            min_rating: Minimum rating for reviews (1-5)

        Returns:
            Dict with results, facets, highlighting, suggestions
        """
        if not query or len(query.strip()) < 2:
            return {
                'results': [],
                'total': 0,
                'facets': {},
                'highlighting': {},
                'suggestions': [],
                'duration_ms': 0
            }

        try:
            # Get Elasticsearch client
            es_client = SearchService._get_es_client()

            # Build search query with field boosting
            search_query = SearchService._build_search_query(query, types, store, user, comment_type, min_rating)

            # Add highlighting
            search_query = SearchService._add_highlighting(search_query)

            # Add facets/aggregations
            search_query = SearchService._add_facets(search_query)

            # Execute search
            response = search_query[offset:offset+limit].execute()

            # Process results
            results = SearchService._process_results(response)
            facets = SearchService._process_facets(response)
            highlighting = SearchService._process_highlighting(response)
            suggestions = SearchService.get_suggestions(store, query[:20], 5)  # Limit query for suggestions

            # Log the search
            SearchService._log_search(query, len(results), store)

            return {
                'results': results,
                'total': response.hits.total.value,
                'facets': facets,
                'highlighting': highlighting,
                'suggestions': suggestions,
                'duration_ms': int(response.took)
            }

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            # Fallback to infrastructure service
            return InfrastructureSearchService.search(
                store=store,
                query=query,
                search_type=types[0] if types else 'all',
                page=(offset // limit) + 1,
                page_size=limit
            )

    @staticmethod
    def _get_es_client():
        """Get Elasticsearch client instance"""
        return Elasticsearch([{
            'host': getattr(settings, 'ELASTICSEARCH_HOST', 'localhost'),
            'port': getattr(settings, 'ELASTICSEARCH_PORT', 9200),
            'scheme': getattr(settings, 'ELASTICSEARCH_SCHEME', 'http'),
        }])

    @staticmethod
    def _build_search_query(query, types=None, store=None, user=None, comment_type=None, min_rating=None):
        """Build Elasticsearch query with field boosting and personalization"""
        # Create search instance
        search = Search(using=SearchService._get_es_client())

        # Index name with store scoping
        index_name = f"store_{store.id if store else 'global'}_search"
        search = search.index(index_name)

        # Multi-match query with field boosting
        fields = []
        for field, boost in SearchService.FIELD_BOOSTS.items():
            fields.append(f"{field}^{boost}")

        multi_match = Q('multi_match', query=query, fields=fields, fuzziness='AUTO')

        # Content type filtering
        if types:
            type_filter = Q('terms', content_type=types)
            search = search.query(multi_match & type_filter)
        else:
            search = search.query(multi_match)

        # Comment type filtering (comment vs review)
        if comment_type:
            if comment_type == 'comment':
                comment_filter = Q('term', content_type='Comment')
                search = search.filter(comment_filter)
            elif comment_type == 'review':
                review_filter = Q('term', content_type='Review')
                search = search.filter(review_filter)

        # Minimum rating filter for reviews
        if min_rating and min_rating > 0:
            rating_filter = Q('range', rating={'gte': min_rating})
            search = search.filter(rating_filter)

        # Store scoping (if not already in index name)
        if store:
            store_filter = Q('term', store_id=store.id)
            search = search.filter(store_filter)

        # Personalization for authenticated users
        if user and store:
            # Boost user's own content slightly
            personalization = Q('term', author_id=user.id)
            search = search.query(multi_match & personalization)

        return search

    @staticmethod
    def _add_highlighting(search_query):
        """Add highlighting configuration"""
        return search_query.highlight(
            'title',
            'content',
            'excerpt',
            'description',
            fragment_size=100,
            number_of_fragments=3,
            pre_tags=['<mark>'],
            post_tags=['</mark>']
        )

    @staticmethod
    def _add_facets(search_query):
        """Add aggregation facets"""
        # Content type facet
        search_query.aggs.bucket('content_types', 'terms', field='content_type')

        # Language facet
        search_query.aggs.bucket('languages', 'terms', field='language')

        # Store facet (for admin searches)
        search_query.aggs.bucket('stores', 'terms', field='store_id')

        # Date histogram facet (last 30 days)
        search_query.aggs.bucket('recent', 'date_histogram',
                                field='created_at',
                                calendar_interval='day')

        return search_query

    @staticmethod
    def _process_results(response):
        """Process search results into unified format"""
        results = []
        for hit in response:
            result = {
                'id': hit.meta.id,
                'type': hit.content_type,
                'title': hit.title,
                'slug': getattr(hit, 'slug', ''),
                'excerpt': getattr(hit, 'excerpt', ''),
                'content': getattr(hit, 'content', '')[:200] + '...' if hasattr(hit, 'content') and len(hit.content) > 200 else getattr(hit, 'content', ''),
                'url': getattr(hit, 'url', ''),
                'score': hit.meta.score,
                'language': getattr(hit, 'language', 'en'),
                'tags': getattr(hit, 'tags', []),
                'created_at': getattr(hit, 'created_at', None),
                'updated_at': getattr(hit, 'updated_at', None),
                'store_id': getattr(hit, 'store_id', None),
                'author_id': getattr(hit, 'author_id', None),
                'metadata': {
                    'index': hit.meta.index,
                    'id': hit.meta.id,
                    'score': hit.meta.score
                }
            }
            results.append(result)

        return results

    @staticmethod
    def _process_facets(response):
        """Process aggregation results into facets"""
        facets = {}

        if hasattr(response.aggregations, 'content_types'):
            facets['content_types'] = [
                {'key': bucket.key, 'count': bucket.doc_count}
                for bucket in response.aggregations.content_types.buckets
            ]

        if hasattr(response.aggregations, 'languages'):
            facets['languages'] = [
                {'key': bucket.key, 'count': bucket.doc_count}
                for bucket in response.aggregations.languages.buckets
            ]

        if hasattr(response.aggregations, 'stores'):
            facets['stores'] = [
                {'key': bucket.key, 'count': bucket.doc_count}
                for bucket in response.aggregations.stores.buckets
            ]

        if hasattr(response.aggregations, 'recent'):
            facets['recent'] = [
                {'key': bucket.key_as_string, 'count': bucket.doc_count}
                for bucket in response.aggregations.recent.buckets
            ]

        return facets

    @staticmethod
    def _process_highlighting(response):
        """Process highlighting results"""
        highlighting = {}

        for hit in response:
            if hasattr(hit.meta, 'highlight'):
                highlighting[hit.meta.id] = hit.meta.highlight

        return highlighting

    @staticmethod
    def get_suggestions(store, query, limit=10):
        """
        Get search suggestions using completion suggester.

        Args:
            store: Store instance
            query: Query prefix for suggestions
            limit: Maximum suggestions to return

        Returns:
            List of suggestion strings
        """
        if not query or len(query.strip()) < 1:
            return []

        try:
            es_client = SearchService._get_es_client()
            index_name = f"store_{store.id if store else 'global'}_search"

            # Completion suggester query
            suggestion_query = {
                "suggest": {
                    "title_suggestions": {
                        "prefix": query.lower(),
                        "completion": {
                            "field": "title_completion",
                            "size": limit,
                            "skip_duplicates": True
                        }
                    }
                }
            }

            response = es_client.search(
                index=index_name,
                body=suggestion_query
            )

            suggestions = []
            if 'suggest' in response and 'title_suggestions' in response['suggest']:
                for option in response['suggest']['title_suggestions'][0]['options']:
                    suggestions.append(option['text'])

            return suggestions[:limit]

        except Exception as e:
            logger.error(f"Suggestions error: {str(e)}")
            return []

    @staticmethod
    def _log_search(query, results_count, store=None):
        """
        Log search query to SearchLog model.

        Args:
            query: Search query string
            results_count: Number of results returned
            store: Store instance
        """
        try:
            from apps.search.models.infrastructure import SearchQuery
            SearchQuery.objects.create(
                store=store,
                query=query,
                results_count=results_count,
                user_agent='',  # Would be populated from request
                ip_address='',  # Would be populated from request
                search_type='all'
            )
        except Exception as e:
            logger.error(f"Search logging error: {str(e)}")
