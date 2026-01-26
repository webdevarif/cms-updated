"""
URL configuration for entities dashboard API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DashboardEntityActionViewSet, DashboardEntityInteractionViewSet

# Dashboard router
router = DefaultRouter()
router.register(r'actions', DashboardEntityActionViewSet, basename='dashboard-entity-actions')
router.register(r'interactions', DashboardEntityInteractionViewSet, basename='dashboard-entity-interactions')

urlpatterns = [
    path('', include(router.urls)),
]
