"""
Django app configuration for ecommerce app.
"""
from django.apps import AppConfig


class EcommerceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ecommerce"
    verbose_name = "Ecommerce"

    def ready(self):
        """Import signals when app is ready."""
        pass
