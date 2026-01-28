"""
Theme model.
"""
from django.db import models


class Theme(models.Model):
    """
    Main theme model for each store.
    Each store can have multiple themes, but only one active theme.
    """

    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="Default Theme")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "themes_theme"
        ordering = ["-is_active", "name"]
        unique_together = [["store", "name"]]

    def __str__(self):
        return f"{self.store.name} - {self.name}"

    def activate(self):
        """Activate this theme and deactivate others"""
        Theme.objects.filter(store=self.store).update(is_active=False)
        self.is_active = True
        self.save(update_fields=["is_active"])

    def get_active_color_scheme(self):
        """Get the default color scheme for this theme"""
        return self.color_schemes.filter(is_default=True).first()

    def get_color_scheme(self, key=None):
        """Get a specific color scheme by key"""
        if key:
            return self.color_schemes.filter(key=key).first()
        return self.get_active_color_scheme()
