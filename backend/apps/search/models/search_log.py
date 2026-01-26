"""Placeholder models for search app."""
from django.conf import settings
from django.db import models


class SearchLog(models.Model):
    """Minimal search log entry for future analytics."""

    query = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="search_logs",
    )
    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="search_logs",
    )
    results_count = models.PositiveIntegerField(default=0)
    success = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.query} ({self.results_count} results)"
