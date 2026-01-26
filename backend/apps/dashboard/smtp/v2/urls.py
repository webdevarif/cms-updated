"""
Dashboard SMTP URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'configs', views.SmtpDashboardViewSet, basename='dashboard-smtp-configs')
router.register(r'templates', views.EmailTemplateDashboardViewSet, basename='dashboard-smtp-templates')
router.register(r'logs', views.EmailLogDashboardViewSet, basename='dashboard-smtp-logs')
router.register(r'webhooks', views.EmailWebhookDashboardViewSet, basename='dashboard-smtp-webhooks')

urlpatterns = router.urls
