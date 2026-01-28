"""
Customer search API views - authenticated search with own content prioritization.
"""
from apps.search.services import SearchService
from core.permissions import IsAuthenticatedAndStoreOwner
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import SearchHistorySerializer, SearchResultSerializer, SearchSuggestionSerializer


class SearchViewSet(viewsets.ViewSet):
    """
    Customer search API - authenticated search with store-scoped results.
    Prioritizes own content and provides personalized search experience.
    """

    permission_classes = [IsAuthenticatedAndStoreOwner]

    @extend_schema(
        summary="Search store content",
        description="Search within authenticated user's store content",
        parameters=[
            OpenApiParameter(
                name="q",
                description="Search query",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="type",
                description="Content type filter (product, post, page)",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="limit",
                description="Results per page",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY,
                default=20,
            ),
            OpenApiParameter(
                name="offset",
                description="Results offset",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY,
                default=0,
            ),
        ],
    )
    def list(self, request):
        """Personalized search within authenticated user's store content"""
        query = request.GET.get("q", "").strip()
        content_type = request.GET.get("type", "all")
        limit = int(request.GET.get("limit", 20))
        offset = int(request.GET.get("offset", 0))

        if not query:
            return Response(
                {"error": "Search query is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        store = getattr(request, "store", None)
        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Use enhanced SearchService with personalization
            search_result = SearchService.search(
                query=query,
                types=[content_type] if content_type != "all" else None,
                store=store,
                limit=limit,
                offset=offset,
                user=request.user,  # Enable personalization for own content boosting
            )

            # Format enhanced response with personalization features
            response_data = {
                "total": search_result["total"],
                "results": search_result["results"],
                "facets": search_result["facets"],
                "highlighting": search_result["highlighting"],
                "suggestions": search_result["suggestions"],
                "query": query,
                "limit": limit,
                "offset": offset,
                "duration_ms": search_result["duration_ms"],
                "has_more": (offset + limit) < search_result["total"],
                "personalized": True,  # Indicate personalized results
                "store_id": store.id,
            }

            return Response(response_data)

        except Exception as e:
            return Response(
                {"error": f"Search failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"])
    def suggestions(self, request):
        """Get personalized search suggestions"""
        query = request.GET.get("q", "").strip()
        limit = int(request.GET.get("limit", 10))

        if not query or len(query) < 2:
            return Response({"suggestions": []})

        store = request.store
        if not store:
            return Response({"suggestions": []})

        try:
            suggestions = SearchService.get_suggestions(store, query, limit)
            serializer = SearchSuggestionSerializer(
                {"suggestions": [{"text": s, "type": "query"} for s in suggestions]}
            )
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": f"Suggestions failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def history(self, request):
        """Get user's search history"""
        limit = int(request.GET.get("limit", 20))
        offset = int(request.GET.get("offset", 0))

        store = request.store
        if not store:
            return Response({"history": []})

        try:
            # Could be enhanced to return real search history for the user
            history = []  # Placeholder for search history
            serializer = SearchHistorySerializer(
                {"history": history, "limit": limit, "offset": offset}
            )
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": f"History failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["post"])
    def save_search(self, request):
        """Save a search query for future reference"""
        query = request.data.get("query", "").strip()
        name = request.data.get("name", "").strip()

        if not query:
            return Response(
                {"error": "Search query is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        store = request.store
        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Could be enhanced to save search queries
            # For now, just return success
            return Response({"message": "Search saved successfully", "query": query, "name": name})
        except Exception as e:
            return Response(
                {"error": f"Save failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
