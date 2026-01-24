"""
Apps configuration for metafields module.
"""
from django.apps import AppConfig


class MetafieldsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.public.metafields'
    verbose_name = 'Metafields'
