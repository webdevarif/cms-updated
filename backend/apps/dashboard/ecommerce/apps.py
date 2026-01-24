"""
Apps configuration for dashboard ecommerce.
"""
from django.apps import AppConfig


class DashboardEcommerceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dashboard.ecommerce'
    verbose_name = 'Dashboard Ecommerce'
