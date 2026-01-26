"""
URL configuration for smtp public API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SmtpPublicViewSet, SmtpDashboardViewSet, EmailTemplateDashboardViewSet, EmailLogDashboardViewSet

# Public router for smtp
public_router = DefaultRouter()
public_router.register(r'smtp', SmtpPublicViewSet, basename='public-smtp')

# Dashboard router for smtp
dashboard_router = DefaultRouter()
dashboard_router.register(r'configs', SmtpDashboardViewSet, basename='dashboard-smtp-configs')
dashboard_router.register(r'templates', EmailTemplateDashboardViewSet, basename='dashboard-smtp-templates')
dashboard_router.register(r'logs', EmailLogDashboardViewSet, basename='dashboard-smtp-logs')

urlpatterns = [
    path('', include(public_router.urls)),
    path('dashboard/', include(dashboard_router.urls)),
]
