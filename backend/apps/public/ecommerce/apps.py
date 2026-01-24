"""
Apps configuration for ecommerce.
"""
from django.apps import AppConfig


class EcommerceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.public.ecommerce'
    verbose_name = 'Ecommerce'
    
    def ready(self):
        """Import signals for automatic translation key creation"""
        from . import signals
