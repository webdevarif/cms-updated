"""
URL configuration for forms dashboard API v2.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DashboardFormSubmissionViewSet, DashboardFormTemplateViewSet

# Dashboard router
router = DefaultRouter()
router.register(r"forms", DashboardFormTemplateViewSet, basename="dashboard-forms")
router.register(r"submissions", DashboardFormSubmissionViewSet, basename="dashboard-submissions")

urlpatterns = [
    path("", include(router.urls)),
]
