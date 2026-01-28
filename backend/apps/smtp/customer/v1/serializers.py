"""
Customer SMTP serializers.
"""
from apps.smtp.models import EmailLog, SMTPConfig
from rest_framework import serializers


class SMTPConfigCustomerSerializer(serializers.ModelSerializer):
    """Customer SMTP config serializer"""

    email_count = serializers.SerializerMethodField()

    class Meta:
        model = SMTPConfig
        fields = [
            "id",
            "name",
            "host",
            "port",
            "username",
            "use_ssl",
            "use_tls",
            "is_active",
            "is_default",
            "email_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "email_count"]
        extra_kwargs = {"password": {"write_only": True}}

    def get_email_count(self, obj):
        """Get total email count"""
        return obj.email_logs.count()


class EmailLogCustomerSerializer(serializers.ModelSerializer):
    """Customer email log serializer"""

    smtp_config_name = serializers.CharField(source="smtp_config.name", read_only=True)

    class Meta:
        model = EmailLog
        fields = [
            "id",
            "smtp_config",
            "smtp_config_name",
            "to_email",
            "subject",
            "status",
            "error_message",
            "sent_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "sent_at"]
