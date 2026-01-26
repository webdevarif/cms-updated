"""
URL configuration for logs public API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PublicLogViewSet

# Public router
router = DefaultRouter()
router.register(r'logs', PublicLogViewSet, basename='public-logs')

urlpatterns = [
    path('', include(router.urls)),
]
