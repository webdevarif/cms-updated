"""
Public pages URLs - read-only interface for published pages.
Architectural + real implementation for public pages interface.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PagePublicViewSet

# Public router for pages
router = DefaultRouter()
router.register(r"pages", PagePublicViewSet, basename="public-pages")

urlpatterns = [
    path("", include(router.urls)),
]
