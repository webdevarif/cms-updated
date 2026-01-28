"""
Admin configuration for forms app.
"""
from django.contrib import admin

from .models.forms import FormSubmission, FormSubmissionData, FormTemplate


@admin.register(FormTemplate)
class FormTemplateAdmin(admin.ModelAdmin):
    list_display = ["title", "form_id", "store", "status", "is_active", "created_at"]
    list_filter = ["status", "is_active", "created_at"]
    search_fields = ["title", "description", "form_id"]
    readonly_fields = ["form_id", "submission_count", "created_at", "updated_at"]
    prepopulated_fields = {"slug": "title"}
    date_hierarchy = "created_at"
    raw_id_fields = ["created_by", "form_id"]


@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ["submission_id", "form_template", "user", "status", "submitted_at"]
    list_filter = ["status", "submitted_at", "form_template"]
    search_fields = ["submission_id", "user__email", "ip_address"]
    readonly_fields = ["submission_id", "submitted_at", "processed_at"]
    date_hierarchy = "submitted_at"
    raw_id_fields = ["user", "form_template", "submission_id"]


@admin.register(FormSubmissionData)
class FormSubmissionDataAdmin(admin.ModelAdmin):
    list_display = ["submission", "field_name", "field_type", "field_order"]
    list_filter = ["submission", "field_type"]
    search_fields = ["field_name", "field_value"]
    readonly_fields = ["submission", "field_order"]
