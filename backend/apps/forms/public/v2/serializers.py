"""
Serializers for forms module.
"""
from rest_framework import serializers
from apps.forms.models.forms import FormTemplate
from apps.forms.models.submissions import FormSubmission, FormSubmissionData


class FormTemplateSerializer(serializers.ModelSerializer):
    """Serializer for FormTemplate"""
    form_id = serializers.CharField(read_only=True)
    submission_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FormTemplate
        fields = [
            'id', 'store', 'title', 'slug', 'description', 'form_id',
            'fields', 'settings', 'status', 'is_active',
            'save_to_database', 'send_email_notifications',
            'seo_title', 'seo_description',
            'submission_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'submission_count']
    
    def get_submission_count(self, obj):
        """Get total submission count"""
        return obj.submissions.count()


class FormSubmissionDataSerializer(serializers.ModelSerializer):
    """Serializer for FormSubmissionData"""
    
    class Meta:
        model = FormSubmissionData
        fields = ['field_name', 'field_value', 'field_type']


class FormSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for FormSubmission"""
    data = FormSubmissionDataSerializer(many=True, read_only=True)
    
    class Meta:
        model = FormSubmission
        fields = [
            'id', 'form_template', 'submission_id', 'user', 'ip_address',
            'user_agent', 'status', 'submitted_at', 'processed_at',
            'error_message', 'metadata', 'data'
        ]
        read_only_fields = ['id', 'submission_id', 'submitted_at', 'processed_at']
    
    def create(self, validated_data):
        """Create submission with form data"""
        form_data = validated_data.pop('form_data', {})
        submission = FormSubmission.objects.create(**validated_data)
        
        # Create submission data entries
        for field_name, field_value in form_data.items():
            FormSubmissionData.objects.create(
                submission=submission,
                field_name=field_name,
                field_value=field_value,
                field_type=self._get_field_type(form, field_name)
            )
        
        return submission
    
    def _get_field_type(self, form, field_name):
        """Get field type from form configuration"""
        for field in form.fields:
            if field.get('name') == field_name:
                return field.get('type', 'text')
        return 'text'
