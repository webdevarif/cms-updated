"""
URL configuration for stores public API v2.
Stores V2 API URLs.
Consolidated URL patterns for all store operations.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from . import views

# Create router for store endpoints
router = DefaultRouter()

# Public endpoints (no auth required)
router.register(r"public", views.StorePublicViewSet, basename="store-public")

# Customer endpoints (store users)
router.register(r"customer", views.StoreCustomerViewSet, basename="store-customer")

# Dashboard endpoints (store owners)
router.register(r"dashboard", views.StoreDashboardViewSet, basename="store-dashboard")

urlpatterns = [
    path("", include(router.urls)),
]
