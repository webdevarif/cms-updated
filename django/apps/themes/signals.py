"""
Django signals for themes app.
"""

from apps.stores.models import Store

from django.db.models.signals import post_save
from django.dispatch import receiver

from .services import create_default_theme


@receiver(post_save, sender=Store)
def create_store_theme(sender, instance, created, **kwargs):
    """
    Automatically create a default theme when a new store is created.
    """
    if created:
        create_default_theme(instance)
