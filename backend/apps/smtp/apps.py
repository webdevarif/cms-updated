"""
Apps configuration for SMTP app.
"""
from django.apps import AppConfig


class SmtpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.smtp'
    verbose_name = 'SMTP'
