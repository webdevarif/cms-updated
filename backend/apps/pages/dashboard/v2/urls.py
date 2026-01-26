"""
Dashboard pages URLs - admin interface for page management.
Architectural + real implementation for dashboard pages interface.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PageDashboardViewSet, PostTypeViewSet, 
    TaxonomyViewSet, TermViewSet
)

# Dashboard router for pages
router = DefaultRouter()
router.register(r'pages', PageDashboardViewSet, basename='dashboard-pages')
router.register(r'post-types', PostTypeViewSet, basename='dashboard-post-types')
router.register(r'taxonomies', TaxonomyViewSet, basename='dashboard-taxonomies')
router.register(r'terms', TermViewSet, basename='dashboard-terms')

urlpatterns = [
    path('', include(router.urls)),
]
