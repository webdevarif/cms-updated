"""
Metafield model for metafields app.
"""
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from core.models import TenantModel


class Metafield(TenantModel):
    """
    Store-scoped metafield value with generic relations.
    """
    
    # Link to definition
    definition = models.ForeignKey(
        'metafields.MetafieldDefinition',
        on_delete=models.CASCADE,
        related_name='values'
    )
    
    # Generic relation to any model
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Value storage (type-specific)
    value_text = models.TextField(blank=True, null=True)
    value_number = models.FloatField(blank=True, null=True)
    value_boolean = models.BooleanField(blank=True, default=False)
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
    
    class Meta(TenantModel.Meta):
        db_table = 'metafields_value'
        unique_together = [
            ['store', 'definition', 'content_type', 'object_id']
        ]
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['definition', 'value_text']),
            models.Index(fields=['definition', 'value_number']),
        ]
        ordering = ['definition', 'created_at']
    
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
