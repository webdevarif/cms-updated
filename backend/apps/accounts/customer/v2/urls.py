"""
URL configuration for accounts customer API v2.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import CustomerUserViewSet

router = DefaultRouter()
router.register(r"users", CustomerUserViewSet, basename="customer-users")

urlpatterns = [
    path("", include(router.urls)),
]
