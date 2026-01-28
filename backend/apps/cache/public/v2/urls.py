"""
Public cache API URLs.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CacheStatsPublicViewSet

router = DefaultRouter()
router.register(r"stats", CacheStatsPublicViewSet, basename="cache-stats-public")

urlpatterns = [
    path("", include(router.urls)),
]
