"""
Customer webhooks serializers.
"""
from rest_framework import serializers
from apps.webhooks.models import Webhook, WebhookDelivery


class WebhookCustomerSerializer(serializers.ModelSerializer):
    """Serializer for Webhook model in customer context"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Webhook
        fields = [
            'id', 'name', 'description', 'url', 'method',
            'verify_ssl', 'events', 'event_filter', 'headers',
            'is_active', 'last_triggered_at', 'status_display',
            'max_retries', 'retry_delay', 'retry_backoff_multiplier',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_triggered_at', 'status_display'
        ]


class WebhookCreateCustomerSerializer(serializers.ModelSerializer):
    """Webhook creation serializer in customer context"""
    
    class Meta:
        model = Webhook
        fields = ['name', 'description', 'url', 'method', 'verify_ssl', 'events', 'event_filter', 'headers']


class WebhookDeliveryCustomerSerializer(serializers.ModelSerializer):
    """Serializer for WebhookDelivery model in customer context"""
    webhook_name = serializers.CharField(source='webhook.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = WebhookDelivery
        fields = [
            'id', 'webhook', 'webhook_name', 'event_type', 'event_id',
            'payload', 'status', 'status_display', 'response_status',
            'attempt_number', 'triggered_at', 'delivered_at', 'duration_ms',
            'error_message', 'error_code'
        ]
        read_only_fields = ['id', 'triggered_at', 'delivered_at', 'status_display']
