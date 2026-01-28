"""
Theme management services for Digital Farmers CMS.

Shared theme management service.
"""
import logging

from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class ThemeService:
    """Shared theme management service"""

    @staticmethod
    def create_theme(store, name, **extra_fields):
        """
        Centralized theme creation method
        """
        from apps.themes.models import Theme

        return Theme.objects.create(store=store, name=name, **extra_fields)

    @staticmethod
    def get_theme(theme_id=None, **filters):
        """
        Centralized theme retrieval method
        """
        from apps.themes.models import Theme

        if theme_id:
            return Theme.objects.get(id=theme_id, **filters)
        else:
            return Theme.objects.get(**filters)

    @staticmethod
    def get_theme_or_none(theme_id=None, **filters):
        """
        Centralized theme retrieval method (safe)
        """
        from apps.themes.models import Theme

        if theme_id:
            return Theme.objects.filter(id=theme_id, **filters).first()
        else:
            return Theme.objects.filter(**filters).first()

    @staticmethod
    def update_theme(theme, **fields):
        """
        Centralized theme update method
        """
        for field, value in fields.items():
            setattr(theme, field, value)
        theme.save()
        return theme

    @staticmethod
    def delete_theme(theme):
        """
        Centralized theme deletion method
        """
        theme.delete()

    @staticmethod
    def filter_themes(store, **filters):
        """
        Centralized theme filtering method
        """
        from apps.themes.models import Theme

        return Theme.objects.filter(store=store, **filters)

    @staticmethod
    def get_active_theme(store):
        """
        Get active theme for a store
        """
        from apps.themes.models import Theme

        return Theme.objects.filter(store=store, is_active=True).first()
