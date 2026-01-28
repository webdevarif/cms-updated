"""
User activity model for Digital Farmers CMS.

Tracks user actions and activities for audit logging.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserActivity(models.Model):
    """User activity log"""

    ACTION_CHOICES = [
        ("login", _("Login")),
        ("logout", _("Logout")),
        ("password_change", _("Password Change")),
        ("profile_update", _("Profile Update")),
        ("role_change", _("Role Change")),
        ("user_created", _("User Created")),
        ("user_deleted", _("User Deleted")),
        ("user_deactivated", _("User Deactivated")),
        ("other", _("Other")),
    ]

    store_user = models.ForeignKey(
        "StoreUser",
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name=_("store user"),
    )
    action = models.CharField(_("action"), max_length=50, choices=ACTION_CHOICES, default="other")
    details = models.JSONField(_("details"), default=dict, blank=True)
    ip_address = models.GenericIPAddressField(_("IP address"), null=True, blank=True)
    user_agent = models.TextField(_("user agent"), blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        db_table = "accounts_user_activity"
        verbose_name = _("user activity")
        verbose_name_plural = _("user activities")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["store_user", "action"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.store_user.user.email} - {self.get_action_display()}"
