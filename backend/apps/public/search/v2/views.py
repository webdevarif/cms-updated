"""
API views for search module.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.throttling import AnonRateThrottle

from rest_framework import viewsets
from core.permissions import IsStoreOwner
from ..models import SearchIndex, SearchQuery
from ..services import SearchService
from .serializers import SearchIndexSerializer, SearchDocumentSerializer, SearchResultsSerializer, FacetsSerializer, SuggestionsSerializer


class SearchViewSet(viewsets.ModelViewSet):
    """
    Search endpoints
    """
    permission_classes = []  # Allow anonymous access
    throttle_classes = [AnonRateThrottle]
    
    @extend_schema(
        summary="Search",
        description="Perform search query",
        responses={200: SearchResultsSerializer}
    )
    def list(self, request):
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
        
        facets = SearchService.get_facets(
            store=request.store,
            search_type=search_type
        )
        
        return Response(facets, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Get Suggestions",
        description="Get search suggestions",
        responses={200: SuggestionsSerializer}
    )
    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """Get search suggestions"""
        query = request.query_params.get('q', '')
        
        if not query:
            return Response([], status=status.HTTP_200_OK)
        
        suggestions = SearchService.get_suggestions(
            store=request.store,
            query=query
        )
        
        return Response(suggestions, status=status.HTTP_200_OK)


class SearchIndexViewSet(viewsets.ModelViewSet):
    """
    Search index management endpoints
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = SearchIndexSerializer
    
    def get_queryset(self):
        return SearchIndex.objects.filter(store=self.request.store)
    
    @extend_schema(
        summary="Rebuild Index",
        description="Rebuild search index from content",
        responses={200: None}
    )
    @action(detail=True, methods=['post'])
    def rebuild(self, request, pk=None):
        """Rebuild search index"""
        search_index = self.get_object()
        
        # Trigger async rebuild
        from ..tasks import rebuild_index
        task = rebuild_index.delay(search_index.store.id)
        
        return Response({
            'message': 'Index rebuild started',
            'task_id': task.id
        })


class SearchDocumentViewSet(viewsets.ModelViewSet):
    """
    Search document management endpoints
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = SearchDocumentSerializer
    
    def get_queryset(self):
        return SearchDocument.objects.filter(store=self.request.store)
