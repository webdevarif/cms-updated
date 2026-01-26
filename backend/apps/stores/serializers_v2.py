"""
Shared serializers for stores app.
"""
from rest_framework import serializers
from .models import Store


class BaseStoreSerializer(serializers.ModelSerializer):
    """Base serializer for Store model"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    store_type_display = serializers.CharField(source='get_store_type_display', read_only=True)
    
    class Meta:
        model = Store
        fields = '__all__'
        read_only_fields = ['id', 'owner', 'access_code', 'created_at']


class BaseStoreCreateSerializer(serializers.ModelSerializer):
    """Base store creation serializer"""
    
    class Meta:
        model = Store
        fields = ['name', 'slug', 'description', 'store_type']
    
    def validate_slug(self, value):
        """Validate slug uniqueness"""
        if Store.objects.filter(slug=value).exists():
            raise serializers.ValidationError("Store with this slug already exists.")
        return value


class BaseStorePublicSerializer(serializers.ModelSerializer):
    """Base public store information serializer"""
    
    class Meta:
        model = Store
        fields = [
            'id', 'name', 'slug', 'description', 'logo',
            'domain', 'meta_title', 'meta_description',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BaseStoreSettingsSerializer(serializers.ModelSerializer):
    """Base store settings serializer"""
    
    class Meta:
        model = Store
        fields = [
            'name', 'slug', 'description', 'logo', 'domain', 'meta_title',
            'meta_description', 'status', 'store_type'
        ]
        read_only_fields = ['id', 'created_at']
