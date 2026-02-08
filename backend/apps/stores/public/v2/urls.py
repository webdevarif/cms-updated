"""
Public stores API URLs.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import StorePublicViewSet, StoreVerificationViewSet

router = DefaultRouter()
router.register(r"", StorePublicViewSet, basename="store-public")
router.register(r"verify", StoreVerificationViewSet, basename="store-verify")

urlpatterns = [
    path("", include(router.urls)),
]
