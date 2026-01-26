"""
Apps configuration for translations module.
"""
from django.apps import AppConfig


class TranslationsConfig(AppConfig):
    label = 'translations'
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.translations'
    verbose_name = 'Translations'
    
    def ready(self):
        """Import signals for automatic translation key creation"""
        from . import signals
