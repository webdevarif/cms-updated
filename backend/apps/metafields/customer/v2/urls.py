"""
URL configuration for metafields customer API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MetafieldCustomerViewSet

# Customer router
router = DefaultRouter()
router.register(r'metafields', MetafieldCustomerViewSet, basename='customer-metafields')

urlpatterns = [
    path('', include(router.urls)),
]
