"""
Public webhooks URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'webhooks', views.WebhookPublicViewSet, basename='public-webhooks')

urlpatterns = router.urls
