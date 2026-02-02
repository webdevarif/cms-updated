"""
Customer pages URLs - authenticated interface for page management.
Architectural + real implementation for customer pages interface.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PageCustomerViewSet

# Customer router for pages
router = DefaultRouter()
router.register(r"pages", PageCustomerViewSet, basename="customer-pages")

urlpatterns = [
    path("", include(router.urls)),
]
