"""
Public themes API URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ThemePublicViewSet

router = DefaultRouter()
router.register(r'', ThemePublicViewSet, basename='theme-public')

urlpatterns = [
    path('', include(router.urls)),
]
