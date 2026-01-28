"""
User preferences model for Digital Farmers CMS.

Stores user-specific preferences and settings.
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserPreferences(models.Model):
    """User preferences and settings"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="preferences",
        verbose_name=_("user"),
    )

    # Notification preferences
    email_notifications = models.BooleanField(_("email notifications"), default=True)
    push_notifications = models.BooleanField(_("push notifications"), default=True)

    # UI preferences
    theme = models.CharField(
        _("theme"),
        max_length=20,
        default="light",
        choices=[("light", _("Light")), ("dark", _("Dark"))],
    )
    language = models.CharField(
        _("language"), max_length=10, default="en", choices=settings.LANGUAGES
    )

    # Privacy settings
    show_email = models.BooleanField(_("show email"), default=False)
    show_online_status = models.BooleanField(_("show online status"), default=True)

    # Timestamps
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        db_table = "accounts_user_preferences"
        verbose_name = _("user preferences")
        verbose_name_plural = _("user preferences")

    def __str__(self):
        return f"Preferences for {self.user.email}"
