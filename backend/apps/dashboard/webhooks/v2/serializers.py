"""
Dashboard webhooks serializers.
"""
from rest_framework import serializers
from apps.webhooks.models import Webhook, WebhookDelivery


class WebhookDashboardSerializer(serializers.ModelSerializer):
    """Serializer for Webhook model in dashboard context"""
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Webhook
        fields = [
            'id', 'store', 'name', 'description', 'url', 'method',
            'secret', 'verify_ssl', 'events', 'event_filter', 'headers',
            'is_active', 'last_triggered_at', 'created_by', 'created_by_email',
            'status_display', 'max_retries', 'retry_delay', 'retry_backoff_multiplier',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'created_by_email', 'created_at', 'updated_at',
            'last_triggered_at', 'status_display'
        ]


class WebhookCreateDashboardSerializer(serializers.ModelSerializer):
    """Webhook creation serializer in dashboard context"""
    
    class Meta:
        model = Webhook
        fields = ['name', 'description', 'url', 'method', 'verify_ssl', 'events', 'event_filter', 'headers']


class WebhookDeliveryDashboardSerializer(serializers.ModelSerializer):
    """Serializer for WebhookDelivery model in dashboard context"""
    webhook = WebhookDashboardSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = WebhookDelivery
        fields = [
            'id', 'store', 'webhook', 'event_type', 'event_id',
            'payload', 'status', 'status_display', 'response_status', 'response_body',
            'response_headers', 'attempt_number', 'next_retry_at',
            'triggered_at', 'delivered_at', 'duration_ms',
            'error_message', 'error_code'
        ]
        read_only_fields = ['id', 'triggered_at', 'delivered_at', 'status_display']
