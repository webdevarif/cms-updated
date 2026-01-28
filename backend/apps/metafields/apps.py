"""Metafields application configuration."""
from django.apps import AppConfig


class MetafieldsConfig(AppConfig):
    label = "metafields"
    """AppConfig for the shared metafields app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.metafields"
    verbose_name = "Metafields"
