"""
Customer webhooks URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'webhooks', views.WebhookCustomerViewSet, basename='customer-webhooks')
router.register(r'deliveries', views.WebhookDeliveryCustomerViewSet, basename='customer-webhook-deliveries')

urlpatterns = router.urls
