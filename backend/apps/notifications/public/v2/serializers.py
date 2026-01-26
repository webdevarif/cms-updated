"""
Public notifications serializers.
"""
from rest_framework import serializers
from apps.notifications.models import Notification


class NotificationPublicSerializer(serializers.ModelSerializer):
    """Public notification serializer"""
    
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'type', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']
