"""
Dashboard webhooks URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'webhooks', views.WebhookDashboardViewSet, basename='dashboard-webhooks')
router.register(r'deliveries', views.WebhookDeliveryDashboardViewSet, basename='dashboard-webhook-deliveries')

urlpatterns = router.urls
