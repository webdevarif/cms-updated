"""
URL configuration for test public API v2.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TestDashboardViewSet, TestDeliveryDashboardViewSet, TestPublicViewSet

# Public router for test
public_router = DefaultRouter()
public_router.register(r"test", TestPublicViewSet, basename="public-test")

# Dashboard router for test
dashboard_router = DefaultRouter()
dashboard_router.register(r"test", TestDashboardViewSet, basename="dashboard-test")
dashboard_router.register(
    r"test-deliveries",
    TestDeliveryDashboardViewSet,
    basename="dashboard-test-deliveries",
)

urlpatterns = [
    path("", include(public_router.urls)),
    path("dashboard/", include(dashboard_router.urls)),
]
