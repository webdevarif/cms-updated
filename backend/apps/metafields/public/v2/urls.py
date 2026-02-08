"""
URL configuration for metafields public API v2.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import MetafieldPublicViewSet

# Public router
router = DefaultRouter()
router.register(r"metafields", MetafieldPublicViewSet, basename="public-metafields")

urlpatterns = [
    path("", include(router.urls)),
]
