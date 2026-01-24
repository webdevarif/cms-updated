"""
Serializers for notifications API v2.
"""
from rest_framework import serializers
from ..models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 'user', 'user_email',
            'target_type', 'target_id', 'channels', 'status', 'status_display',
            'delivery_attempts', 'last_attempt_at', 'delivered_at', 'read_at',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_attempt_at',
            'delivered_at', 'read_at', 'delivery_attempts'
        ]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'user_email', 'notification_type', 'channel_preferences',
            'digest_enabled', 'digest_frequency', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
