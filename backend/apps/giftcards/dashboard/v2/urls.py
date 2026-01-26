"""
Dashboard gift cards URLs - admin interface for gift card management.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DashboardGiftCardViewSet

# Dashboard router
router = DefaultRouter()
router.register(r'gift-cards', DashboardGiftCardViewSet, basename='dashboard-gift-cards')

urlpatterns = [
    path('', include(router.urls)),
]
