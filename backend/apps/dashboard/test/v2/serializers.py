"""
Dashboard test serializers.
"""
from rest_framework import serializers
from apps.webhooks.models import Webhook, WebhookDelivery


class TestDashboardSerializer(serializers.ModelSerializer):
    """Test results serializer"""
    webhook_id = serializers.CharField(source='webhook.id', read_only=True)
    webhook_name = serializers.CharField(source='webhook.name', read_only=True)
    status = serializers.CharField(source='status', read_only=True)
    error = serializers.CharField(source='error', read_only=True)
    message = serializers.CharField(source='message', read_only=True)
    
    class Meta:
        model = WebhookDelivery
        fields = [
            'webhook_id', 'webhook_name', 'status', 'error', 'message'
        ]
        read_only_fields = ['webhook_id', 'webhook_name', 'status', 'error', 'message']


class TestResultsSummarySerializer(serializers.Serializer):
    """Test results summary serializer"""
    total_tests = serializers.IntegerField()
    passed = serializers.IntegerField()
    failed = serializers.IntegerField()
    
    class Meta:
        fields = ['total_tests', 'passed', 'failed']


class TestDeliveryDashboardSerializer(serializers.ModelSerializer):
    """Test delivery serializer"""
    webhook_name = serializers.CharField(source='webhook.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = WebhookDelivery
        fields = [
            'id', 'webhook', 'webhook_name', 'event_type', 'event_id',
            'payload', 'status', 'status_display', 'response_status', 'response_body',
            'response_headers', 'attempt_number', 'triggered_at', 'delivered_at', 'duration_ms',
            'error_message', 'error_code'
        ]
        read_only_fields = ['id', 'triggered_at', 'delivered_at', 'status_display']
