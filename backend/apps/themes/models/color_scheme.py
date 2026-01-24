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
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
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
        base = {
            'background': '#ffffff' if mode == 'light' else '#111827',
            'foreground': '#111827' if mode == 'light' else '#f3f4f6',
            'muted': '#6b7280' if mode == 'light' else '#9ca3af',
            'muted_foreground': '#374151' if mode == 'light' else '#d1d5db',
            
            # Primary colors
            'primary': '#3b82f6',
            'primary_foreground': '#ffffff',
            'primary_hover': '#2563eb',
            
            # Secondary colors
            'secondary': '#f3f4f6' if mode == 'light' else '#1f2937',
            'secondary_foreground': '#111827' if mode == 'light' else '#f9fafb',
            'secondary_hover': '#e5e7eb' if mode == 'light' else '#374151',
            
            # Accent colors
            'accent': '#f59e0b',
            'accent_foreground': '#ffffff',
            'accent_hover': '#d97706',
            
            # Destructive colors
            'destructive': '#ef4444',
            'destructive_foreground': '#ffffff',
            'destructive_hover': '#dc2626',
            
            # Success colors
            'success': '#10b981',
            'success_foreground': '#ffffff',
            'success_hover': '#059669',
            
            # Warning colors
            'warning': '#f59e0b',
            'warning_foreground': '#ffffff',
            'warning_hover': '#d97706',
            
            # Info colors
            'info': '#3b82f6',
            'info_foreground': '#ffffff',
            'info_hover': '#2563eb',
            
            # Border colors
            'border': '#e5e7eb' if mode == 'light' else '#374151',
            'input': '#d1d5db' if mode == 'light' else '#4b5563',
            'ring': '#93c5fd',
            
            # Card colors
            'card': '#ffffff' if mode == 'light' else '#1f2937',
            'card_foreground': '#111827' if mode == 'light' else '#f9fafb',
            
            # Popover colors
            'popover': '#ffffff' if mode == 'light' else '#1f2937',
            'popover_foreground': '#111827' if mode == 'light' else '#f9fafb',
            
            # Tooltip colors
            'tooltip': '#111827' if mode == 'light' else '#f3f4f6',
            'tooltip_foreground': '#f9fafb' if mode == 'light' else '#111827',
            
            # Overlay colors
            'overlay': 'rgba(0, 0, 0, 0.5)',
            
            # Shadow colors
            'shadow': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
            
            # Button variants
            'button_primary': {
                'background': '#3b82f6',
                'foreground': '#ffffff',
                'hover': '#2563eb',
                'border': '#3b82f6',
            },
            'button_secondary': {
                'background': '#f3f4f6' if mode == 'light' else '#374151',
                'foreground': '#111827' if mode == 'light' else '#f9fafb',
                'hover': '#e5e7eb' if mode == 'light' else '#4b5563',
                'border': '#e5e7eb' if mode == 'light' else '#4b5563',
            },
            'button_outline': {
                'background': 'transparent',
                'foreground': '#3b82f6',
                'hover': '#f3f4f6' if mode == 'light' else '#1f2937',
                'border': '#d1d5db',
            },
            'button_ghost': {
                'background': 'transparent',
                'foreground': '#3b82f6',
                'hover': '#f3f4f6' if mode == 'light' else '#1f2937',
                'border': 'transparent',
            },
            'button_link': {
                'background': 'transparent',
                'foreground': '#3b82f6',
                'hover': 'transparent',
                'border': 'transparent',
                'underline': True,
            },
            
            # Form elements
            'input_background': '#ffffff' if mode == 'light' else '#1f2937',
            'input_foreground': '#111827' if mode == 'light' else '#f9fafb',
            'input_placeholder': '#9ca3af',
            'input_border': '#d1d5db',
            'input_ring': '#93c5fd',
            
            # Checkbox/radio
            'checkbox_background': '#ffffff' if mode == 'light' else '#1f2937',
            'checkbox_foreground': '#3b82f6',
            'checkbox_border': '#d1d5db',
            
            # Toggle
            'toggle_background': '#e5e7eb' if mode == 'light' else '#374151',
            'toggle_foreground': '#3b82f6',
            
            # Badge variants
            'badge_primary': {
                'background': '#dbeafe',
                'foreground': '#1e40af',
            },
            'badge_secondary': {
                'background': '#e5e7eb' if mode == 'light' else '#374151',
                'foreground': '#111827' if mode == 'light' else '#f9fafb',
            },
            'badge_destructive': {
                'background': '#fee2e2',
                'foreground': '#b91c1c',
            },
            'badge_outline': {
                'background': 'transparent',
                'foreground': '#111827' if mode == 'light' else '#f9fafb',
                'border': '#e5e7eb' if mode == 'light' else '#374151',
            },
        }
        
        return base
