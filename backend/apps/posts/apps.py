"""
Apps configuration for posts app.
"""
from django.apps import AppConfig


class PostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.posts'
    verbose_name = 'Posts'
    
    def ready(self):
        """Import signals for automatic translation key creation"""
        from . import signals
