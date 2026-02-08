"""
URL configuration for forms public API v2.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import PublicFormViewSet

# Public router
router = DefaultRouter()
router.register(r"forms", PublicFormViewSet, basename="public-forms")

urlpatterns = [
    path("", include(router.urls)),
]
