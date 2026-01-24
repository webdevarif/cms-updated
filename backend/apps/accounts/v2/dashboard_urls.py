"""
Dashboard URL configuration for Digital Farmers CMS accounts API.

Store user management endpoints for dashboard.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .dashboard_views import StoreUserViewSet

router = DefaultRouter()
router.register(r'users', StoreUserViewSet, basename='store-users')

urlpatterns = [
    path('', include(router.urls)),
]
