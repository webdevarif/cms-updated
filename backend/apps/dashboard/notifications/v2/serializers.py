"""
Dashboard notifications serializers.
"""
from apps.notifications.serializers import BaseNotificationSerializer, BaseNotificationPreferenceSerializer


class NotificationDashboardSerializer(BaseNotificationSerializer):
    """Serializer for Notification model in dashboard context"""
    user_email = serializers.EmailField(source='user.email', read_only=True)


class NotificationPreferenceDashboardSerializer(BaseNotificationPreferenceSerializer):
    """Serializer for NotificationPreference model in dashboard context"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
