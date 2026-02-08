"""
Dashboard pages URLs - admin interface for page management.
Architectural + real implementation for dashboard pages interface.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import PageDashboardViewSet, PostTypeViewSet, TaxonomyViewSet, TermViewSet
from .views_navigation import MenuDashboardViewSet, MenuItemDashboardViewSet

# Dashboard router for pages
router = DefaultRouter()
router.register(r"pages", PageDashboardViewSet, basename="dashboard-pages")
router.register(r"post-types", PostTypeViewSet, basename="dashboard-post-types")
router.register(r"taxonomies", TaxonomyViewSet, basename="dashboard-taxonomies")
router.register(r"terms", TermViewSet, basename="dashboard-terms")

# Dashboard router for navigation
navigation_router = DefaultRouter()
navigation_router.register(r"menus", MenuDashboardViewSet, basename="dashboard-menus")
navigation_router.register(r"menu-items", MenuItemDashboardViewSet, basename="dashboard-menu-items")

urlpatterns = [
    path("", include(router.urls)),
    path("navigation/", include(navigation_router.urls)),
]
