"""
Customer stores API URLs.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import StoreAccessViewSet, StoreCustomerViewSet

router = DefaultRouter()
router.register(r"", StoreCustomerViewSet, basename="store-customer")
router.register(r"access", StoreAccessViewSet, basename="store-access")

urlpatterns = [
    path("", include(router.urls)),
]
