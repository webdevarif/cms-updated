# Forms App Rules v1.0

## 🎯 Purpose

This document defines strict development rules for the **forms** app in CMS-Updated backend, implementing a dynamic form builder similar to Shopify's with features inspired by Fluent Form, following the clean V2-only architecture.

---

## 🏗️ Forms App Structure

### **Fixed Directory Structure**
```
apps/
├── public/                    # Public APIs (no authentication)
│   └── forms/               # Public form APIs
│       ├── v2/               # Version 2 (Current Only)
│       │   ├── urls.py
│       │   ├── views.py
│       │   ├── serializers.py
│       │   ├── services.py
│       │   └── tests.py
│       ├── models/             # Shared models across versions
│       │   ├── __init__.py
│       │   ├── forms.py        # FormTemplate, FormField
│       │   ├── submissions.py  # FormSubmission, FormSubmissionData
│       │   └── templates.py    # EmailTemplate
│       ├── admin.py
│       ├── apps.py
│       └── migrations/
├── customer/                  # Customer APIs (customer authentication)
│   └── forms/               # Customer form APIs
│       ├── v2/               # Version 2 (Current Only)
│       │   ├── urls.py
│       │   ├── views.py
│       │   ├── serializers.py
│       │   ├── services.py
│       │   └── tests.py
│       └── models/             # Same shared models
└── dashboard/                 # Dashboard APIs (admin authentication)
    └── forms/               # Dashboard form APIs
        ├── v2/               # Version 2 (Current Only)
        │   ├── urls.py
        │   ├── views.py
        │   ├── serializers.py
        │   ├── services.py
        │   └── tests.py
        └── models/             # Same shared models
```

---

## 📋 Core Models

### **Model Inheritance**
All forms models must inherit from `TenantModel` for store scoping:

```python
from core.models import TenantModel
from django.db import models

class FormTemplate(TenantModel):
    # Store-scoped form template model
    pass
```

### **FormTemplate Model**
```python
# apps/public/forms/models/forms.py
from django.db import models
from core.models import TenantModel
import random
import string

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
        help_text="6-digit unique form identifier for HTML forms"
    )
    
    # Configuration
    fields = models.JSONField(default=dict, help_text="Dynamic form fields configuration")
    settings = models.JSONField(default=dict, help_text="Form settings and options")
    
    # Status and visibility
    status = models.CharField(max_length=20, choices=FORM_STATUS_CHOICES, default='draft')
    is_active = models.BooleanField(default=True)
    
    # Submission handling
    save_to_database = models.BooleanField(default=True)
    send_email_notifications = models.BooleanField(default=True)
    
    # SEO and meta
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.CharField(max_length=500, blank=True)
    
    class Meta:
        db_table = 'forms_form_template'
        unique_together = [['store', 'slug']]
        indexes = [
            models.Index(fields=['store', 'status']),
            models.Index(fields=['store', 'is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['form_id']),  # Add index for form_id lookups
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} (ID: {self.form_id})"
    
    def save(self, *args, **kwargs):
        """Generate 6-digit form_id if not exists"""
        if not self.form_id:
            self.form_id = self.generate_unique_form_id()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_unique_form_id():
        """Generate unique 6-digit form ID"""
        while True:
            # Generate 6-digit alphanumeric ID
            chars = string.ascii_uppercase + string.digits
            form_id = ''.join(random.choices(chars, k=6))
            
            # Check uniqueness
            if not FormTemplate.objects.filter(form_id=form_id).exists():
                return form_id
    
    def get_field_by_name(self, field_name):
        """Get field configuration by name"""
        return self.fields.get(field_name)
    
    def validate_submission_data(self, data):
        """Validate submitted data against field configuration"""
        errors = {}
        
        for field_name, field_config in self.fields.items():
            if field_config.get('required', False) and not data.get(field_name):
                errors[field_name] = f"{field_config.get('label', field_name)} is required"
        
        return errors
    
    def get_html_form_attributes(self):
        """Get HTML form attributes for frontend"""
        return {
            'action': f'/v2/api/public/forms/{self.form_id}/submit/',
            'method': 'POST',
            'enctype': 'multipart/form-data',
            'data-form-id': self.form_id,
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        }
```

### **FormSubmission Model**
```python
# apps/public/forms/models/submissions.py
class FormSubmission(TenantModel):
    """
    Stores submitted form data with tracking
    """
    
    # Relationships
    form_template = models.ForeignKey(FormTemplate, on_delete=models.CASCADE, related_name='submissions')
    
    # Submission data
    data = models.JSONField(default=dict, help_text="Submitted form data")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=SUBMISSION_STATUS_CHOICES, default='pending')
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
        from services.form import FormService
        FormService.send_form_notifications.delay(self.id)
```

### **EmailTemplate Model**
```python
# apps/public/forms/models/templates.py
class EmailTemplate(TenantModel):
    """
    Email templates for form notifications
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
    recipient_type = models.CharField(max_length=20, choices=RECIPIENT_CHOICES, default='admin')
    recipient_email = models.EmailField(blank=True, help_text="Custom recipient email")
    auto_detect_recipient = models.BooleanField(default=True, help_text="Auto-detect from form fields")
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'forms_email_template'
        indexes = [
            models.Index(fields=['store', 'recipient_type']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['title']
    
    def render_with_context(self, context):
        """Render template with submission data"""
        from django.template import Template, Context
        from django.template.loader import render_to_string
        
        # Simple variable replacement
        html_content = self.body_html
        text_content = self.body_text
        
        for key, value in context.items():
            placeholder = f"{{ {key} }}"
            html_content = html_content.replace(placeholder, str(value))
            if text_content:
                text_content = text_content.replace(placeholder, str(value))
        
        return {
            'html': html_content,
            'text': text_content,
            'subject': self.subject.replace('{{ form_title }}', context.get('form_title', ''))
        }
```

---

## 🔌 API Endpoints

### **V2-Only Implementation**
All form endpoints must be V2-only with clean architecture:

#### PublicFormViewSet
```python
# apps/public/forms/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import AllowAny
from drf_spectacular.utils import extend_schema

class PublicFormViewSet(TenantViewSet):
    """
    Public form submission endpoints
    No authentication required
    """
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    queryset = FormTemplate.objects.filter(status='published', is_active=True)
    serializer_class = PublicFormTemplateSerializer
    search_fields = ['title', 'description']
    ordering = ['title']
    
    def get_object(self):
        """Override to lookup by form_id instead of pk"""
        form_id = self.kwargs.get('pk')
        if form_id:
            return get_object_or_404(self.get_queryset(), form_id=form_id)
        return super().get_object()
    
    @extend_schema(
        summary="Get Form by ID",
        description="Get form configuration by 6-digit form ID",
        responses={200: PublicFormTemplateSerializer}
    )
    def retrieve(self, request, pk=None):
        """Get form by 6-digit form_id"""
        form_template = self.get_object()
        serializer = self.get_serializer(form_template)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Submit Form",
        description="Submit form data using 6-digit form ID",
        request=FormSubmissionSerializer,
        responses={201: FormSubmissionSerializer}
    )
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit form data using service layer"""
        form_template = self.get_object()
        
        from services.form import FormService
        try:
            submission = FormService.submit_form(
                form_template, request.data, request
            )
            
            serializer = FormSubmissionSerializer(submission)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
```

#### DashboardFormViewSet
```python
# apps/dashboard/forms/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema

class DashboardFormViewSet(TenantViewSet):
    """
    Form management endpoints for dashboard
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    queryset = FormTemplate.objects.all()
    serializer_class = FormTemplateSerializer
    filterset_fields = ['status', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    @extend_schema(
        summary="Duplicate Form",
        description="Create duplicate of existing form",
        responses={201: FormTemplateSerializer}
    )
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate form template using service layer"""
        form_template = self.get_object()
        
        from services.form import FormService
        new_form = FormService.duplicate_form(form_template, request.user)
        
        serializer = self.get_serializer(new_form)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
```

---

## 🛠️ Services Layer

### **Business Logic Centralization**
All form business logic must be in services.py:

#### FormService
```python
# apps/public/forms/services.py
from django.core.exceptions import ValidationError
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class FormService:
    """Shared form management service"""
    
    @staticmethod
    @transaction.atomic
    def submit_form(form_template, data, request):
        """Process form submission with validation"""
        # Validate submission data
        errors = form_template.validate_submission_data(data)
        if errors:
            raise ValidationError(errors)
        
        # Create submission
        submission = FormSubmission.objects.create(
            form_template=form_template,
            data=data,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            status='pending'
        )
        
        # Log submission
        log_event_async(
            user=request.user if request.user.is_authenticated else None,
            store=form_template.store,
            action='form_submitted',
            object_type='form_submission',
            object_id=submission.id,
            details={
                'form_title': form_template.title,
                'submission_id': submission.id
            }
        )
        
        # Trigger email notifications
        if form_template.send_email_notifications:
            FormService.send_form_notifications.delay(submission.id)
        
        return submission
    
    @staticmethod
    def duplicate_form(form_template, user):
        """Duplicate form template with new slug"""
        from django.utils.text import slugify
        
        new_title = f"{form_template.title} (Copy)"
        new_slug = slugify(new_title)
        
        # Ensure unique slug
        counter = 1
        original_slug = new_slug
        while FormTemplate.objects.filter(store=form_template.store, slug=new_slug).exists():
            new_slug = f"{original_slug}-{counter}"
            counter += 1
        
        new_form = FormTemplate.objects.create(
            store=form_template.store,
            title=new_title,
            slug=new_slug,
            description=form_template.description,
            fields=form_template.fields,
            settings=form_template.settings,
            status='draft',
            created_by=user
        )
        
        # Duplicate email templates
        for email_template in form_template.email_templates.all():
            EmailTemplate.objects.create(
                store=new_form.store,
                form_template=new_form,
                title=email_template.title,
                subject=email_template.subject,
                body_html=email_template.body_html,
                body_text=email_template.body_text,
                headers=email_template.headers,
                variables=email_template.variables,
                recipient_type=email_template.recipient_type,
                recipient_email=email_template.recipient_email,
                auto_detect_recipient=email_template.auto_detect_recipient
            )
        
        log_event_async(
            user=user,
            store=new_form.store,
            action='form_duplicated',
            object_type='form_template',
            object_id=new_form.id,
            details={
                'original_form_id': form_template.id,
                'new_form_title': new_form.title
            }
        )
        
        return new_form
```

---

## 📧 Email Integration

### **SMTP Integration**
All email sending must use smtp.md patterns:

#### Async Email Tasks
```python
# apps/public/forms/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_form_notifications(self, submission_id):
    """Send form notification emails asynchronously"""
    try:
        from .models import FormSubmission
        from services.smtp import SMTPService
        
        submission = FormSubmission.objects.select_related('form_template').get(id=submission_id)
        form_template = submission.form_template
        
        # Get email templates
        email_templates = form_template.email_templates.filter(is_active=True)
        
        for email_template in email_templates:
            # Prepare context
            context = {
                'form_title': form_template.title,
                'submission_data': submission.data,
                'submitted_at': submission.submitted_at,
                'submission_id': submission.id
            }
            
            # Render template
            rendered = email_template.render_with_context(context)
            
            # Determine recipients
            recipients = FormService.get_email_recipients(
                email_template, submission.data, form_template.store
            )
            
            # Send via SMTP service
            SMTPService.send_template_email(
                template_name='form_notification',
                recipients=recipients,
                subject=rendered['subject'],
                html_content=rendered['html'],
                text_content=rendered['text'],
                headers=email_template.headers,
                store=form_template.store
            )
        
        # Update submission status
        submission.email_sent = True
        submission.email_sent_at = timezone.now()
        submission.status = 'sent'
        submission.save(update_fields=['email_sent', 'email_sent_at', 'status'])
        
    except Exception as exc:
        logger.error(f"Failed to send form notifications: {exc}")
        # Update submission status
        submission.status = 'failed'
        submission.save(update_fields=['status'])
        raise self.retry(exc=exc, countdown=60)
```

---

## 🔒 Security Rules

### **Form Security**
- **Input Validation**: All form submissions must be validated against field configuration
- **CSRF Protection**: All form endpoints must have CSRF protection
- **Rate Limiting**: Implement rate limiting on form submission endpoints
- **Spam Protection**: Implement CAPTCHA or honeypot fields
- **Data Sanitization**: Sanitize all user input before storage
- **Privacy**: Store only necessary data, comply with GDPR

### **Email Security**
- **Header Injection**: Prevent email header injection attacks
- **Recipient Validation**: Validate all email recipients
- **Attachment Scanning**: Scan uploaded files for malware
- **Unsubscribe Links**: Include unsubscribe functionality

---

## 📊 Performance Rules

### **Database Optimization**
- **JSONField Indexing**: Use appropriate indexes for JSONField queries
- **Query Optimization**: Use select_related and prefetch_related
- **Bulk Operations**: Use bulk_create for multiple submissions
- **Caching**: Cache form templates and field configurations

### **Email Performance**
- **Async Sending**: All email sending must be asynchronous
- **Queue Management**: Use Celery for email queue management
- **Batch Processing**: Batch multiple emails when possible
- **Retry Logic**: Implement exponential backoff for failed emails

---

## 💰 Cost/Quota Rules

### **Email Quotas**
- **Daily Limits**: Implement daily email sending limits per store
- **Monthly Quotas**: Track monthly email usage
- **Cost Tracking**: Monitor email service costs
- **Overage Handling**: Handle quota exceeded scenarios

### **Storage Costs**
- **Submission Retention**: Define retention policies for form submissions
- **Attachment Limits**: Limit file upload sizes and counts
- **Cleanup Tasks**: Implement periodic cleanup of old data

---

## 🧪 Testing Rules

### **Required Coverage**
- **Models**: 95% code coverage
- **Views**: 90% code coverage  
- **Services**: 100% code coverage
- **Integration**: Critical path testing

### **Test Examples**
```python
# apps/public/forms/tests/test_services.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from ..models import FormTemplate, FormSubmission
from ..services import FormService

class FormServiceTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', slug='test-store')
        self.form_template = FormTemplate.objects.create(
            store=self.store,
            title='Test Form',
            slug='test-form',
            fields={
                'email': {
                    'type': 'email',
                    'label': 'Email',
                    'required': True
                },
                'message': {
                    'type': 'textarea',
                    'label': 'Message',
                    'required': True
                }
            }
        )
    
    def test_submit_form_valid_data(self):
        """Test form submission with valid data"""
        data = {
            'email': 'test@example.com',
            'message': 'Test message'
        }
        
        submission = FormService.submit_form(self.form_template, data, self.request)
        
        self.assertEqual(submission.form_template, self.form_template)
        self.assertEqual(submission.data, data)
        self.assertEqual(submission.status, 'pending')
    
    def test_submit_form_invalid_data(self):
        """Test form submission with invalid data"""
        data = {
            'email': '',  # Required field missing
            'message': 'Test message'
        }
        
        with self.assertRaises(ValidationError):
            FormService.submit_form(self.form_template, data, self.request)
```

### **URL Structure**

#### Main Forms URLs
```python
# apps/public/forms/urls.py
from django.urls import include, path

app_name = 'forms'

urlpatterns = [
    path('v2/', include('apps.public.forms.v2.urls')),
]

# apps/customer/forms/urls.py
urlpatterns = [
    path('v2/', include('apps.customer.forms.v2.urls')),
]

# apps/dashboard/forms/urls.py
urlpatterns = [
    path('v2/', include('apps.dashboard.forms.v2.urls')),
]

# Main project URLs
# config/urls.py
urlpatterns = [
    path('v2/api/public/forms/', include('apps.public.forms.urls')),
    path('v2/api/customer/forms/', include('apps.customer.forms.urls')),
    path('v2/api/dashboard/forms/', include('apps.dashboard.forms.urls')),
]
```

#### Individual App URLs
```python
# apps/public/forms/v2/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PublicFormViewSet

router = DefaultRouter()
router.register(r'', PublicFormViewSet, basename='public-forms')

urlpatterns = [
    path('', include(router.urls)),
]

# apps/customer/forms/v2/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomerFormViewSet

router = DefaultRouter()
router.register(r'submissions', CustomerFormViewSet, basename='customer-forms')

urlpatterns = [
    path('', include(router.urls)),
]

# apps/dashboard/forms/v2/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import (
    DashboardFormViewSet, FormSubmissionViewSet, EmailTemplateViewSet
)

router = DefaultRouter()
router.register(r'forms', DashboardFormViewSet, basename='dashboard-forms')
router.register(r'submissions', FormSubmissionViewSet, basename='dashboard-submissions')
router.register(r'email-templates', EmailTemplateViewSet, basename='dashboard-email-templates')

# Nested routes
forms_router = routers.NestedDefaultRouter(router, r'forms', lookup='form')
forms_router.register(r'submissions', FormSubmissionViewSet, basename='form-submissions')
forms_router.register(r'email-templates', EmailTemplateViewSet, basename='form-email-templates')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(forms_router.urls)),
]
```

---

## � HTML Form Implementation

### **Frontend Integration**
The 6-digit `form_id` makes it easy to identify and submit forms:

```html
<!-- Example HTML form generated from FormTemplate -->
<form action="/v2/api/public/forms/ABC123/submit/" method="POST" enctype="multipart/form-data">
    <input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}">
    <input type="hidden" name="form_id" value="ABC123" data-form-id="ABC123">
    
    <!-- Dynamic fields from form_template.fields JSON -->
    <div class="form-field">
        <label for="email">Email Address *</label>
        <input type="email" id="email" name="email" required>
    </div>
    
    <div class="form-field">
        <label for="message">Message *</label>
        <textarea id="message" name="message" required></textarea>
    </div>
    
    <button type="submit">Submit Form</button>
</form>

<!-- JavaScript for enhanced form handling -->
<script>
document.querySelector('form[data-form-id]').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formId = this.dataset.formId;
    const formData = new FormData(this);
    
    try {
        const response = await fetch(`/v2/api/public/forms/${formId}/submit/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Form submitted successfully!');
            this.reset();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        alert('Submission failed: ' + error.message);
    }
});
</script>
```

### **Form Identification Methods**

1. **URL-based**: `/v2/api/public/forms/{form_id}/submit/`
2. **Hidden Field**: `<input type="hidden" name="form_id" value="ABC123">`
3. **Data Attribute**: `<form data-form-id="ABC123">`
4. **URL Parameter**: `?form_id=ABC123` (alternative method)

---

### **DFCMS Compatibility**
Check for existing form-related models in DFCMS:

```python
# apps/public/forms/migrations/0002_migrate_dfcms_forms.py
def migrate_dfcms_forms(apps, schema_editor):
    """Migrate DFCMS form components if they exist"""
    try:
        # Check if DFCMS has form models
        OldForm = apps.get_model('modules', 'Form')
        OldFormField = apps.get_model('modules', 'FormField')
        
        # Migrate to new FormTemplate structure
        for old_form in OldForm.objects.all():
            form_template = FormTemplate.objects.create(
                store=old_form.store,
                title=old_form.title,
                slug=old_form.slug,
                description=old_form.description,
                fields=migrate_field_configuration(old_form.fields.all()),
                status='published',
                is_active=old_form.is_active
            )
            
            # Migrate email templates
            for old_template in old_form.email_templates.all():
                EmailTemplate.objects.create(
                    store=form_template.store,
                    form_template=form_template,
                    title=old_template.title,
                    subject=old_template.subject,
                    body_html=old_template.body_html,
                    recipient_type=old_template.recipient_type
                )
                
    except LookupError:
        # DFCMS form models don't exist, skip migration
        pass
```

---

## 🔗 Integration Rules

### **Required Integrations**
- **accounts.md**: User authentication and permissions
- **stores.md**: Store scoping and multi-tenancy
- **media.md**: File uploads and attachments
- **smtp.md**: Email sending and tracking
- **translations.md**: Multi-language form support
- **logs.md**: Activity logging and audit trails

### **Integration Examples**
```python
# Integration with media.md for file uploads
class FormField(models.Model):
    # ... other fields ...
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES)
    allow_uploads = models.BooleanField(default=False)
    upload_max_size = models.IntegerField(default=5242880)  # 5MB
    
    def get_upload_media_files(self, submission_data):
        """Get uploaded media files for this field"""
        if self.field_type == 'file' and self.allow_uploads:
            file_ids = submission_data.get(self.name, [])
            return MediaFile.objects.filter(id__in=file_ids, store=self.store)
        return MediaFile.objects.none()

# Integration with translations.md
class FormTemplate(TenantModel):
    # ... other fields ...
    
    def get_translated_field(self, field_name, language_code):
        """Get translated field configuration"""
        from services.translation import TranslationService
        return TranslationService.get_translated_field(
            self.fields.get(field_name, {}), 
            language_code,
            context='form_field'
        )
```

---

## 📈 Improvement Suggestions

### **Enhanced Features**
- **Conditional Logic**: Implement field visibility based on other field values
- **Multi-step Forms**: Support for multi-step form wizards
- **Webhooks**: Add webhook support for real-time form submissions
- **Analytics Dashboard**: Track form conversion rates and submission trends
- **A/B Testing**: Test different form versions for better conversion

### **Security Enhancements**
- **Advanced CAPTCHA**: Implement reCAPTCHA or hCaptcha integration
- **IP Blocking**: Block suspicious IP addresses
- **Rate Limiting**: Implement sophisticated rate limiting algorithms
- **Content Filtering**: Filter spam content using AI/ML

### **Performance Optimizations**
- **CDN Integration**: Serve forms via CDN for better performance
- **Lazy Loading**: Load form fields dynamically as needed
- **Caching Strategy**: Implement intelligent caching for form configurations
- **Database Sharding**: Shard submissions table for high-traffic stores

---

## 🤖 AI Guidelines

### **Allowed Actions**
- **Code Generation**: Generate boilerplate code for form fields and validation
- **Documentation**: Auto-generate API documentation from form configurations
- **Test Cases**: Generate test cases based on form field configurations
- **Migration Scripts**: Generate migration scripts for schema changes
- **Performance Analysis**: Analyze form performance and suggest optimizations

### **Forbidden Actions**
- **Dynamic Field Logic**: AI cannot implement complex business logic for form fields
- **Security Implementation**: AI cannot implement security-critical components
- **Email Templates**: AI cannot generate email template content without explicit requirements
- **Database Schema**: AI cannot design optimal database schemas without requirements
- **Production Deployment**: AI cannot deploy to production without human review

### **Review Checklist**
- [ ] Store scoping properly implemented
- [ ] All business logic in services layer
- [ ] Email sending is asynchronous
- [ ] Input validation implemented
- [ ] Logging integration complete
- [ ] Multi-language support added
- [ ] Media integration working
- [ ] Security measures in place
- [ ] Performance optimizations applied
- [ ] Test coverage meets requirements
- [ ] Migration scripts tested
- [ ] Documentation complete

---

## 📅 Implementation Timeline

### **Phase 1: Core Infrastructure (Week 1-2)**
- Set up directory structure and base models
- Implement FormTemplate and FormSubmission models
- Create basic V2 API endpoints
- Set up service layer foundation

### **Phase 2: Email Integration (Week 3-4)**
- Implement EmailTemplate model
- Integrate with smtp.md for email sending
- Add async email tasks with Celery
- Implement email tracking and analytics

### **Phase 3: Advanced Features (Week 5-6)**
- Add file upload support with media.md integration
- Implement multi-language support with translations.md
- Add conditional field logic
- Create admin interface for form management

### **Phase 4: Security & Performance (Week 7-8)**
- Implement security measures (CAPTCHA, rate limiting)
- Add performance optimizations (caching, indexing)
- Create comprehensive test suite
- Implement migration scripts from DFCMS

### **Phase 5: Analytics & Monitoring (Week 9-10)**
- Add analytics dashboard for form performance
- Implement webhook support for real-time notifications
- Add A/B testing capabilities
- Complete documentation and deployment guides
