"""
Customer notifications serializers.
"""
from rest_framework import serializers
from apps.notifications.serializers import BaseNotificationSerializer, BaseNotificationPreferenceSerializer


class NotificationCustomerSerializer(BaseNotificationSerializer):
    """Serializer for Notification model in customer context"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove user field for customer context (user is always current user)
        if 'user' in self.fields:
            del self.fields['user']


class NotificationPreferenceCustomerSerializer(BaseNotificationPreferenceSerializer):
    """Serializer for NotificationPreference model in customer context"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove user field for customer context (user is always current user)
        if 'user' in self.fields:
            del self.fields['user']
    
    def validate(self, data):
        """Ensure user can only manage their own preferences"""
        if self.instance and self.instance.user != self.context['user']:
            raise serializers.ValidationError("You can only manage your own notification preferences")
        return data
