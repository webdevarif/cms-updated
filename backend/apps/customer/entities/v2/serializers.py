"""
Serializers for customer entities API.
"""
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType


class EntityActionSerializer(serializers.Serializer):
    """Serializer for entity action requests"""
    action_slug = serializers.SlugField()
    content_type = serializers.CharField()
    object_id = serializers.IntegerField()


class EntityInteractionSerializer(serializers.Serializer):
    """Serializer for entity interaction responses"""
    id = serializers.IntegerField(read_only=True)
    action = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()
    object_id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    def get_action(self, obj):
        return {
            'id': obj.action.id,
            'name': obj.action.name,
            'slug': obj.action.slug,
            'action_type': obj.action.action_type
        }
    
    def get_user(self, obj):
        if obj.user:
            return {
                'id': obj.user.id,
                'email': obj.user.email
            }
        return None
    
    def get_content_type(self, obj):
        return {
            'model': obj.content_type.model,
            'app_label': obj.content_type.app_label
        }
