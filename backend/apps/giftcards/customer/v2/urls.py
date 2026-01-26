"""
Customer gift cards URLs - authenticated interface for gift card management.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomerGiftCardViewSet

# Customer router
router = DefaultRouter()
router.register(r'gift-cards', CustomerGiftCardViewSet, basename='customer-gift-cards')

urlpatterns = [
    path('', include(router.urls)),
]
