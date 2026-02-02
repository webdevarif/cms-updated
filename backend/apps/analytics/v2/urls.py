"""
V2 URL configuration for analytics app.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AnalyticsViewSet, EventLogViewSet, SearchLogViewSet

# Create routers
analytics_router = DefaultRouter()
event_log_router = DefaultRouter()
search_log_router = DefaultRouter()

# Register viewsets
analytics_router.register(r"", AnalyticsViewSet, basename="analytics")
event_log_router.register(r"events", EventLogViewSet, basename="event-logs")
search_log_router.register(r"search", SearchLogViewSet, basename="search-logs")

urlpatterns = [
    path("", include(analytics_router.urls)),
    path("events/", include(event_log_router.urls)),
    path("search/", include(search_log_router.urls)),
]
