"""
URL configuration for metafields public API v2.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MetafieldPublicViewSet

# Public router
router = DefaultRouter()
router.register(r"metafields", MetafieldPublicViewSet, basename="public-metafields")

urlpatterns = [
    path("", include(router.urls)),
]
