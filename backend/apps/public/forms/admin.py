"""
Admin configuration for forms module.
"""
from django.contrib import admin
from .models.forms import FormTemplate, EmailTemplate
from .models.submissions import FormSubmission, FormSubmissionData


@admin.register(FormTemplate)
class FormTemplateAdmin(admin.ModelAdmin):
    """Admin for FormTemplate"""
    list_display = ['title', 'form_id', 'status', 'is_active']
    list_filter = ['status', 'is_active']
    search_fields = ['title', 'slug']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    """Admin for FormSubmission"""
    list_display = ['form_template', 'status', 'email_sent', 'submitted_at']
    list_filter = ['status', 'email_sent']
    readonly_fields = ['submitted_at', 'email_sent_at', 'opened_at']


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    """Admin for EmailTemplate"""
    list_display = ['title', 'recipient_type', 'is_active']
    list_filter = ['recipient_type', 'is_active']
