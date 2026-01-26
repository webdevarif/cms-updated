"""
Dashboard notification serializers.
"""
from rest_framework import serializers
from apps.notifications.models import Notification, NotificationPreference, NotificationTemplate


class NotificationDashboardSerializer(serializers.ModelSerializer):
    """
    Dashboard notification serializer.
    
    Full admin serializer with all fields.
    """
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 'user', 
            'target_type', 'target_id', 'channels', 'status',
            'delivery_attempts', 'last_attempt_at', 'delivered_at', 
            'read_at', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'delivery_attempts', 'last_attempt_at', 
            'delivered_at', 'read_at', 'created_at', 'updated_at'
        ]


class NotificationPreferenceDashboardSerializer(serializers.ModelSerializer):
    """
    Dashboard notification preference serializer.
    
    Full admin serializer with all fields.
    """
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'user_email', 'notification_type', 
            'channel_preferences', 'digest_enabled', 'digest_frequency',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_email', 'created_at', 'updated_at']


class NotificationTemplateDashboardSerializer(serializers.ModelSerializer):
    """
    Dashboard notification template serializer.
    
    Full admin serializer with all fields.
    """
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'notification_type', 'title_template', 
            'message_template', 'email_subject_template', 'email_body_template',
            'push_title_template', 'push_body_template', 'sms_template',
            'variables', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
