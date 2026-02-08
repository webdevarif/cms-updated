"""
URL configuration for forms dashboard API v2.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import DashboardFormSubmissionViewSet, DashboardFormTemplateViewSet

# Dashboard router
router = DefaultRouter()
router.register(r"forms", DashboardFormTemplateViewSet, basename="dashboard-forms")
router.register(r"submissions", DashboardFormSubmissionViewSet, basename="dashboard-submissions")

urlpatterns = [
    path("", include(router.urls)),
]
