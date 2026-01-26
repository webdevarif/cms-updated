"""
MetafieldDefinition model for metafields app.
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from core.models import TenantModel


class MetafieldDefinition(TenantModel):
    """
    Store-scoped metafield definition for dynamic custom fields.
    """
    
    # Core Identification
    name = models.CharField(max_length=100)
    namespace = models.CharField(max_length=50, help_text="Category for grouping fields")
    key = models.CharField(max_length=50, help_text="Unique identifier within namespace")
    
    # Type and Validation
    TYPE_CHOICES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('boolean', 'True/False'),
        ('date', 'Date'),
        ('url', 'URL'),
        ('json', 'JSON'),
        ('select', 'Dropdown'),
        ('multiselect', 'Multi-select'),
        ('image', 'Image'),
        ('file', 'File'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Configuration
    is_required = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    is_filterable = models.BooleanField(default=False)
    is_sortable = models.BooleanField(default=False)
    
    # Options for select fields
    options = models.JSONField(
        default=list,
        help_text="Options for select/multiselect fields"
    )
    
    # Validation rules
    validations = models.JSONField(
        default=dict,
        help_text="Validation rules (min_length, max_length, etc.)"
    )
    
    # Content types this field applies to
    content_types = models.JSONField(
        default=list,
        help_text="Which models this field applies to"
    )
    
    # UI Configuration
    ui = models.JSONField(
        default=dict,
        help_text="UI configuration (placeholder, help text, etc.)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = 'metafields_definition'
        unique_together = [['store', 'namespace', 'key']]
        indexes = [
            models.Index(fields=['namespace', 'key']),
            models.Index(fields=['is_visible']),
            models.Index(fields=['content_types']),
        ]
        ordering = ['namespace', 'key']
    
    def __str__(self):
        return f"{self.namespace}.{self.key}"
    
    def clean(self):
        """Validate the definition"""
        # Validate namespace/key format
        if not self.namespace.islower():
            raise ValidationError("Namespace must be lowercase")
            
        if not self.key.islower():
            raise ValidationError("Key must be lowercase")
            
        # Validate options for select fields
        if self.type in ['select', 'multiselect'] and not self.options:
            raise ValidationError("Select fields must have options defined")
