"""
Dashboard stores API URLs.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import StoreDashboardViewSet

router = DefaultRouter()
router.register(r"", StoreDashboardViewSet, basename="store-dashboard")

urlpatterns = [
    path("", include(router.urls)),
]
