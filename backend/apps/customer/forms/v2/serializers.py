"""
Customer form serializers.
"""
from rest_framework import serializers
from apps.public.forms.models.forms import FormTemplate, FormSubmission, EmailTemplate


class CustomerFormTemplateSerializer(serializers.ModelSerializer):
    """Serializer for customer form templates"""
    form_id = serializers.CharField(read_only=True)
    status = serializers.ChoiceField(choices=FormTemplate.STATUS_CHOICES, default='draft')
    
    class Meta:
        model = FormTemplate
        fields = [
            'id', 'title', 'slug', 'description', 'form_id', 'fields', 'settings',
            'status', 'is_active', 'save_to_database', 'send_email_notifications',
            'seo_title', 'seo_description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'form_id']


class CustomerFormSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for customer form submissions"""
    form_template = serializers.PrimaryKeyRelatedField(
        queryset=FormTemplate.objects.all(),
        required=False
    )
    
    class Meta:
        model = FormSubmission
        fields = [
            'id', 'form_template', 'data', 'ip_address', 'user_agent',
            'status', 'email_sent', 'email_opened', 'submitted_at',
            'email_sent_at', 'opened_at'
        ]
        read_only_fields = [
            'id', 'ip_address', 'user_agent', 'status', 'email_sent',
            'email_opened', 'submitted_at', 'email_sent_at', 'opened_at'
        ]


class CustomerEmailTemplateSerializer(serializers.ModelSerializer):
    """Serializer for customer email templates"""
    
    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'title', 'subject', 'body_html', 'body_text', 'headers',
            'variables', 'recipient_type', 'recipient_email',
            'auto_detect_recipient', 'is_active'
        ]
        read_only_fields = ['id']
