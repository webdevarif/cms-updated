"""
Apps configuration for mediafile app.
"""
from django.apps import AppConfig


class MediafileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.mediafile'
    verbose_name = 'Media Files'
