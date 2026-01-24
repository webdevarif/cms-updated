"""
Serializers for SMTP app.
"""
from rest_framework import serializers
from .models import SmtpConfiguration, EmailTemplate, EmailLog


class SmtpConfigSerializer(serializers.ModelSerializer):
    """Serializer for SmtpConfiguration"""
    
    class Meta:
        model = SmtpConfiguration
        fields = [
            'id', 'name', 'provider', 'host', 'port', 'username', 'password',
            'use_tls', 'use_ssl', 'is_default', 'is_verified', 'last_tested',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class EmailTemplateSerializer(serializers.ModelSerializer):
    """Serializer for EmailTemplate"""
    
    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'template_type', 'subject', 'html_content',
            'text_content', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class EmailLogSerializer(serializers.ModelSerializer):
    """Serializer for EmailLog"""
    
    class Meta:
        model = EmailLog
        fields = [
            'id', 'to_email', 'subject', 'status', 'tracking_id', 'message_id',
            'is_tracked', 'sent_at', 'delivered_at', 'opened_at', 'clicked_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
