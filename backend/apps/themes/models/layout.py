"""
Layout model.
"""
from django.db import models


class Layout(models.Model):
    """
    Defines global structure including header, footer, and content slots.
    Each theme can have multiple layouts, with one default layout.
    """
    theme = models.ForeignKey('themes.Theme', on_delete=models.CASCADE, related_name='layouts')
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    key = models.SlugField(max_length=100)
    description = models.TextField(blank=True)

    # Header & footer templates
    header_template = models.ForeignKey(
        'themes.Template',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_as_header'
    )
    footer_template = models.ForeignKey(
        'themes.Template',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_as_footer'
    )

    # Layout settings
    is_default = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Content slots (for dynamic content injection)
    content_slots = models.JSONField(
        default=dict,
        blank=True,
        help_text="Defines content slots and their default content"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'themes_layout'
        unique_together = [['theme', 'key']]
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.theme.name})"

    def clean(self):
        # Ensure only one default layout per theme
        if self.is_default and self.theme:
            Layout.objects.filter(
                theme=self.theme, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
