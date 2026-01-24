from django.db import models
from django.core.exceptions import ValidationError

class MetafieldDefinition(models.Model):
    """Defines the structure and validation for metafields"""
    
    # Store scoping
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    
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
    options = models.JSONField(default=list, blank=True)
    validations = models.JSONField(default=dict, blank=True)
    
    # Content types this applies to
    content_types = models.JSONField(
        default=list,
        help_text="Which models this field applies to"
    )
    
    # UI Configuration
    ui = models.JSONField(
        default=dict,
        help_text="UI configuration (placeholder, help text, etc.)"
    )
    
    class Meta:
        db_table = 'metafields_definition'
        unique_together = [['store', 'namespace', 'key']]
        indexes = [
            models.Index(fields=['store', 'namespace']),
            models.Index(fields=['store', 'type']),
            models.Index(fields=['namespace', 'key']),
            models.Index(fields=['is_visible']),
        ]
        ordering = ['store', 'namespace', 'key']
    
    def __str__(self):
        return f"{self.namespace}.{self.key}"
    
    def clean(self):
        """Validate the definition"""
        super().clean()
        
        # Validate namespace/key format
        if not self.namespace.islower() or not self.namespace.replace('_', '').isalnum():
            raise ValidationError("Namespace must be lowercase alphanumeric with underscores")
            
        if not self.key.islower() or not self.key.replace('_', '').isalnum():
            raise ValidationError("Key must be lowercase alphanumeric with underscores")
            
        # Validate options for select fields
        if self.type in ['select', 'multiselect'] and not self.options:
            raise ValidationError("Select fields must have options defined")
            
        if self.type in ['select', 'multiselect'] and not all(
            isinstance(opt, (str, int, float)) for opt in self.options
        ):
            raise ValidationError("Select options must be strings or numbers")
