"""
V2 API views for analytics app.
"""

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models.events import EventLog, SearchLog
from ..services.analytics_service import AnalyticsService
from ..services.event_service import EventService
from ..services.search_service import SimpleSearchService
from .serializers import EventLogSerializer, SearchLogSerializer


class AnalyticsViewSet(viewsets.ViewSet):
    """
    Analytics API viewset for comprehensive analytics data.
    """

    @action(detail=False, methods=["get"])
    def overview(self, request):
        """Get analytics overview data"""
        store = getattr(request, "store", None)
        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            overview_data = AnalyticsService.get_overview(store)
            return Response(overview_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["get"])
    def trends(self, request):
        """Get analytics trends data"""
        store = getattr(request, "store", None)
        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            trends_data = AnalyticsService.get_trends(store)
            return Response(trends_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["get"])
    def popular_content(self, request):
        """Get popular content analytics"""
        store = getattr(request, "store", None)
        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            popular_data = AnalyticsService.get_popular_content(store)
            return Response(popular_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EventLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API viewset for EventLog model.
    """

    serializer_class = EventLogSerializer

    def get_queryset(self):
        store = getattr(self.request, "store", None)
        if store:
            return EventLog.objects.filter(store=store)
        return EventLog.objects.none()

    @action(detail=False, methods=["get"])
    def search(self, request):
        """Search event logs"""
        store = getattr(self.request, "store", None)
        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        query = request.GET.get("q", "").strip()
        if not query:
            return Response({"results": []})

        try:
            results = AnalyticsService.search_events(store, query)
            return Response({"results": results})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API viewset for SearchLog model.
    """

    serializer_class = SearchLogSerializer

    def get_queryset(self):
        store = getattr(self.request, "store", None)
        if store:
            return SearchLog.objects.filter(store=store)
        return SearchLog.objects.none()

    @action(detail=False, methods=["get"])
    def popular_queries(self, request):
        """Get popular search queries"""
        store = getattr(self.request, "store", None)
        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            popular_queries = AnalyticsService.get_popular_search_queries(store)
            return Response({"queries": popular_queries})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["get"])
    def search_performance(self, request):
        """Get search performance metrics"""
        store = getattr(self.request, "store", None)
        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            performance_data = AnalyticsService.get_search_performance(store)
            return Response(performance_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
