"""
Dashboard notification URLs.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

dashboard_router = DefaultRouter()
dashboard_router.register(
    r"notifications", views.NotificationDashboardViewSet, basename="notification-dashboard"
)
dashboard_router.register(
    r"preferences", views.NotificationPreferenceDashboardViewSet, basename="preference-dashboard"
)
dashboard_router.register(
    r"templates", views.NotificationTemplateDashboardViewSet, basename="template-dashboard"
)

urlpatterns = [
    path("", include(dashboard_router.urls)),
]
