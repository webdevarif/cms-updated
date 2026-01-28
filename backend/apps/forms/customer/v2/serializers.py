"""
Customer form serializers.
"""
from apps.forms.models.forms import FormTemplate
from apps.forms.models.submissions import FormSubmission, FormSubmissionData
from rest_framework import serializers


class CustomerFormTemplateSerializer(serializers.ModelSerializer):
    """Serializer for customer form templates"""

    form_id = serializers.CharField(read_only=True)
    status = serializers.ChoiceField(
        choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")],
        default="draft",
    )

    class Meta:
        model = FormTemplate
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "form_id",
            "fields",
            "settings",
            "status",
            "is_active",
            "save_to_database",
            "send_email_notifications",
            "seo_title",
            "seo_description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "form_id"]


class CustomerFormSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for customer form submissions"""

    form_template = serializers.PrimaryKeyRelatedField(
        queryset=FormTemplate.objects.all(), required=False
    )
    data = serializers.SerializerMethodField()

    class Meta:
        model = FormSubmission
        fields = [
            "id",
            "form_template",
            "submission_id",
            "user",
            "ip_address",
            "user_agent",
            "status",
            "submitted_at",
            "processed_at",
            "error_message",
            "metadata",
            "data",
        ]
        read_only_fields = ["id", "submission_id", "submitted_at", "processed_at"]

    def get_data(self, obj):
        """Get submission data as dictionary"""
        return {item.field_name: item.field_value for item in obj.data.all()}
