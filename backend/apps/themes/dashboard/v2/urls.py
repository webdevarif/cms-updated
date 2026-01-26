"""
Dashboard themes API URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ThemeDashboardViewSet

router = DefaultRouter()
router.register(r'', ThemeDashboardViewSet, basename='theme-dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
