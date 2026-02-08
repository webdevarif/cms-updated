"""
Dashboard SMTP serializers.
"""

from apps.smtp.models import EmailLog, SMTPConfig
from rest_framework import serializers


class SMTPConfigDashboardSerializer(serializers.ModelSerializer):
    """Dashboard SMTP config serializer"""

    email_count = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()

    class Meta:
        model = SMTPConfig
        fields = [
            "id",
            "name",
            "host",
            "port",
            "username",
            "password",
            "use_ssl",
            "use_tls",
            "is_active",
            "is_default",
            "email_count",
            "success_rate",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "email_count",
            "success_rate",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def get_email_count(self, obj):
        """Get total email count"""
        return obj.email_logs.count()

    def get_success_rate(self, obj):
        """Calculate success rate"""
        total = obj.email_logs.count()
        if total == 0:
            return 0
        successful = obj.email_logs.filter(status="sent").count()
        return round((successful / total) * 100, 2)


class EmailLogDashboardSerializer(serializers.ModelSerializer):
    """Dashboard email log serializer"""

    smtp_config_name = serializers.CharField(source="smtp_config.name", read_only=True)

    class Meta:
        model = EmailLog
        fields = [
            "id",
            "smtp_config",
            "smtp_config_name",
            "to_email",
            "subject",
            "body",
            "status",
            "error_message",
            "sent_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "sent_at"]
