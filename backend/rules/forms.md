# Forms Rules v1.0

## 🎯 Purpose
This document defines strict development rules for the **forms** app in CMS-Updated backend, implementing a dynamic form builder similar to Shopify's with features inspired by Fluent Form, following the clean V2-only architecture.

---

## 🏗️ Structure
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

## 🔧 Implementation
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
                form_template=form_template,
                data=request.data,
                store=getattr(request, 'store', None),
                user=request.user if request.user.is_authenticated else None,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

            serializer = FormSubmissionSerializer(submission)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({
                'error': 'Validation failed',
                'details': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
```

#### CustomerFormViewSet
```python
# apps/customer/forms/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsAuthenticated, IsStoreUser
from drf_spectacular.utils import extend_schema

class CustomerFormViewSet(TenantViewSet):
    """
    Customer form management endpoints
    Requires customer authentication
    """
    permission_classes = [IsAuthenticated, IsStoreUser]

    def get_queryset(self):
        return FormTemplate.objects.filter(
            store=self.request.store,
            created_by=self.request.user
        )

    @extend_schema(
        summary="Create Form",
        description="Create new form template",
        request=CreateFormTemplateSerializer,
        responses={201: FormTemplateSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Create form with automatic owner assignment"""
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Update Form",
        description="Update form template",
        request=UpdateFormTemplateSerializer,
        responses={200: FormTemplateSerializer}
    )
    def update(self, request, *args, **kwargs):
        """Update form with validation"""
        return super().update(request, *args, **kwargs)
```

#### DashboardFormViewSet
```python
# apps/dashboard/forms/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsAuthenticated, IsStoreStaff
from drf_spectacular.utils import extend_schema

class DashboardFormViewSet(TenantViewSet):
    """
    Dashboard form management endpoints
    Requires staff authentication
    """
    permission_classes = [IsAuthenticated, IsStoreStaff]

    def get_queryset(self):
        return FormTemplate.objects.filter(store=self.request.store)

    @extend_schema(
        summary="List All Forms",
        description="Get all forms for the store (including drafts)"
        responses={200: FormTemplateSerializer}
    )
    def list(self, request, *args, **kwargs):
        """Override to include draft forms"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Publish Form",
        description="Publish form to make it publicly available",
        responses={200: dict}
    )
    def publish(self, request, pk=None):
        """Publish form"""
        form = self.get_object()
        form.status = 'published'
        form.save(update_fields=['status'])

        return Response({
            'message': f"Form '{form.title}' published successfully",
            'form_id': form.form_id
        })

    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Duplicate Form",
        description="Create a copy of the form",
        request=DuplicateFormSerializer,
        responses={201: FormTemplateSerializer}
    )
    def duplicate(self, request, pk=None):
        """Duplicate form with all fields"""
        form = self.get_object()

        from services.form import FormService
        new_form = FormService.duplicate_form(
            original_form=form,
            new_title=request.data.get('title', f"{form.title} (Copy)"),
            store=form.store,
            user=request.user
        )

        serializer = FormTemplateSerializer(new_form)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
```

---

## 🔒 Permissions
### **Permission Matrix**
```python
# core/permissions.py

class IsFormOwner(BasePermission):
    """Allow access only to form owner"""

    def has_object_permission(self, request, view, obj):
        return (
            request.user and
            request.user.is_authenticated and
            obj.created_by == request.user
        )

class CanPublishForm(BasePermission):
    """Allow publishing if user has permission"""

    def has_object_permission(self, request, view, obj):
        return (
            request.user and
            request.user.is_authenticated and
            (
                obj.created_by == request.user or
                request.user.has_perm('forms.publish_form', obj.store)
            )
        )
```

---

## 🧪 Testing
### **Model Tests**
```python
# apps/forms/tests/test_models.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.forms.models import FormTemplate, FormField

class FormTemplateTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', slug='test-store')
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

    def test_create_form_template(self):
        form = FormTemplate.objects.create(
            store=self.store,
            title='Contact Form',
            created_by=self.user,
            form_id='ABC123'
        )

        self.assertEqual(form.title, 'Contact Form')
        self.assertEqual(form.form_id, 'ABC123')
        self.assertEqual(form.status, 'draft')

    def test_form_id_uniqueness(self):
        FormTemplate.objects.create(
            store=self.store,
            title='Form 1',
            created_by=self.user,
            form_id='ABC123'
        )

        with self.assertRaises(ValidationError):
            FormTemplate.objects.create(
                store=self.store,
                title='Form 2',
                created_by=self.user,
                form_id='ABC123'  # Duplicate
            )

    def test_auto_generate_form_id(self):
        form = FormTemplate.objects.create(
            store=self.store,
            title='Auto Form',
            created_by=self.user
        )

        self.assertIsNotNone(form.form_id)
        self.assertEqual(len(form.form_id), 6)
        self.assertTrue(form.form_id.isalnum())
```

### **Service Tests**
```python
# apps/forms/tests/test_services.py
from django.test import TestCase
from unittest.mock import patch
from apps.forms.services import FormService

class FormServiceTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', slug='test-store')
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

    def test_submit_form_success(self):
        form = FormTemplate.objects.create(
            store=self.store,
            title='Test Form',
            created_by=self.user,
            form_id='TEST123',
            fields=[
                {'type': 'text', 'label': 'Name', 'required': True},
                {'type': 'email', 'label': 'Email', 'required': True}
            ]
        )

        submission_data = {
            'Name': 'John Doe',
            'Email': 'john@example.com'
        }

        submission = FormService.submit_form(
            form_template=form,
            data=submission_data,
            store=self.store,
            user=self.user
        )

        self.assertEqual(submission.form, form)
        self.assertEqual(submission.data['Name'], 'John Doe')
        self.assertEqual(submission.status, 'submitted')

    @patch('apps.forms.services.FormService.send_notification_email')
    def test_submit_form_with_notification(self, mock_email):
        form = FormTemplate.objects.create(
            store=self.store,
            title='Test Form',
            created_by=self.user,
            form_id='TEST123',
            send_notifications=True
        )

        submission = FormService.submit_form(
            form_template=form,
            data={'Name': 'Test'},
            store=self.store,
            user=self.user
        )

        mock_email.assert_called_once()
```

---

## ⚙️ Services
### **FormService**
```python
# apps/forms/services.py
from django.core.exceptions import ValidationError
from django.db import transaction
import uuid
import logging

logger = logging.getLogger(__name__)

class FormService:
    @staticmethod
    def generate_form_id():
        """Generate unique 6-digit form ID"""
        while True:
            form_id = ''.join(random.choices(string.ascii_uppercase + string.digits, 6))
            if not FormTemplate.objects.filter(form_id=form_id).exists():
                return form_id

    @staticmethod
    def submit_form(form_template, data, store, user=None, ip_address=None, user_agent=''):
        """Submit form data with validation"""
        with transaction.atomic():
            # Validate form fields
            validated_data = FormService.validate_form_data(form_template, data)

            # Create submission
            submission = FormSubmission.objects.create(
                form=form_template,
                store=store,
                user=user,
                data=validated_data,
                ip_address=ip_address,
                user_agent=user_agent,
                status='submitted'
            )

            # Send notifications if configured
            if form_template.send_notifications:
                FormService.send_notification_email(submission)

            # Trigger webhook if configured
            if form_template.webhook_url:
                FormService.send_webhook(submission)

            logger.info(f"Form submitted: {form_template.title} - {submission.id}")
            return submission

    @staticmethod
    def validate_form_data(form_template, data):
        """Validate form data against field definitions"""
        validated_data = {}
        errors = {}

        for field in form_template.fields:
            field_name = field.get('name')
            field_value = data.get(field_name)

            if field.get('required', False) and not field_value:
                errors[field_name] = f"{field.get('label', field_name)} is required"
                continue

            # Type validation
            field_type = field.get('type')
            if field_type == 'email' and field_value:
                try:
                    validate_email(field_value)
                except ValidationError:
                    errors[field_name] = "Invalid email address"
            elif field_type == 'url' and field_value:
                try:
                    URLValidator()(field_value)
                except ValidationError:
                    errors[field_name] = "Invalid URL"

            validated_data[field_name] = field_value

        if errors:
            raise ValidationError(errors)

        return validated_data

    @staticmethod
    def duplicate_form(original_form, new_title, store, user):
        """Duplicate a form template with all fields"""
        with transaction.atomic():
            new_form = FormTemplate.objects.create(
                store=store,
                title=new_title,
                description=original_form.description,
                created_by=user,
                form_id=FormService.generate_form_id(),
                status='draft',
                fields=original_form.fields.copy(),
                send_notifications=original_form.send_notifications,
                webhook_url=original_form.webhook_url,
                success_message=original_form.success_message,
                error_message=original_form.error_message
            )

            # Copy fields
            for field in original_form.fields.all():
                FormField.objects.create(
                    form=new_form,
                    **field.__dict__
                )

            return new_form

    @staticmethod
    def send_notification_email(submission):
        """Send notification email to form owner"""
        from core.libs.email import EmailService

        context = {
            'submission': submission,
            'form': submission.form,
            'store': submission.store
        }

        EmailService.send_template_email(
            to_email=submission.form.created_by.email,
            subject=f"New Form Submission: {submission.form.title}",
            template_name='form_submission',
            context=context
        )

    @staticmethod
    def send_webhook(submission):
        """Send webhook notification"""
        import requests

        try:
            response = requests.post(
                submission.form.webhook_url,
                json={
                    'event': 'form.submitted',
                    'form_id': submission.form.form_id,
                    'submission_id': submission.id,
                    'data': submission.data,
                    'timestamp': submission.created_at.isoformat()
                },
                timeout=10
            )
            logger.info(f"Webhook sent: {response.status_code}")
        except Exception as e:
            logger.error(f"Webhook failed: {e}")
```

---

## 🔗 Dependencies
```tree
[Related components with @path references]
```
- accounts.md for user authentication and permissions
- stores.md for store-scoped queries
- notifications.md for email notifications
- webhooks.md for webhook integration
- core.md for base ViewSet and permissions
```

## 📋 Migration
### **From Legacy Forms**
```python
# apps/forms/management/commands/migrate_forms.py
from django.core.management.base import BaseCommand
from django.db import transaction

class Command(BaseCommand):
    help = 'Migrate legacy forms to new structure'

    def handle(self, *args, **options):
        from apps.legacy.models import LegacyForm

        queryset = LegacyForm.objects.all()

        with transaction.atomic():
            for legacy_form in queryset:
                # Map legacy fields to new structure
                new_fields = []
                for field in legacy_form.fields:
                    new_fields.append({
                        'type': field.field_type,
                        'label': field.label,
                        'required': field.required,
                        'options': field.options or []
                    })

                FormTemplate.objects.create(
                    store=legacy_form.store,
                    title=legacy_form.title,
                    description=legacy_form.description,
                    created_by=legacy_form.created_by,
                    form_id=legacy_form.form_id or FormService.generate_form_id(),
                    fields=new_fields,
                    status='published' if legacy_form.is_active else 'draft',
                    created_at=legacy_form.created_at
                )

        self.stdout.write(self.style.SUCCESS('Migration completed'))
```

---

## ✅ Benefits
- ✅ **Dynamic Form Builder**: Create forms without coding
- ✅ **Multi-tenant**: Store-scoped form isolation
- ✅ **Clean Architecture**: V2-only with proper service layer
- ✅ **Validation**: Built-in field validation and custom rules
- ✅ **Notifications**: Email and webhook integrations
- ✅ **Analytics**: Track submissions and form performance
- ✅ **Security**: Proper permissions and data validation

---

**Version**: 1.0
**Last Updated**: 2026-01-26
**Next Review**: 2026-02-25
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

## 🔒 Permissions
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

## 🧪 Testing
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

## ⚙️ Services
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

## 🔗 Dependencies
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

## 📋 Migration
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

## ✅ Benefits
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

---
**Version**: 1.0
**Last Updated**: 2026-01-26
**Next Review**: 2026-02-25
