"""
Serializers for metafields module.
"""
from rest_framework import serializers
from ..models import MetafieldDefinition, Metafield


class MetafieldDefinitionSerializer(serializers.ModelSerializer):
    """Serializer for MetafieldDefinition"""
    
    class Meta:
        model = MetafieldDefinition
        fields = [
            'id', 'store', 'name', 'namespace', 'key', 'type',
            'is_required', 'is_visible', 'is_filterable', 'is_sortable',
            'options', 'ui', 'content_types'
        ]
        read_only_fields = ['id', 'store']


class MetafieldSerializer(serializers.ModelSerializer):
    """Serializer for Metafield"""
    definition = MetafieldDefinitionSerializer(read_only=True)
    
    class Meta:
        model = Metafield
        fields = [
            'id', 'definition', 'content_type', 'object_id',
            'value_text', 'value_number', 'value_boolean',
            'value_date', 'value_json', 'value_media',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
