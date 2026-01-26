"""
Public SMTP URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'status', views.SmtpPublicViewSet, basename='public-smtp-status')
router.register(r'webhooks', views.EmailWebhookPublicViewSet, basename='public-smtp-webhooks')

urlpatterns = router.urls
