"""
Customer SMTP URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'configs', views.SmtpCustomerViewSet, basename='customer-smtp-configs')
router.register(r'templates', views.EmailTemplateCustomerViewSet, basename='customer-smtp-templates')
router.register(r'logs', views.EmailLogCustomerViewSet, basename='customer-smtp-logs')

urlpatterns = router.urls
