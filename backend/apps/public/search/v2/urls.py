"""
URL configuration for search API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'search_v2'

router = DefaultRouter()
router.register(r'search', views.SearchViewSet, basename='search')
router.register(r'indices', views.SearchIndexViewSet, basename='search_index')

urlpatterns = [
    path('', include(router.urls)),
]
