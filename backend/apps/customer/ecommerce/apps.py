"""
Apps configuration for customer ecommerce.
"""
from django.apps import AppConfig


class CustomerEcommerceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.customer.ecommerce'
    verbose_name = 'Customer Ecommerce'
