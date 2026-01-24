"""
Form submission models for dynamic form builder.
"""
from django.db import models
from core.models import TenantModel

# Form submission status choices
SUBMISSION_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('processed', 'Processed'),
    ('sent', 'Sent'),
    ('failed', 'Failed'),
]

class FormSubmission(TenantModel):
    """
    Stores submitted form data with tracking
    """
    
    # Relationships
    form_template = models.ForeignKey(
        'forms.FormTemplate', 
        on_delete=models.CASCADE, 
        related_name='submissions'
    )
    
    # Submission data
    data = models.JSONField(default=dict, help_text="Submitted form data")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Status tracking
    status = models.CharField(
        max_length=20, 
        choices=SUBMISSION_STATUS_CHOICES, 
        default='pending'
    )
    email_sent = models.BooleanField(default=False)
    email_opened = models.BooleanField(default=False)
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'forms_form_submission'
        indexes = [
            models.Index(fields=['form_template', 'status']),
            models.Index(fields=['submitted_at']),
            models.Index(fields=['email_sent']),
        ]
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"Submission for {self.form_template.title} (ID: {self.form_template.form_id})"
    
    def send_notification_emails(self):
        """Trigger async email sending"""
        from ..services import FormService
        FormService.send_form_notifications.delay(self.id)


class FormSubmissionData(TenantModel):
    """
    Individual form submission data field for structured storage
    """
    
    # Relationships
    submission = models.ForeignKey(
        FormSubmission,
        on_delete=models.CASCADE,
        related_name='field_data'
    )
    
    # Field data
    field_name = models.CharField(max_length=255)
    field_value = models.TextField()
    field_type = models.CharField(max_length=50, default='text')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'forms_form_submission_data'
        indexes = [
            models.Index(fields=['submission', 'field_name']),
            models.Index(fields=['field_type']),
        ]
        ordering = ['field_name']
    
    def __str__(self):
        return f"{self.submission.id} - {self.field_name}"
