"""
URL configuration for entities customer API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomerEntityActionViewSet, CustomerEntityInteractionViewSet

# Customer router
router = DefaultRouter()
router.register(r'actions', CustomerEntityActionViewSet, basename='customer-entity-actions')
router.register(r'interactions', CustomerEntityInteractionViewSet, basename='customer-entity-interactions')

urlpatterns = [
    path('', include(router.urls)),
]
