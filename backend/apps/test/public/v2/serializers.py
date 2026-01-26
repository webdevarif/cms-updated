"""
Public test serializers.
"""
from rest_framework import serializers
from apps.webhooks.serializers import BaseWebhookSerializer, BaseWebhookDeliverySerializer


class TestPublicSerializer(serializers.Serializer):
    """Public test serializer"""
    pass


class TestDashboardSerializer(BaseWebhookSerializer):
    """Serializer for Test model in dashboard context"""
    test_count = serializers.IntegerField(read_only=True)
    last_run_at = serializers.DateTimeField(read_only=True)
    last_run_status = serializers.CharField(max_length=20, read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)


class TestResultsSummarySerializer(serializers.Serializer):
    """Serializer for test results summary"""
    total_tests = serializers.IntegerField()
    passed = serializers.IntegerField()
    failed = serializers.IntegerField()
    errors = serializers.ListField(child=serializers.CharField())
    duration_ms = serializers.IntegerField()
    created_at = serializers.DateTimeField(read_only=True)


class TestDeliveryDashboardSerializer(BaseWebhookDeliverySerializer):
    """Serializer for WebhookDelivery model in dashboard context"""
    test_status = serializers.CharField(max_length=20)
    last_tested_at = serializers.DateTimeField(read_only=True)
    error_message = serializers.CharField(allow_blank=True)
    response_code = serializers.IntegerField(allow_null=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
