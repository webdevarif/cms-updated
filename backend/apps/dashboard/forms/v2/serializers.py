"""
Dashboard form serializers with admin-level access.
"""
from rest_framework import serializers
from apps.public.forms.models.forms import FormTemplate, EmailTemplate
from apps.public.forms.models.submissions import FormSubmission, FormSubmissionData


class DashboardFormTemplateSerializer(serializers.ModelSerializer):
    """Serializer for dashboard form templates with admin access"""
    form_id = serializers.CharField(read_only=True)
    submission_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = FormTemplate
        fields = [
            'id', 'title', 'slug', 'description', 'form_id', 'fields', 'settings',
            'status', 'is_active', 'save_to_database', 'send_email_notifications',
            'seo_title', 'seo_description', 'created_at', 'updated_at', 
            'submission_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'form_id', 'submission_count']


class DashboardFormSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for dashboard form submissions with admin access"""
    form_template_title = serializers.CharField(source='form_template.title', read_only=True)
    
    class Meta:
        model = FormSubmission
        fields = [
            'id', 'form_template', 'form_template_title', 'data', 'ip_address', 
            'user_agent', 'status', 'email_sent', 'email_opened', 'submitted_at',
            'email_sent_at', 'opened_at'
        ]
        read_only_fields = [
            'id', 'ip_address', 'user_agent', 'status', 'email_sent',
            'email_opened', 'submitted_at', 'email_sent_at', 'opened_at'
        ]


class DashboardEmailTemplateSerializer(serializers.ModelSerializer):
    """Serializer for dashboard email templates with admin access"""
    
    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'title', 'subject', 'body_html', 'body_text', 'headers',
            'variables', 'recipient_type', 'recipient_email',
            'auto_detect_recipient', 'is_active'
        ]
        read_only_fields = ['id']
