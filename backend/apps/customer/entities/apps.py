"""
Customer entities app configuration.
"""
from django.apps import AppConfig


class CustomerEntitiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.customer.entities'
    verbose_name = 'Customer Entities'
