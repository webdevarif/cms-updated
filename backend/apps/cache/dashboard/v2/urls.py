"""
Dashboard cache API URLs.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CacheDashboardViewSet, CacheStatsDashboardViewSet

router = DefaultRouter()
router.register(r"entries", CacheDashboardViewSet, basename="cache-dashboard")
router.register(r"stats", CacheStatsDashboardViewSet, basename="cache-stats-dashboard")

urlpatterns = [
    path("", include(router.urls)),
]
