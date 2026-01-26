"""
URL configuration for metafields dashboard API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MetafieldDashboardViewSet, MetafieldDefinitionDashboardViewSet

# Dashboard router
router = DefaultRouter()
router.register(r'metafields', MetafieldDashboardViewSet, basename='dashboard-metafields')
router.register(r'metafield-definitions', MetafieldDefinitionDashboardViewSet, basename='dashboard-metafield-definitions')

urlpatterns = [
    path('', include(router.urls)),
]
