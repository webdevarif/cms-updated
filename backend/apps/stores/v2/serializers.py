"""
Serializers for stores API v2.
"""
from rest_framework import serializers
from ..models import Store, StoreSettings


class StorePublicSerializer(serializers.ModelSerializer):
    """Public store information"""
    
    class Meta:
        model = Store
        fields = [
            'id', 'name', 'slug', 'description', 'logo',
            'domain', 'meta_title', 'meta_description',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class StoreSerializer(serializers.ModelSerializer):
    """Full store information for owners"""
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    store_type_display = serializers.CharField(source='get_store_type_display', read_only=True)
    
    class Meta:
        model = Store
        fields = '__all__'
        read_only_fields = ['id', 'owner', 'access_code', 'created_at']


class StoreCreateSerializer(serializers.ModelSerializer):
    """Store creation serializer"""
    
    class Meta:
        model = Store
        fields = ['name', 'slug', 'description', 'store_type']
    
    def validate_slug(self, value):
        """Validate slug uniqueness"""
        if Store.objects.filter(slug=value).exists():
            raise serializers.ValidationError("Store with this slug already exists.")
        return value


class StoreSettingsSerializer(serializers.ModelSerializer):
    """Store settings serializer"""
    
    class Meta:
        model = StoreSettings
        fields = '__all__'
