"""
Customer stores API URLs.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import StoreAccessViewSet, StoreCustomerViewSet

router = DefaultRouter()
router.register(r"", StoreCustomerViewSet, basename="store-customer")
router.register(r"access", StoreAccessViewSet, basename="store-access")

urlpatterns = [
    path("", include(router.urls)),
]
