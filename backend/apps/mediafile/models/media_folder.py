"""
MediaFolder model for organizing media files.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class MediaFolder(models.Model):
    """
    Represents a folder for organizing media files within a store.
    Supports nested folder structure.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='media_folders')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_folders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('store', 'parent', 'slug')
        ordering = ['name']
        indexes = [
            models.Index(fields=['store']),
            models.Index(fields=['parent']),
            models.Index(fields=['created_at']),
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
