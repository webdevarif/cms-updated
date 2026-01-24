from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

class Metafield(models.Model):
    """Stores actual metafield values with generic relations"""
    
    # Store scoping
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    
    # Reference to the definition
    definition = models.ForeignKey(
        'metafields.MetafieldDefinition',
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
    value_date = models.DateField(blank=True, null=True)  # Changed from DateTime to Date
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
        db_table = 'metafields_value'  # Changed from metafields_metafield
        unique_together = [['store', 'definition', 'content_type', 'object_id']]
        indexes = [
            models.Index(fields=['store', 'definition']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['definition', 'value_text']),
            models.Index(fields=['definition', 'value_number']),
            models.Index(fields=['definition', 'value_boolean']),
            models.Index(fields=['definition', 'value_date']),
        ]
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.definition} = {self.get_value()}"
    
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
    
    def clean(self):
        """Validate the metafield against its definition"""
        super().clean()
        
        # Ensure store matches definition
        if self.definition.store_id != self.store_id:
            raise ValidationError("Metafield store must match definition store")
            
        # Validate required fields
        if self.definition.is_required and self.get_value() is None:
            raise ValidationError(f"{self.definition} is required")
            
        # Validate select options
        if self.definition.type in ['select', 'multiselect']:
            value = self.get_value()
            if value is not None:
                if self.definition.type == 'select' and value not in self.definition.options:
                    raise ValidationError(
                        f"Value must be one of: {', '.join(map(str, self.definition.options))}"
                    )
                elif (self.definition.type == 'multiselect' and 
                      not all(v in self.definition.options for v in value)):
                    raise ValidationError(
                        f"All values must be in: {', '.join(map(str, self.definition.options))}"
                    )
