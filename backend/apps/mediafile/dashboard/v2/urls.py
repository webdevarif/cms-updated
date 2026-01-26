"""
URL configuration for mediafile dashboard API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MediafileDashboardViewSet, MediafolderDashboardViewSet

# Dashboard router
router = DefaultRouter()
router.register(r'files', MediafileDashboardViewSet, basename='dashboard-mediafiles')
router.register(r'folders', MediafolderDashboardViewSet, basename='dashboard-mediafolders')

urlpatterns = [
    path('', include(router.urls)),
]
