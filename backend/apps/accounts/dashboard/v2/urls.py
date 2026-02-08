"""
URL configuration for accounts dashboard API v2.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import DashboardStoreUserViewSet, DashboardUserViewSet

router = DefaultRouter()
router.register(r"users", DashboardUserViewSet, basename="dashboard-users")
router.register(r"store-users", DashboardStoreUserViewSet, basename="dashboard-store-users")

urlpatterns = [
    path("", include(router.urls)),
]
