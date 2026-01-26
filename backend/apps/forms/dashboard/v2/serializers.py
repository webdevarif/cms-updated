"""
Dashboard form serializers with admin-level access.
"""
from rest_framework import serializers
from apps.forms.models.forms import FormTemplate
from apps.forms.models.submissions import FormSubmission, FormSubmissionData


class DashboardFormTemplateSerializer(serializers.ModelSerializer):
    """Serializer for dashboard form templates with admin access"""
    form_id = serializers.CharField(read_only=True)
    submission_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = FormTemplate
        fields = [
            'id', 'store', 'title', 'slug', 'description', 'form_id', 'fields', 'settings',
            'status', 'is_active', 'save_to_database', 'send_email_notifications',
            'seo_title', 'seo_description', 'created_by', 'created_at', 'updated_at', 
            'submission_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'form_id', 'submission_count']

    def get_submission_count(self, obj):
        """Get total submission count"""
        return obj.submissions.count()


class DashboardFormSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for dashboard form submissions with admin access"""
    form_template_title = serializers.CharField(source='form_template.title', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    data = serializers.SerializerMethodField()
    
    class Meta:
        model = FormSubmission
        fields = [
            'id', 'form_template', 'form_template_title', 'submission_id', 'user', 
            'username', 'user_email', 'ip_address', 'user_agent', 'status', 
            'submitted_at', 'processed_at', 'error_message', 'metadata', 'data'
        ]
        read_only_fields = ['id', 'submission_id', 'submitted_at', 'processed_at']
    
    def get_data(self, obj):
        """Get submission data as dictionary"""
        return {
            item.field_name: item.field_value 
            for item in obj.data.all()
        }
