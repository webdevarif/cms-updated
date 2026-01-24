"""
Serializers for entities API v2.
"""
from rest_framework import serializers
from ..models import EntityAction, EntityInteraction


class EntityActionSerializer(serializers.ModelSerializer):
    """Serializer for EntityAction model"""
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    
    class Meta:
        model = EntityAction
        fields = [
            'id', 'name', 'slug', 'description', 'action_type', 'action_type_display',
            'icon', 'color', 'content_types', 'is_active', 'is_public', 'allow_anonymous',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EntityInteractionSerializer(serializers.ModelSerializer):
    """Serializer for EntityInteraction model"""
    action_name = serializers.CharField(source='action.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = EntityInteraction
        fields = [
            'id', 'action', 'action_name', 'user', 'user_email',
            'content_type', 'object_id', 'value', 'rating', 'is_active',
            'ip_address', 'user_agent', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
