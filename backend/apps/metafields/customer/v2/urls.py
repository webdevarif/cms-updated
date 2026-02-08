"""
URL configuration for metafields customer API v2.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import MetafieldCustomerViewSet

# Customer router
router = DefaultRouter()
router.register(r"metafields", MetafieldCustomerViewSet, basename="customer-metafields")

urlpatterns = [
    path("", include(router.urls)),
]
