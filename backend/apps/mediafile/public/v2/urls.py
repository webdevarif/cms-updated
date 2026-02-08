"""
URL configuration for mediafile public API v2.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import MediafilePublicViewSet, MediafolderPublicViewSet

# Public router
router = DefaultRouter()
router.register(r"files", MediafilePublicViewSet, basename="public-mediafiles")
router.register(r"folders", MediafolderPublicViewSet, basename="public-mediafolders")

urlpatterns = [
    path("", include(router.urls)),
]
