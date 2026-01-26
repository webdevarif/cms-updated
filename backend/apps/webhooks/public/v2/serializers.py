"""
Public webhooks serializers.
"""
from rest_framework import serializers


class WebhookPublicSerializer(serializers.Serializer):
    """Public webhook serializer for status endpoint"""
    
    class Meta:
        fields = ['id', 'name', 'is_active', 'url', 'method', 'last_triggered_at']


class WebhookDeliveryPublicSerializer(serializers.Serializer):
    """Public webhook delivery confirmation serializer"""
    
    class Meta:
        fields = ['delivery_id', 'status', 'message', 'webhook_id', 'event_type']


class WebhookStatusSerializer(serializers.Serializer):
    """Webhook status serializer"""
    
    class Meta:
        fields = ['webhook_id', 'name', 'is_active', 'url', 'method', 'last_triggered_at']
