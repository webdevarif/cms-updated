"""
Style class model.
"""
from django.db import models


class StyleClass(models.Model):
    """
    Reusable style classes with light/dark mode support and version-specific overrides.
    """
    theme = models.ForeignKey('themes.Theme', on_delete=models.CASCADE, related_name='style_classes')
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
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
    
    # Version-specific overrides (for different template versions)
    version_css = models.JSONField(
        default=dict,
        blank=True,
        help_text="Version-specific CSS overrides (e.g., {'v1': {...}, 'v2': {...}})"
    )
    
    # Media queries for responsive design
    media_queries = models.JSONField(
        default=dict,
        blank=True,
        help_text="Responsive styles (e.g., {'sm': {...}, 'md': {...}, 'lg': {...}})"
    )
    
    # Pseudo-class styles
    pseudo_classes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Pseudo-class styles (e.g., {'hover': {...}, 'focus': {...}, 'active': {...}})"
    )
    
    # Animation properties
    animations = models.JSONField(
        default=dict,
        blank=True,
        help_text="Animation properties (e.g., {'transition': 'all 0.3s ease', 'animation': 'fadeIn 0.5s'})"
    )
    
    # Custom CSS (raw CSS for complex styles)
    custom_css = models.TextField(
        blank=True,
        help_text="Raw CSS for complex styles that can't be expressed in JSON"
    )
    
    # Version-specific custom CSS
    version_custom_css = models.JSONField(
        default=dict,
        blank=True,
        help_text="Version-specific raw CSS (e.g., {'v1': '...', 'v2': '...'})"
    )
    
    # CSS variables for this class
    css_variables = models.JSONField(
        default=dict,
        blank=True,
        help_text="CSS variables specific to this class"
    )
    
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False, help_text="System style classes cannot be deleted")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'themes_style_class'
        unique_together = [['theme', 'slug']]
        ordering = ['name']
    
    def __str__(self):
        return f"{self.theme.name} - {self.name}"
    
    def get_css_for_version(self, version='default', mode='light'):
        """
        Get CSS properties for a specific version and mode
        """
        # Start with default CSS
        css = self.default_css.copy()
        
        # Apply mode-specific overrides
        if mode == 'dark' and self.dark_css:
            css.update(self.dark_css)
        elif mode == 'light' and self.light_css:
            css.update(self.light_css)
        
        # Apply version-specific overrides
        if version != 'default' and self.version_css.get(version):
            css.update(self.version_css[version])
        
        return css
    
    def get_custom_css_for_version(self, version='default'):
        """
        Get custom CSS for a specific version
        """
        if version != 'default' and self.version_custom_css.get(version):
            return self.version_custom_css[version]
        return self.custom_css
    
    def get_media_query_css(self, version='default', mode='light'):
        """
        Get media query CSS for responsive design
        """
        result = {}
        for breakpoint, styles in self.media_queries.items():
            # Apply version and mode overrides to media query styles
            css = styles.copy()
            if mode == 'dark' and self.dark_css:
                css.update(self.dark_css)
            if version != 'default' and self.version_css.get(version):
                css.update(self.version_css[version])
            result[breakpoint] = css
        return result
    
    def get_pseudo_class_css(self, pseudo_class, version='default', mode='light'):
        """
        Get pseudo-class CSS (hover, focus, active, etc.)
        """
        css = self.pseudo_classes.get(pseudo_class, {}).copy()
        
        # Apply mode-specific overrides
        if mode == 'dark' and self.dark_css:
            css.update(self.dark_css)
        elif mode == 'light' and self.light_css:
            css.update(self.light_css)
        
        # Apply version-specific overrides
        if version != 'default' and self.version_css.get(version):
            css.update(self.version_css[version])
        
        return css
    
    def generate_css_class(self, version='default', mode='light'):
        """
        Generate complete CSS class with all properties
        """
        css_rules = []
        
        # Main class
        main_css = self.get_css_for_version(version, mode)
        if main_css:
            main_props = '; '.join([f"{k}: {v}" for k, v in main_css.items()])
            css_rules.append(f".{self.slug} {{ {main_props}; }}")
        
        # Media queries
        media_css = self.get_media_query_css(version, mode)
        for breakpoint, styles in media_css.items():
            if styles:
                props = '; '.join([f"{k}: {v}" for k, v in styles.items()])
                css_rules.append(f"@media (min-width: {breakpoint}) {{ .{self.slug} {{ {props}; }} }}")
        
        # Pseudo-classes
        for pseudo in ['hover', 'focus', 'active', 'disabled']:
            pseudo_css = self.get_pseudo_class_css(pseudo, version, mode)
            if pseudo_css:
                props = '; '.join([f"{k}: {v}" for k, v in pseudo_css.items()])
                css_rules.append(f".{self.slug}:{pseudo} {{ {props}; }}")
        
        # Custom CSS
        custom_css = self.get_custom_css_for_version(version)
        if custom_css:
            css_rules.append(custom_css)
        
        # CSS variables
        if self.css_variables:
            var_props = '; '.join([f"{k}: {v}" for k, v in self.css_variables.items()])
            css_rules.append(f".{self.slug} {{ {var_props}; }}")
        
        return '\n'.join(css_rules)
    
    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
