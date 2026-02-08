"""
URL configuration for webhooks customer API v2.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import WebhookCustomerViewSet, WebhookDeliveryCustomerViewSet

# Customer router
router = DefaultRouter()
router.register(r"webhooks", WebhookCustomerViewSet, basename="customer-webhooks")
router.register(
    r"deliveries",
    WebhookDeliveryCustomerViewSet,
    basename="customer-webhook-deliveries",
)

urlpatterns = [
    path("", include(router.urls)),
]
