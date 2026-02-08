"""
URL configuration for webhooks dashboard API v2.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import WebhookDashboardViewSet, WebhookDeliveryDashboardViewSet

# Dashboard router
router = DefaultRouter()
router.register(r"webhooks", WebhookDashboardViewSet, basename="dashboard-webhooks")
router.register(
    r"deliveries",
    WebhookDeliveryDashboardViewSet,
    basename="dashboard-webhook-deliveries",
)

urlpatterns = [
    path("", include(router.urls)),
]
