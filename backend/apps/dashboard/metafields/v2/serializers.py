from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from apps.public.metafields.models import MetafieldDefinition, Metafield


class MetafieldDefinitionSerializer(serializers.ModelSerializer):
    """Serializer for metafield definitions"""
    
    class Meta:
        model = MetafieldDefinition
        fields = [
            'id', 'name', 'namespace', 'key', 'type', 'is_required', 
            'is_visible', 'is_filterable', 'is_sortable', 'options',
            'validations', 'content_types', 'ui', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MetafieldSerializer(serializers.ModelSerializer):
    """Serializer for metafield values"""
    
    namespace = serializers.CharField(source='definition.namespace', read_only=True)
    key = serializers.CharField(source='definition.key', read_only=True)
    name = serializers.CharField(source='definition.name', read_only=True)
    type = serializers.CharField(source='definition.type', read_only=True)
    
    class Meta:
        model = Metafield
        fields = [
            'id', 'namespace', 'key', 'name', 'type', 'value_text',
            'value_number', 'value_boolean', 'value_date', 'value_json',
            'value_media', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BulkMetafieldUpdateSerializer(serializers.Serializer):
    """Serializer for bulk updating metafields"""
    
    content_type = serializers.ChoiceField(
        choices=[],  # Will be set in __init__
        help_text="Content type model name (e.g., 'product')"
    )
    object_id = serializers.IntegerField(help_text="Object ID")
    metafields = serializers.DictField(
        child=serializers.JSONField(),
        help_text="Dictionary of metafield values (namespace.key: value)"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set content type choices based on installed apps
        self.fields['content_type'].choices = [
            (ct.model, ct.model)
            for ct in ContentType.objects.all()
            if hasattr(ct.model_class(), 'metafields')
        ]
    
    def validate(self, data):
        """Validate the bulk update data"""
        # Additional validation can be added here
        return data
