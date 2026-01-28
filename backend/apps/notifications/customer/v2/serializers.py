"""
Customer notification serializers.
"""
from apps.notifications.models import Notification, NotificationPreference
from rest_framework import serializers


class NotificationCustomerSerializer(serializers.ModelSerializer):
    """
    Customer notification serializer.

    Read-only serializer for customer notification consumption.
    """

    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "title",
            "message",
            "status",
            "channels",
            "metadata",
            "created_at",
            "read_at",
            "delivered_at",
        ]
        read_only_fields = fields


class NotificationPreferenceCustomerSerializer(serializers.ModelSerializer):
    """
    Customer notification preference serializer.

    Full serializer for customer preference management.
    """

    class Meta:
        model = NotificationPreference
        fields = [
            "id",
            "notification_type",
            "channel_preferences",
            "digest_enabled",
            "digest_frequency",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
