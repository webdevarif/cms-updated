"""
Dashboard search API URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SearchViewSet, SearchIndexViewSet, SearchQueryViewSet

router = DefaultRouter()
router.register(r'', SearchViewSet, basename='search-dashboard')
router.register(r'indices', SearchIndexViewSet, basename='search-indices')
router.register(r'queries', SearchQueryViewSet, basename='search-queries')

urlpatterns = [
    path('', include(router.urls)),
]
