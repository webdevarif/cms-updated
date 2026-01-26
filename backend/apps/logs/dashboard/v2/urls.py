"""
URL configuration for logs dashboard API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DashboardLogViewSet

# Dashboard router
router = DefaultRouter()
router.register(r'logs', DashboardLogViewSet, basename='dashboard-logs')

urlpatterns = [
    path('', include(router.urls)),
]
