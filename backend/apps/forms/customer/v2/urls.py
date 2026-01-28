"""
URL configuration for forms customer API v2.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomerFormViewSet

# Customer router
router = DefaultRouter()
router.register(r"forms", CustomerFormViewSet, basename="customer-forms")

urlpatterns = [
    path("", include(router.urls)),
]
