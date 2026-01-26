"""
FormTemplate model for forms app.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings
from core.models import TenantModel

User = get_user_model()


class FormTemplate(TenantModel):
    """
    Store-scoped form template model for creating reusable form structures.
    """
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    form_id = models.CharField(max_length=50, unique=True, help_text="Unique identifier for the form")
    fields = models.JSONField(default=dict, help_text="Form field definitions")
    settings = models.JSONField(default=dict, help_text="Form settings and configuration")
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('published', 'Published'),
            ('archived', 'Archived')
        ],
        default='draft'
    )
    is_active = models.BooleanField(default=True)
    save_to_database = models.BooleanField(default=True, help_text="Save submissions to database")
    send_email_notifications = models.BooleanField(default=True)
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_forms'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = 'forms_form_template'
        unique_together = [['store', 'slug'], ['store', 'form_id']]
        indexes = [
            models.Index(fields=['store', 'status']),
            models.Index(fields=['store', 'is_active']),
            models.Index(fields=['form_id']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.form_id})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.form_id:
            self.form_id = self.generate_form_id()
        super().save(*args, **kwargs)

    def generate_form_id(self):
        """Generate unique 6-digit form ID"""
        import random
        import string
        while True:
            form_id = ''.join(random.choices(string.ascii_uppercase + string.digits, 6))
            if not FormTemplate.objects.filter(form_id=form_id).exists():
                return form_id

    def get_absolute_url(self):
        return reverse('public-forms-detail', kwargs={'form_id': self.form_id})

    @property
    def submission_count(self):
        """Get total submission count for this form."""
        return self.submissions.count()
