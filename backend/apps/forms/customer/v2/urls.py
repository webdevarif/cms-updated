"""
URL configuration for forms customer API v2.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import CustomerFormViewSet

# Customer router
router = DefaultRouter()
router.register(r"forms", CustomerFormViewSet, basename="customer-forms")

urlpatterns = [
    path("", include(router.urls)),
]
