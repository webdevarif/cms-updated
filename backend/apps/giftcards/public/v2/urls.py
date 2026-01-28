"""
Public gift cards URLs - read-only interface for gift card balance checks.
Architectural + real implementation for public gift cards interface.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PublicGiftCardViewSet

router = DefaultRouter()
router.register(r"gift-cards", PublicGiftCardViewSet, basename="public-gift-cards")

urlpatterns = [
    path("", include(router.urls)),
]
