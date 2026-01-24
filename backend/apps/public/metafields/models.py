"""
Metafields models.
"""
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class MetafieldDefinition(models.Model):
    """Defines the structure and validation for metafields"""
    
    # Core Identification
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
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
    
    # UI Configuration
    ui = models.JSONField(default=dict, help_text="UI configuration")
    
    # Content types this applies to
    content_types = models.JSONField(default=list, help_text="Which models this field applies to")
    
    class Meta:
        app_label = 'metafields'
        db_table = 'metafields_definition'
        unique_together = [['store', 'namespace', 'key']]
        ordering = ['namespace', 'key']
    
    def __str__(self):
        return f"{self.namespace}.{self.key}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            from apps.logs.tasks import log_event_async
            log_event_async.delay({
                'event_type': 'create_metafielddefinition_public_metafields',
                'message': f"Metafield definition created: {self.namespace}.{self.key}",
                'store_id': self.store.id,
                'object_id': self.id,
                'metadata': {
                    'namespace': self.namespace,
                    'key': self.key,
                    'name': self.name,
                    'type': self.type,
                    'is_required': self.is_required
                }
            })


class Metafield(models.Model):
    """Stores actual metafield values with generic relations"""

    # Reference to the definition
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    definition = models.ForeignKey(
        MetafieldDefinition,
        on_delete=models.CASCADE,
        related_name='values'
    )

    # Generic relation to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Value storage (type-specific)
    value_text = models.TextField(blank=True, null=True)
    value_number = models.FloatField(blank=True, null=True)
    value_boolean = models.BooleanField(blank=True, null=True)
    value_date = models.DateTimeField(blank=True, null=True)
    value_json = models.JSONField(blank=True, null=True)

    # Media fields (for image/file types)
    value_media = models.ForeignKey(
        'mediafile.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'metafields'
        db_table = 'metafields_metafield'
        unique_together = [['definition', 'content_type', 'object_id']]
        indexes = [
            models.Index(fields=['store']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.definition} = {self.get_value()}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            from apps.logs.tasks import log_event_async
            log_event_async.delay({
                'event_type': 'create_metafield_public_metafields',
                'message': f"Metafield created: {self.definition.namespace}.{self.definition.key}",
                'store_id': self.store.id,
                'object_id': self.id,
                'metadata': {
                    'definition_key': self.definition.key,
                    'definition_namespace': self.definition.namespace,
                    'content_type': self.content_type.model,
                    'object_id': self.object_id,
                    'type': self.definition.type
                }
            })
    
    def get_value(self):
        """Get the value in the correct type"""
        if self.definition.type in ['image', 'file']:
            return self.value_media
        return getattr(self, f'value_{self.definition.type}', None)
    
    def set_value(self, value):
        """Set the value with type conversion"""
        if self.definition.type in ['image', 'file']:
            self.value_media = value
        else:
            field_name = f'value_{self.definition.type}'
            setattr(self, field_name, value)
            
            # Clear other value fields
            for t in ['text', 'number', 'boolean', 'date', 'json']:
                if t != self.definition.type:
                    setattr(self, f'value_{t}', None)
            self.value_media = None
