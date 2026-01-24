"""
Template model.
"""
from django.db import models


class Template(models.Model):
    """
    Defines reusable template components with a specific role in the layout system.
    Templates are body-only by default, with specialized roles for headers and footers.
    """
    theme = models.ForeignKey('themes.Theme', on_delete=models.CASCADE, related_name='templates')
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    
    TEMPLATE_ROLES = [
        ('body', 'Body'),        # Main content (default)
        ('header', 'Header'),    # Header component
        ('footer', 'Footer'),    # Footer component
        ('partial', 'Partial'),  # Reusable partials
        ('section', 'Section'),  # Page sections
    ]
    
    name = models.CharField(max_length=100)
    key = models.SlugField(max_length=100)
    template_role = models.CharField(
        max_length=20,
        choices=TEMPLATE_ROLES,
        default='body',
        help_text="Defines the template's role in the layout system"
    )
    description = models.TextField(blank=True)
    
    # Template content (body-only for header/footer roles)
    content = models.TextField(
        help_text="HTML template with variables (Django template syntax)"
    )
    
    # Advanced customization tab
    custom_css = models.TextField(
        blank=True,
        help_text="Custom CSS for this template"
    )
    custom_js = models.TextField(
        blank=True,
        help_text="Custom JavaScript for this template"
    )
    
    # Version-specific customizations
    version_css = models.JSONField(
        default=dict,
        blank=True,
        help_text="Version-specific CSS (e.g., {'v1': '...', 'v2': '...'})"
    )
    version_js = models.JSONField(
        default=dict,
        blank=True,
        help_text="Version-specific JavaScript (e.g., {'v1': '...', 'v2': '...'})"
    )
    
    # Template metadata
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Default meta title for pages using this template"
    )
    meta_description = models.TextField(
        blank=True,
        help_text="Default meta description for pages using this template"
    )
    meta_keywords = models.CharField(
        max_length=500,
        blank=True,
        help_text="Default meta keywords for pages using this template"
    )
    
    # Template settings
    is_default = models.BooleanField(
        default=False,
        help_text="Default template for this type and role"
    )
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(
        default=False,
        help_text="System templates cannot be deleted"
    )
    
    # Layout association (for body templates)
    layout = models.ForeignKey(
        'themes.Layout',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Default layout for this template (body templates only)",
        related_name='templates_using_this_layout'
    )
    
    # Template variables (for documentation)
    variables = models.JSONField(
        default=dict,
        blank=True,
        help_text="Available variables in this template"
    )
    
    # Template dependencies
    requires = models.JSONField(
        default=list,
        blank=True,
        help_text="Required components or templates"
    )
    
    # Preview settings
    preview_image = models.URLField(
        blank=True,
        help_text="Preview image for template selection"
    )
    preview_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Sample data for template preview"
    )
    
    # Performance settings
    cache_duration = models.PositiveIntegerField(
        default=300,
        help_text="Cache duration in seconds"
    )
    minify_html = models.BooleanField(
        default=False,
        help_text="Minify HTML output"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'themes_template'
        unique_together = [['theme', 'key']]
        ordering = ['template_role', 'name']
        indexes = [
            models.Index(fields=['theme', 'template_role']),
            models.Index(fields=['is_default', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.template_role})"
    
    def get_css_for_version(self, version='default'):
        """
        Get CSS for a specific version
        """
        if version != 'default' and self.version_css.get(version):
            return self.version_css[version]
        return self.custom_css
    
    def get_js_for_version(self, version='default'):
        """
        Get JavaScript for a specific version
        """
        if version != 'default' and self.version_js.get(version):
            return self.version_js[version]
        return self.custom_js
    
    def render_content(self, context=None):
        """
        Render template content with context.
        For header/footer templates, ensures no <html> or <body> tags.
        """
        from django.template import Template as DjangoTemplate
        from django.template import Context as DjangoContext
        
        template_context = {
            'store': self.store,
            'theme': self.theme,
            'template_name': self.name,
            'template_key': self.key,
        }
        
        if context:
            template_context.update(context)
        
        # Render the template
        django_template = DjangoTemplate(self.content)
        return django_template.render(DjangoContext(template_context))
    
    def get_variables_list(self):
        """
        Extract variables from template content
        """
        import re
        variables = set()
        
        # Find Django template variables
        pattern = r'\{\{\s*([^}]+)\s*\}\}'
        matches = re.findall(pattern, self.content)
        
        for match in matches:
            # Clean up the variable name
            var = match.strip().split('.')[0].strip()
            if var and not var.startswith('|') and not var.startswith('if'):
                variables.add(var)
        
        return sorted(list(variables))
    
    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.key:
            from django.utils.text import slugify
            self.key = slugify(self.name)
        
        # Extract variables from content
        if not self.variables:
            self.variables = self.get_variables_list()
        
        super().save(*args, **kwargs)
