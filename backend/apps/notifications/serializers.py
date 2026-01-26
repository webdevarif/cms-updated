"""
Shared serializers for notifications app.
"""
from rest_framework import serializers
from .models import Notification, NotificationPreference


class BaseNotificationSerializer(serializers.ModelSerializer):
    """Base serializer for Notification model"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 'user',
            'target_type', 'target_id', 'channels', 'status', 'status_display',
            'delivery_attempts', 'last_attempt_at', 'delivered_at', 'read_at',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_attempt_at',
            'delivered_at', 'read_at', 'delivery_attempts'
        ]


class BaseNotificationPreferenceSerializer(serializers.ModelSerializer):
    """Base serializer for NotificationPreference model"""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'notification_type', 'channel_preferences',
            'digest_enabled', 'digest_frequency', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
