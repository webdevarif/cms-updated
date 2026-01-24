"""
Form models.
"""
from django.db import models
import random
import string
from django.core.validators import RegexValidator
from core.models import TenantModel


class FormTemplate(TenantModel):
    """
    Store-scoped form template for dynamic form builder
    Similar to Shopify's forms with Fluent Form features
    """
    
    # Core fields
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    
    # Form Identification (6-digit unique ID)
    form_id = models.CharField(
        max_length=6, 
        unique=True, 
        db_index=True,
        validators=[RegexValidator(r'^\d{6}$', 'Form ID must be 6 digits')],
        help_text="6-digit unique form identifier for HTML forms"
    )
    
    # Configuration
    fields = models.JSONField(default=dict, help_text="Dynamic form fields configuration")
    settings = models.JSONField(default=dict, help_text="Form settings and options")
    
    # Status and visibility
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_active = models.BooleanField(default=True)
    
    # Submission handling
    save_to_database = models.BooleanField(default=True)
    send_email_notifications = models.BooleanField(default=True)
    
    # SEO and meta
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.CharField(max_length=500, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_forms'
    )
    
    class Meta:
        unique_together = [['store', 'slug']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['store', 'form_id']),
            models.Index(fields=['store', 'status']),
            models.Index(fields=['store', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.form_id})"
    
    def get_absolute_url(self):
        """Get absolute URL for form"""
        return f"/forms/{self.form_id}/"
    
    def get_submission_count(self):
        """Get total submission count"""
        return self.submissions.count()
    
    def get_field_names(self):
        """Get list of field names"""
        return list(self.fields.keys())
    
    def get_required_fields(self):
        """Get list of required field names"""
        return [name for name, config in self.fields.items() 
                if config.get('required', False)]


class EmailTemplate(models.Model):
    """
    Email templates for form notifications
    """
    
    # Store scoping
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='email_templates')
    
    # Template fields
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    
    # Template type
    TEMPLATE_TYPES = [
        ('form_submission', 'Form Submission'),
        ('form_notification', 'Form Notification'),
        ('auto_reply', 'Auto Reply'),
    ]
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, default='form_submission')
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['store', 'template_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"

