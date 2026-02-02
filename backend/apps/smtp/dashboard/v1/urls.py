"""
URL configuration for SMTP dashboard API v2.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EmailLogDashboardViewSet, SMTPConfigDashboardViewSet

# Dashboard router
router = DefaultRouter()
router.register(r"smtp-configs", SMTPConfigDashboardViewSet, basename="dashboard-smtp-configs")
router.register(r"email-logs", EmailLogDashboardViewSet, basename="dashboard-email-logs")

urlpatterns = [
    path("", include(router.urls)),
]
