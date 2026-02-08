"""
URL configuration for entities public API v2.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import PublicEntityActionViewSet, PublicEntityInteractionViewSet

# Public router
router = DefaultRouter()
router.register(r"actions", PublicEntityActionViewSet, basename="public-entity-actions")
router.register(
    r"interactions",
    PublicEntityInteractionViewSet,
    basename="public-entity-interactions",
)

urlpatterns = [
    path("", include(router.urls)),
]
