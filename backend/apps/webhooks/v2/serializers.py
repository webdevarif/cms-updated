"""
Serializers for webhooks module.
"""
from rest_framework import serializers
from ..models import Webhook, WebhookDelivery


class WebhookSerializer(serializers.ModelSerializer):
    """Serializer for Webhook"""
    
    class Meta:
        model = Webhook
        fields = [
            'id', 'store', 'name', 'description', 'url', 'method',
            'secret', 'verify_ssl', 'events', 'event_filter', 'headers',
            'is_active', 'last_triggered_at',
            'max_retries', 'retry_delay', 'retry_backoff_multiplier',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WebhookDeliverySerializer(serializers.ModelSerializer):
    """Serializer for WebhookDelivery"""
    webhook = WebhookSerializer(read_only=True)
    
    class Meta:
        model = WebhookDelivery
        fields = [
            'id', 'store', 'webhook', 'event_type', 'event_id',
            'payload', 'status', 'response_status', 'response_body',
            'response_headers', 'attempt_number', 'next_retry_at',
            'triggered_at', 'delivered_at', 'duration_ms',
            'error_message', 'error_code'
        ]
        read_only_fields = ['id', 'triggered_at', 'delivered_at']
