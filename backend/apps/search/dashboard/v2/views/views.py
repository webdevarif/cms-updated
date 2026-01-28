"""
Dashboard search API views - full admin CRUD with analytics and bulk operations.
"""
from apps.search.models.infrastructure import SearchIndex, SearchQuery
from apps.search.services import SearchService
from core.permissions import IsStoreAdmin
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    SearchAnalyticsSerializer,
    SearchIndexSerializer,
    SearchQuerySerializer,
    SearchResultSerializer,
    SearchSuggestionSerializer,
)


class SearchViewSet(viewsets.ViewSet):
    """
    Dashboard search API - full admin search with analytics and management.
    Provides comprehensive search functionality for store administrators.
    """

    permission_classes = [IsStoreAdmin]

    @extend_schema(
        summary="Admin search",
        description="Full search across all store content with admin privileges",
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
                description="Content type filter (product, post, page, all)",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="status",
                description="Content status filter (published, draft, etc.)",
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
        """Admin search across all content"""
        query = request.GET.get("q", "").strip()
        content_type = request.GET.get("type", "all")
        content_status = request.GET.get("status")
        limit = int(request.GET.get("limit", 20))
        offset = int(request.GET.get("offset", 0))

        if not query:
            return Response(
                {"error": "Search query is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        store = request.store
        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Build filters for admin search
            filters = {}
            if content_status:
                filters["status"] = content_status

            # Use real SearchService with Elasticsearch
            results = SearchService.search(
                query=query,
                types=[content_type] if content_type != "all" else None,
                store=store,
                limit=limit,
                offset=offset,
            )

            # Format response with admin metadata
            serializer = SearchResultSerializer(
                {
                    "total": len(results),
                    "results": results,
                    "facets": {},  # Could be enhanced
                    "query": query,
                    "limit": limit,
                    "offset": offset,
                    "duration_ms": 0,
                    "filters": filters,
                }
            )

            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": f"Search failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["post"])
    def reindex(self, request):
        """Trigger full search index rebuild"""
        store = request.store
        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Trigger async reindexing
            from apps.search.tasks import rebuild_search_index

            rebuild_search_index.delay(store.id)

            return Response({"message": "Search index rebuild initiated", "store": store.slug})
        except Exception as e:
            return Response(
                {"error": f"Reindex failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get search analytics and insights with time-range filtering"""
        store = request.store
        if not store:
            return Response({"analytics": {}})

        # Parse time range parameters
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        from datetime import datetime

        date_filter = {}
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                date_filter["created_at__gte"] = start_dt
            except ValueError:
                return Response(
                    {"error": "Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                date_filter["created_at__lte"] = end_dt
            except ValueError:
                return Response(
                    {"error": "Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            # Base queryset with date filtering
            queries = SearchQuery.objects.filter(store=store, **date_filter).order_by(
                "-created_at"
            )[
                :1000
            ]  # Increased limit for better analytics

            # Aggregate analytics
            total_queries = queries.count()
            unique_queries = queries.values("query").distinct().count()

            # Top queries with time filtering
            top_queries = (
                queries.values("query")
                .annotate(
                    count=Count("query"),
                    avg_results=Avg("results_count"),
                    last_used=Max("created_at"),
                )
                .order_by("-count")[:10]
            )

            # Recent no-results queries
            no_results = queries.filter(results_count=0).order_by("-created_at")[:10]

            # Search performance metrics
            avg_results_per_query = queries.aggregate(avg=Avg("results_count"))["avg"] or 0
            zero_results_rate = (
                (queries.filter(results_count=0).count() / total_queries * 100)
                if total_queries > 0
                else 0
            )

            # Search trends over time
            search_trends = []
            if start_date and end_date:
                from django.db.models.functions import TruncDate

                daily_searches = (
                    queries.annotate(date=TruncDate("created_at"))
                    .values("date")
                    .annotate(
                        total_queries=Count("id"),
                        unique_queries=Count("query", distinct=True),
                        zero_results=Count("id", filter=Q(results_count=0)),
                        avg_results=Avg("results_count"),
                    )
                    .order_by("date")
                )

                search_trends = [
                    {
                        "date": str(item["date"]),
                        "total_queries": item["total_queries"],
                        "unique_queries": item["unique_queries"],
                        "zero_results": item["zero_results"],
                        "avg_results": float(item["avg_results"] or 0),
                        "success_rate": (
                            (item["total_queries"] - item["zero_results"])
                            / item["total_queries"]
                            * 100
                        )
                        if item["total_queries"] > 0
                        else 0,
                    }
                    for item in daily_searches
                ]

            # Content type popularity (based on search results)
            content_type_popularity = (
                queries.values("search_type")
                .annotate(count=Count("id"), avg_results=Avg("results_count"))
                .exclude(search_type="")
                .order_by("-count")
            )

            content_types = []
            for ct in content_type_popularity:
                content_types.append(
                    {
                        "type": ct["search_type"],
                        "searches": ct["count"],
                        "avg_results": float(ct["avg_results"] or 0),
                    }
                )

            # User engagement metrics
            user_engagement = {
                "total_search_sessions": queries.values("user").distinct().count()
                if queries.filter(user__isnull=False).exists()
                else 0,
                "avg_searches_per_user": total_queries
                / max(queries.values("user").distinct().count(), 1),
                "conversion_rate": 0,  # Would need additional tracking for actual conversions
            }

            analytics_data = {
                "overview": {
                    "total_queries": total_queries,
                    "unique_queries": unique_queries,
                    "avg_results_per_query": float(avg_results_per_query),
                    "zero_results_rate": float(zero_results_rate),
                    "success_rate": float(100 - zero_results_rate),
                },
                "performance": {
                    "top_queries": list(top_queries),
                    "no_results_queries": [
                        {"query": q.query, "timestamp": q.created_at.isoformat()}
                        for q in no_results
                    ],
                    "content_types": content_types,
                    "trends": search_trends,
                },
                "engagement": user_engagement,
                "time_range": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "has_date_filter": bool(start_date or end_date),
                },
            }

            serializer = SearchAnalyticsSerializer(analytics_data)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": f"Analytics failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SearchIndexViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Search index management for administrators.
    """

    permission_classes = [IsStoreAdmin]
    serializer_class = SearchIndexSerializer

    def get_queryset(self):
        return SearchIndex.objects.filter(store=self.request.store)


class SearchQueryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Search query history and logs for administrators.
    """

    permission_classes = [IsStoreAdmin]
    serializer_class = SearchQuerySerializer

    def get_queryset(self):
        return SearchQuery.objects.filter(store=self.request.store).order_by("-created_at")
