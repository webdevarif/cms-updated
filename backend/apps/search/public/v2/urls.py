"""
Public search API URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SearchViewSet

router = DefaultRouter()
router.register(r'', SearchViewSet, basename='search-public')

urlpatterns = [
    path('', include(router.urls)),
]
