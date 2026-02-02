"""
URL configuration for SMTP customer API v2.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EmailLogCustomerViewSet, SMTPConfigCustomerViewSet

# Customer router
router = DefaultRouter()
router.register(r"smtp-configs", SMTPConfigCustomerViewSet, basename="customer-smtp-configs")
router.register(r"email-logs", EmailLogCustomerViewSet, basename="customer-email-logs")

urlpatterns = [
    path("", include(router.urls)),
]
