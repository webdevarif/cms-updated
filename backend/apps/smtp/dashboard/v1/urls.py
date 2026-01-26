"""
URL configuration for SMTP dashboard API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SMTPConfigDashboardViewSet, EmailLogDashboardViewSet

# Dashboard router
router = DefaultRouter()
router.register(r'smtp-configs', SMTPConfigDashboardViewSet, basename='dashboard-smtp-configs')
router.register(r'email-logs', EmailLogDashboardViewSet, basename='dashboard-email-logs')

urlpatterns = [
    path('', include(router.urls)),
]
