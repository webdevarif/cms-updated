"""
Email template models for forms app.
"""
from core.models import TenantModel
from django.db import models
from django.template import Context, Template
from django.template.loader import render_to_string


class EmailTemplate(TenantModel):
    """
    Store-scoped email templates for form notifications.
    """

    # Core fields
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    body_html = models.TextField()
    body_text = models.TextField(blank=True)

    # Configuration
    headers = models.JSONField(default=dict, help_text="Custom email headers")
    variables = models.JSONField(default=dict, help_text="Template variables documentation")

    # Recipients
    RECIPIENT_CHOICES = [
        ("admin", "Form Admin"),
        ("owner", "Form Owner"),
        ("custom", "Custom Email"),
        ("submitter", "Form Submitter"),
    ]
    recipient_type = models.CharField(max_length=20, choices=RECIPIENT_CHOICES, default="admin")
    recipient_email = models.EmailField(blank=True, help_text="Custom recipient email")
    auto_detect_recipient = models.BooleanField(
        default=True, help_text="Auto-detect from form fields"
    )

    # Status
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = "forms_email_template"
        indexes = [
            models.Index(fields=["store", "recipient_type"]),
            models.Index(fields=["is_active"]),
        ]
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.recipient_type})"

    def render_with_context(self, context):
        """Render template with submission data"""
        # Simple variable replacement
        html_content = self.body_html
        text_content = self.body_text

        for key, value in context.items():
            placeholder = f"{{ {key} }}"
            html_content = html_content.replace(placeholder, str(value))
            if text_content:
                text_content = text_content.replace(placeholder, str(value))

        return {
            "html": html_content,
            "text": text_content,
            "subject": self.subject.replace("{{ form_title }}", context.get("form_title", "")),
        }
