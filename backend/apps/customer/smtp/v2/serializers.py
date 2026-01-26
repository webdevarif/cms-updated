"""
Customer SMTP serializers.
"""
from rest_framework import serializers
from apps.smtp.models import SmtpConfiguration, EmailTemplate, EmailLog


class SmtpCustomerSerializer(serializers.ModelSerializer):
    """Serializer for SmtpConfiguration model in customer context"""
    
    class Meta:
        model = SmtpConfiguration
        fields = [
            'id', 'name', 'provider', 'host', 'port', 'username',
            'use_tls', 'use_ssl', 'daily_limit', 'hourly_limit', 'is_active',
            'last_used_at', 'last_tested_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_used_at', 'last_tested_at'
        ]


class EmailTemplateCustomerSerializer(serializers.ModelSerializer):
    """Serializer for EmailTemplate model in customer context"""
    
    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'template_type', 'subject', 'html_content',
            'text_content', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmailLogCustomerSerializer(serializers.ModelSerializer):
    """Serializer for EmailLog model in customer context"""
    
    class Meta:
        model = EmailLog
        fields = [
            'id', 'to_email', 'subject', 'status', 'tracking_id', 'message_id',
            'is_tracked', 'sent_at', 'delivered_at', 'opened_at', 'clicked_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
