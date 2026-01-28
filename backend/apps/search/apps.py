"""App configuration for search module."""
from django.apps import AppConfig


class SearchConfig(AppConfig):
    label = "search"
    """App config for search app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.search"
    verbose_name = "Search"
