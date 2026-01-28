"""
Customer webhooks serializers.
"""
from apps.webhooks.models import Webhook, WebhookDelivery
from rest_framework import serializers


class WebhookCustomerSerializer(serializers.ModelSerializer):
    """Customer webhook serializer with full CRUD access"""

    delivery_count = serializers.SerializerMethodField()
    last_triggered_at = serializers.SerializerMethodField()

    class Meta:
        model = Webhook
        fields = [
            "id",
            "name",
            "description",
            "url",
            "method",
            "secret",
            "verify_ssl",
            "event_types",
            "is_active",
            "delivery_count",
            "last_triggered_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "delivery_count", "last_triggered_at"]

    def get_delivery_count(self, obj):
        """Get total delivery count"""
        return obj.deliveries.count()

    def get_last_triggered_at(self, obj):
        """Get last triggered timestamp"""
        last_delivery = obj.deliveries.order_by("-created_at").first()
        return last_delivery.created_at if last_delivery else None


class WebhookDeliveryCustomerSerializer(serializers.ModelSerializer):
    """Customer webhook delivery serializer"""

    webhook_name = serializers.CharField(source="webhook.name", read_only=True)

    class Meta:
        model = WebhookDelivery
        fields = [
            "id",
            "webhook",
            "webhook_name",
            "event_type",
            "payload",
            "status",
            "response_status",
            "response_body",
            "error_message",
            "retry_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
