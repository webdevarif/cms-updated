"""
URL configuration for SMTP API v1.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import configs

app_name = 'smtp_v1'

router = DefaultRouter()
router.register(r'configs', configs.SmtpConfigViewSet, basename='smtp-config')

urlpatterns = [
    path('', include(router.urls)),
]
