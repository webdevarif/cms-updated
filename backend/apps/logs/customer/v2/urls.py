"""
URL configuration for logs customer API v2.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomerLogViewSet

# Customer router
router = DefaultRouter()
router.register(r"logs", CustomerLogViewSet, basename="customer-logs")

urlpatterns = [
    path("", include(router.urls)),
]
