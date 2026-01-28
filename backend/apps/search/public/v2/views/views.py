"""
Public search API views - read-only search for content consumption.
"""
from apps.search.services import SearchService
from core.permissions import AllowAnyPublicRead
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from .serializers import SearchResultSerializer, SearchSuggestionSerializer


@extend_schema(
    tags=['Search'],
    summary='Public Search API',
    description='Full-text search with Elasticsearch tuning, facets, highlighting, and suggestions. Provides real-time search capabilities for public content.'
)
class SearchViewSet(viewsets.ViewSet):
    """
    Public search API with real Elasticsearch integration.
    Provides comprehensive search functionality for public access.
    """
    permission_classes = [AllowAnyPublicRead]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'search'  # Uses 'search' rate limit (100/hour)

    @extend_schema(
        summary="Search content",
        description="Search across published content with faceting and highlighting",
        parameters=[
            OpenApiParameter(
                name='q',
                description='Search query',
                required=True,
                type=str,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='type',
                description='Content type filter (product, post, page, comment, review)',
                required=False,
                type=str,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='comment_type',
                description='Filter by comment type (comment, review, or all)',
                required=False,
                type=str,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='min_rating',
                description='Minimum rating for reviews (1-5)',
                required=False,
                type=int,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='limit',
                description='Results per page',
                required=False,
                type=int,
                location=OpenApiParameter.QUERY,
                default=20
            ),
            OpenApiParameter(
                name='offset',
                description='Results offset',
                required=False,
                type=int,
                location=OpenApiParameter.QUERY,
                default=0
            ),
        ]
    )
    def list(self, request):
        """Advanced search with real Elasticsearch tuning"""
        query = request.GET.get('q', '').strip()
        content_type = request.GET.get('type', 'all')
        comment_type = request.GET.get('comment_type', None)
        min_rating = request.GET.get('min_rating', None)
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))

        if min_rating:
            min_rating = int(min_rating)

        if not query:
            return Response(
                {'error': 'Search query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get store from request (if available) - fallback to first active store
        store = getattr(request, 'store', None)
        if not store:
            # For public search, we might want to search across all stores or a default store
            # For now, return empty results if no store context
            return Response({
                'total': 0,
                'results': [],
                'facets': {},
                'highlighting': {},
                'suggestions': [],
                'query': query,
                'limit': limit,
                'offset': offset
            })

        try:
            # Use enhanced SearchService with real Elasticsearch
            search_result = SearchService.search(
                query=query,
                types=[content_type] if content_type != 'all' else None,
                store=store,
                limit=limit,
                offset=offset,
                user=request.user if request.user.is_authenticated else None,
                comment_type=comment_type,
                min_rating=min_rating
            )

            # Process results to include proper URLs for comments/reviews
            processed_results = []
            for result in search_result['results']:
                processed_result = result.copy()

                # Add proper URLs for comments and reviews
                if result['type'] == 'Comment':
                    processed_result['url'] = f"/posts/{result.get('post_id')}/#comment-{result['id']}"
                elif result['type'] == 'Review':
                    processed_result['url'] = f"/products/{result.get('product_id')}/#review-{result['id']}"

                # Add additional metadata for comments/reviews
                if result['type'] in ['Comment', 'Review']:
                    processed_result['author_display_name'] = result.get('author_display_name', '')
                    if result['type'] == 'Review':
                        processed_result['rating'] = result.get('rating', 0)
                        processed_result['verified_purchase'] = result.get('verified_purchase', False)

                processed_results.append(processed_result)

            return Response({
                'total': search_result['total'],
                'results': processed_results,
                'facets': search_result['facets'],
                'highlighting': search_result['highlighting'],
                'suggestions': search_result['suggestions'],
                'query': query,
                'limit': limit,
                'offset': offset,
                'duration_ms': search_result['duration_ms']
            })

        except Exception as e:
            return Response(
                {'error': f'Search failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
                offset=offset,
                user=request.user if request.user.is_authenticated else None
            )

            # Format enhanced response with all features
            response_data = {
                'total': search_result['total'],
                'results': search_result['results'],
                'facets': search_result['facets'],
                'highlighting': search_result['highlighting'],
                'suggestions': search_result['suggestions'],
                'query': query,
                'limit': limit,
                'offset': offset,
                'duration_ms': search_result['duration_ms'],
                'has_more': (offset + limit) < search_result['total']
            }

            return Response(response_data)

        except Exception as e:
            return Response(
                {'error': f'Search failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """Get search suggestions"""
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 10))

        if not query or len(query) < 2:
            return Response({'suggestions': []})

        store = getattr(request, 'store', None)
        if not store:
            return Response({'suggestions': []})

        try:
            suggestions = SearchService.get_suggestions(store, query, limit)
            serializer = SearchSuggestionSerializer({
                'suggestions': [{'text': s, 'type': 'query'} for s in suggestions]
            })
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Suggestions failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def facets(self, request):
        """Get available search facets"""
        store = getattr(request, 'store', None)
        if not store:
            return Response({'facets': []})

        try:
            # Could be enhanced to return real facets from Elasticsearch
            facets = [
                {
                    'field': 'type',
                    'label': 'Content Type',
                    'values': [
                        {'value': 'product', 'label': 'Products', 'count': 0},
                        {'value': 'post', 'label': 'Posts', 'count': 0},
                        {'value': 'page', 'label': 'Pages', 'count': 0}
                    ]
                }
            ]
            return Response({'facets': facets})
        except Exception as e:
            return Response(
                {'error': f'Facets failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
