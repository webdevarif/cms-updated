"""
URL configuration for accounts dashboard API v2.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DashboardStoreUserViewSet, DashboardUserViewSet

router = DefaultRouter()
router.register(r"users", DashboardUserViewSet, basename="dashboard-users")
router.register(r"store-users", DashboardStoreUserViewSet, basename="dashboard-store-users")

urlpatterns = [
    path("", include(router.urls)),
]
