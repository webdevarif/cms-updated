"""
Customer pages URLs - authenticated user manages own pages.
Architectural + real implementation for customer pages interface.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import PageCustomerViewSet

router = DefaultRouter()
router.register(r"pages", PageCustomerViewSet, basename="customer-pages")

urlpatterns = [
    path("", include(router.urls)),
]
