"""
Style class model.
"""
from django.db import models


class StyleClass(models.Model):
    """
    Reusable style classes with light/dark mode support and version-specific overrides.
    """
    theme = models.ForeignKey('themes.Theme', on_delete=models.CASCADE, related_name='style_classes')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    
    # Default CSS properties (base styles)
    default_css = models.JSONField(
        default=dict,
        help_text="Default CSS properties for this style class"
    )
    
    # Light/Dark mode overrides
    light_css = models.JSONField(
        default=dict,
        blank=True,
        help_text="Light mode CSS overrides (merges with default_css)"
    )
    dark_css = models.JSONField(
        default=dict,
        blank=True,
        help_text="Dark mode CSS overrides (merges with default_css)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'themes_style_class'
        unique_together = [['theme', 'slug']]
        ordering = ['name']
    
    def __str__(self):
        return f"{self.theme.name} - {self.name}"
    
    def get_css(self, mode='light'):
        """Get CSS for specific mode"""
        css = self.default_css.copy()
        
        if mode == 'light' and self.light_css:
            css.update(self.light_css)
        elif mode == 'dark' and self.dark_css:
            css.update(self.dark_css)
        
        return css
