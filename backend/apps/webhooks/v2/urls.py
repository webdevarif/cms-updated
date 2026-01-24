"""
URL configuration for webhooks API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'webhooks_v2'

router = DefaultRouter()
router.register(r'', views.WebhookViewSet, basename='webhook')
router.register(r'deliveries', views.WebhookDeliveryViewSet, basename='webhook_delivery')

urlpatterns = [
    path('', include(router.urls)),
]
