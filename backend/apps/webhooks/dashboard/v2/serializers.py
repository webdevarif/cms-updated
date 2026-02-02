"""
Dashboard webhooks serializers.
"""

from apps.webhooks.models import Webhook, WebhookDelivery
from rest_framework import serializers


class WebhookDashboardSerializer(serializers.ModelSerializer):
    """Dashboard webhook serializer with full admin access"""

    delivery_count = serializers.SerializerMethodField()
    last_triggered_at = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()

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
            "success_rate",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "delivery_count",
            "last_triggered_at",
            "success_rate",
        ]

    def get_delivery_count(self, obj):
        """Get total delivery count"""
        return obj.deliveries.count()

    def get_last_triggered_at(self, obj):
        """Get last triggered timestamp"""
        last_delivery = obj.deliveries.order_by("-created_at").first()
        return last_delivery.created_at if last_delivery else None

    def get_success_rate(self, obj):
        """Calculate success rate"""
        total = obj.deliveries.count()
        if total == 0:
            return 0
        successful = obj.deliveries.filter(status="success").count()
        return round((successful / total) * 100, 2)


class WebhookDeliveryDashboardSerializer(serializers.ModelSerializer):
    """Dashboard webhook delivery serializer"""

    webhook_name = serializers.CharField(source="webhook.name", read_only=True)
    webhook_url = serializers.CharField(source="webhook.url", read_only=True)

    class Meta:
        model = WebhookDelivery
        fields = [
            "id",
            "webhook",
            "webhook_name",
            "webhook_url",
            "event_type",
            "payload",
            "status",
            "response_status",
            "response_body",
            "error_message",
            "attempt_number",
            "triggered_at",
            "delivered_at",
            "duration_ms",
        ]
        read_only_fields = ["id"]
