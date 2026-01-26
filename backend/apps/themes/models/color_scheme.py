"""
Color scheme model.
"""
from django.db import models


class ColorScheme(models.Model):
    """
    Color scheme with light/dark mode support.
    Each theme can have multiple color schemes.
    """
    theme = models.ForeignKey('themes.Theme', on_delete=models.CASCADE, related_name='color_schemes')
    name = models.CharField(max_length=100)
    key = models.SlugField(max_length=100)
    is_default = models.BooleanField(default=False)
    
    # Light mode colors
    colors = models.JSONField(default=dict, help_text="Light mode colors", blank=True)
    
    # Dark mode colors (optional)
    dark_colors = models.JSONField(default=dict, blank=True, help_text="Dark mode colors")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'themes_color_scheme'
        unique_together = [['theme', 'key']]
        ordering = ['name']
    
    def __str__(self):
        return f"{self.theme.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.colors:
            self.colors = self.get_default_colors('light')
        if not self.dark_colors:
            self.dark_colors = self.get_default_colors('dark')
        super().save(*args, **kwargs)
    
    @staticmethod
    def get_default_colors(mode='light'):
        """Return default color scheme based on mode (light/dark)"""
        if mode == 'light':
            return {
                'primary': '#007bff',
                'secondary': '#6c757d',
                'background': '#ffffff',
                'text': '#212529',
                'border': '#dee2e6',
                'accent': '#007bff'
            }
        else:  # dark mode
            return {
                'primary': '#0d6efd',
                'secondary': '#6c757d',
                'background': '#121212',
                'text': '#ffffff',
                'border': '#495057',
                'accent': '#0d6efd'
            }
