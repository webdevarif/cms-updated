"""
Apps configuration for search module.
"""
from django.apps import AppConfig


class SearchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.public.search'
    verbose_name = 'Search'
    
    def ready(self):
        """Import signal handlers"""
        from . import signals
