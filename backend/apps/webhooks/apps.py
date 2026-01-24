"""
Apps configuration for webhooks module.
"""
from django.apps import AppConfig


class WebhooksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.webhooks'
    verbose_name = 'Webhooks'
    
    def ready(self):
        """Import signals for automatic webhook triggering"""
        from . import signals
