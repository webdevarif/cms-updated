"""
Public smtp serializers.
"""
from apps.smtp.serializers import (
    BaseEmailLogSerializer,
    BaseEmailTemplateSerializer,
    BaseSmtpConfigSerializer,
)
from rest_framework import serializers


class SmtpPublicSerializer(serializers.Serializer):
    """Public smtp serializer"""

    pass


class SmtpDashboardSerializer(BaseSmtpConfigSerializer):
    """Serializer for SmtpConfiguration model in dashboard context"""

    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)


class EmailTemplateDashboardSerializer(BaseEmailTemplateSerializer):
    """Serializer for EmailTemplate model in dashboard context"""

    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)


class EmailLogDashboardSerializer(BaseEmailLogSerializer):
    """Serializer for EmailLog model in dashboard context"""

    error_details = serializers.JSONField(default=dict)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
