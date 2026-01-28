"""Dashboard posts API urls."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentDashboardViewSet, DashboardPostViewSet

# Dashboard router
router = DefaultRouter()
router.register(r"posts", DashboardPostViewSet, basename="dashboard-post")
router.register(r"comments", CommentDashboardViewSet, basename="dashboard-comments")

urlpatterns = [
    path("", include(router.urls)),
]
