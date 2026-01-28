"""
URL configuration for accounts customer API v2.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomerUserViewSet

router = DefaultRouter()
router.register(r"users", CustomerUserViewSet, basename="customer-users")

urlpatterns = [
    path("", include(router.urls)),
]
