"""
MediaFolder model for organizing media files.
"""

from core.models import TenantModel

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class MediaFolder(TenantModel):
    """
    Store-scoped folder for organizing media files.
    Supports nested folder structure.
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_folders"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = "mediafiles_media_folder"
        unique_together = ("store", "parent", "slug")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["store"]),
            models.Index(fields=["parent"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        from django.utils.text import slugify

        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def path(self):
        """Get full folder path as string"""
        if self.parent:
            return f"{self.parent.path}/{self.slug}"
        return self.slug
