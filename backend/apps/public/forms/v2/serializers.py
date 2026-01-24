"""
Serializers for forms module.
"""
from rest_framework import serializers
from ..models.forms import FormTemplate, EmailTemplate
from ..models.submissions import FormSubmission, FormSubmissionData


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
        fields = ['id', 'field_name', 'field_value', 'created_at']
        read_only_fields = ['id', 'created_at']


class FormSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for FormSubmission"""
    form = FormTemplateSerializer(read_only=True)
    form_data = FormSubmissionDataSerializer(source='submission_data', many=True, read_only=True)
    user_info = serializers.SerializerMethodField()
    
    class Meta:
        model = FormSubmission
        fields = [
            'id', 'form', 'user', 'ip_address', 'user_agent',
            'status', 'form_data', 'user_info',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user_info(self, obj):
        """Get user information"""
        if obj.user:
            return {
                'id': obj.user.id,
                'email': obj.user.email,
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name
            }
        return None


class FormSubmissionCreateSerializer(serializers.Serializer):
    """Serializer for creating form submissions"""
    form_data = serializers.JSONField(required=True)
    
    def validate_form_data(self, value):
        """Validate form data structure"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("form_data must be a dictionary")
        return value


class FormCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating forms"""
    
    class Meta:
        model = FormTemplate
        fields = [
            'title', 'slug', 'description', 'fields', 'settings',
            'save_to_database', 'send_email_notifications',
            'seo_title', 'seo_description'
        ]
    
    def validate_fields(self, value):
        """Validate form fields configuration"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("fields must be a dictionary")
        
        # Validate field configurations
        for field_name, field_config in value.items():
            if not isinstance(field_config, dict):
                raise serializers.ValidationError(f"Field '{field_name}' configuration must be a dictionary")
            
            # Check required field properties
            if 'type' not in field_config:
                raise serializers.ValidationError(f"Field '{field_name}' must have a 'type' property")
        
        return value
    
    def validate_settings(self, value):
        """Validate form settings"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("settings must be a dictionary")
        return value
