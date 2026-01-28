"""
Form submission models for forms app.
"""
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class FormSubmission(models.Model):
    """
    Individual form submission data.
    """

    form_template = models.ForeignKey(
        "forms.FormTemplate", on_delete=models.CASCADE, related_name="submissions"
    )
    store = models.ForeignKey(
        "stores.Store", on_delete=models.CASCADE, related_name="form_submissions"
    )
    submission_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="form_submissions"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
        default="pending",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "forms_form_submissions"
        unique_together = [["store", "submission_id"]]
        indexes = [
            models.Index(fields=["store", "form_template", "status"]),
            models.Index(fields=["form_template", "submission_id"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["submitted_at"]),
        ]
        ordering = ["-submitted_at"]
        app_label = "forms"

    def __str__(self):
        return f"{self.submission_id} - {self.form_template.title}"

    @property
    def is_processed(self):
        """Check if submission has been processed."""
        return self.status in ["completed", "failed"]


class FormSubmissionData(models.Model):
    """
    Individual field data for form submissions.
    """

    submission = models.ForeignKey(
        "forms.FormSubmission", on_delete=models.CASCADE, related_name="data"
    )
    field_name = models.CharField(max_length=255)
    field_value = models.TextField()
    field_type = models.CharField(max_length=50)
    field_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "forms_form_submission_data"
        indexes = [
            models.Index(fields=["submission", "field_order"]),
        ]
        ordering = ["field_order"]
        app_label = "forms"

    def __str__(self):
        return f"{self.field_name}: {self.field_value[:50]}..."
