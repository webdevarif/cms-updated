"""
Customer themes API URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ThemeCustomerViewSet

router = DefaultRouter()
router.register(r'', ThemeCustomerViewSet, basename='theme-customer')

urlpatterns = [
    path('', include(router.urls)),
]
