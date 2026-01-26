"""
Dashboard SMTP serializers.
"""
from rest_framework import serializers
from apps.smtp.models import SmtpConfiguration, EmailTemplate, EmailLog


class SmtpDashboardSerializer(serializers.ModelSerializer):
    """Serializer for SmtpConfiguration model in dashboard context"""
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    
    class Meta:
        model = SmtpConfiguration
        fields = [
            'id', 'name', 'provider', 'host', 'port', 'username', 'password',
            'use_tls', 'use_ssl', 'daily_limit', 'hourly_limit', 'is_active',
            'last_used_at', 'last_tested_at', 'created_by', 'created_by_email',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'created_by_email', 'created_at', 'updated_at',
            'last_used_at', 'last_tested_at'
        ]


class EmailTemplateDashboardSerializer(serializers.ModelSerializer):
    """Serializer for EmailTemplate model in dashboard context"""
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    
    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'template_type', 'subject', 'html_content',
            'text_content', 'is_active', 'created_by', 'created_by_email',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_by_email', 'created_at', 'updated_at']


class EmailLogDashboardSerializer(serializers.ModelSerializer):
    """Serializer for EmailLog model in dashboard context"""
    
    class Meta:
        model = EmailLog
        fields = [
            'id', 'to_email', 'from_email', 'subject', 'status', 'tracking_id', 'message_id',
            'is_tracked', 'sent_at', 'delivered_at', 'opened_at', 'clicked_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
