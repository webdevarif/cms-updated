"""
URL configuration for entities dashboard API v2.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import DashboardEntityActionViewSet, DashboardEntityInteractionViewSet

# Dashboard router
router = DefaultRouter()
router.register(r"actions", DashboardEntityActionViewSet, basename="dashboard-entity-actions")
router.register(
    r"interactions",
    DashboardEntityInteractionViewSet,
    basename="dashboard-entity-interactions",
)

urlpatterns = [
    path("", include(router.urls)),
]
