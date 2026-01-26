"""
Public SMTP serializers.
"""
from rest_framework import serializers


class SmtpPublicSerializer(serializers.Serializer):
    """Serializer for SMTP status in public context"""
    
    class Meta:
        fields = ['status', 'webhooks_enabled']


class EmailWebhookPublicSerializer(serializers.Serializer):
    """Serializer for webhook status in public context"""
    
    class Meta:
        fields = ['status', 'webhooks_enabled']
