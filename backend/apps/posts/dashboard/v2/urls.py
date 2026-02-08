"""Dashboard posts API urls."""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import CommentDashboardViewSet, DashboardPostViewSet

# Dashboard router
router = DefaultRouter()
router.register(r"posts", DashboardPostViewSet, basename="dashboard-post")
router.register(r"comments", CommentDashboardViewSet, basename="dashboard-comments")

urlpatterns = [
    path("", include(router.urls)),
]
