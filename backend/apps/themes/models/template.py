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
    content = models.TextField(help_text="Template content (HTML or JSON)")
    content_type = models.CharField(
        max_length=10,
        choices=[
            ('html', 'HTML'),
            ('json', 'JSON'),
        ],
        default='html'
    )
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'themes_template'
        unique_together = [['theme', 'key']]
        ordering = ['name']
    
    def __str__(self):
        return f"{self.theme.name} - {self.name} ({self.template_role})"
    
    def render(self, context=None):
        """Render template with context"""
        if self.content_type == 'html':
            from django.template import Template as DjangoTemplate
            template = DjangoTemplate(self.content)
            return template.render(context or {})
        else:
            # Handle JSON templates
            import json
            return json.loads(self.content) if self.content else {}
