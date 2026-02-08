"""
Public pages URLs - read-only interface for published pages.
Architectural + real implementation for public pages interface.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import PagePublicViewSet
from .views_navigation import MenuPublicViewSet

# Public router for pages
router = DefaultRouter()
router.register(r"pages", PagePublicViewSet, basename="public-pages")

# Public router for navigation
navigation_router = DefaultRouter()
navigation_router.register(r"menus", MenuPublicViewSet, basename="public-menus")

urlpatterns = [
    path("", include(router.urls)),
    path("navigation/", include(navigation_router.urls)),
]
