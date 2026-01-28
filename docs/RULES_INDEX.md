<!-- ===============================================================================
 START CORE.MD
 ================================================================================= -->

# Core Module Rules v1.0

## 🎯 Purpose

This document defines the development rules for the **core** module in CMS-Updated backend, providing the foundational configuration, middleware, and utilities for the entire application with simplified multi-tenant architecture.

---

## 🏗️ Core Module Structure

### **Fixed Directory Structure**
```
backend/
├── core/
│   ├── __init__.py
│   ├── manage.py
│   ├── wsgi.py
│   ├── asgi.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py          # Base settings
│   │   ├── development.py   # Development settings
│   │   ├── production.py    # Production settings
│   │   └── testing.py      # Testing settings
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── tenant.py       # Tenant middleware
│   │   └── security.py     # Security middleware
│   ├── urls/
│   │   ├── __init__.py
│   │   ├── v2.py          # V2 API URLs
│   │   └── admin.py       # Admin URLs
│   ├── libs/
│   │   ├── __init__.py
│   │   ├── email.py       # Email utilities
│   │   ├── choices.py     # Common choices
│   │   ├── utils.py       # General utilities
│   │   └── validators.py  # Custom validators
│   └── exceptions/
│       ├── __init__.py
│       └── custom.py       # Custom exceptions
```

---

## 🧩 Core Architecture

### **1. Multi-Tenant Approach**

**Important**: This project uses **explicit ForeignKey relationships** for multi-tenancy, NOT automatic tenant filtering.

```python
# Standard pattern for all store-scoped models
class Product(models.Model):
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    # ... other fields

    class Meta:
        indexes = [
            models.Index(fields=['store', 'created_at']),
        ]
```

**Benefits of this approach:**
- ✅ Transparent and easy to debug
- ✅ No magic/hidden behavior
- ✅ Explicit relationships in queries
- ✅ Easier to understand for new developers

---

## 🔧 Core Settings

### **1. Base Settings**
```python
# core/settings/base.py
from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BASE_DIR.parent

# Load environment variables
load_dotenv()

# =============================================================================
# SECURITY SETTINGS
# =============================================================================
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable is required")

DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '*').split(',')

# =============================================================================
# APPLICATION DEFINITION
# =============================================================================
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',

    # Core apps
    'apps.accounts',
    'apps.stores',
    'apps.media',
    'apps.logs',

    # Feature apps
    'apps.ecommerce',
    'apps.themes',
    'apps.metafields',
    'apps.entities',
    'apps.giftcards',
    'apps.forms',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'core.middleware.tenant.TenantMiddleware',  # Before authentication
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.security.SecurityMiddleware',
]

ROOT_URLCONF = 'core.urls.v2'

# =============================================================================
# DATABASE
# =============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'cms_updated'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 60,
        }
    }
}

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =============================================================================
# STATIC FILES
# =============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# =============================================================================
# MEDIA FILES
# =============================================================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =============================================================================
# REST FRAMEWORK
# =============================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}

# =============================================================================
# JWT SETTINGS
# =============================================================================
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': SECRET_KEY,
}

# =============================================================================
# CORS SETTINGS
# =============================================================================
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS_ALLOW_CREDENTIALS = True

# =============================================================================
# MULTI-TENANT SETTINGS
# =============================================================================
# Note: We use explicit ForeignKey relationships, not automatic tenant filtering
STORE_MODEL = 'stores.Store'

# =============================================================================
# LOGGING
# =============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# =============================================================================
# SPECTACULAR (API Documentation)
# =============================================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'CMS Updated API',
    'DESCRIPTION': 'API documentation for CMS Updated',
    'VERSION': '2.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}
```

### **2. Development Settings**
```python
# core/settings/development.py
from .base import *

# Debug mode
DEBUG = True

# Email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Additional apps for development
INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# CORS for development
CORS_ALLOW_ALL_ORIGINS = True
```

### **3. Production Settings**
```python
# core/settings/production.py
from .base import *

# Security
DEBUG = False
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
```

---

## 🛡️ Middleware

### **1. Tenant Middleware**
```python
# core/middleware/tenant.py
from django.http import Http404
from django.conf import settings
from django.db import connection
import logging

logger = logging.getLogger(__name__)

class TenantMiddleware:
    """
    Middleware to handle store detection and context setting.
    Extracts store from URL path: domain.com/store/[store-slug]/
    Sets request.store for use in explicit ForeignKey queries.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Extract store from URL path
            store = self.get_store_from_path(request)

            if store:
                request.store = store
                logger.info(f"Store middleware: Set store to '{store.name}' (ID: {store.id})")
            else:
                logger.debug("Store middleware: No store detected")

            return self.get_response(request)

        except Exception as e:
            logger.error(f"Store middleware error: {str(e)}", exc_info=True)
            raise

    def get_store_from_path(self, request):
        """
        Extract store from URL path: /store/[slug]/
        """
        from apps.stores.models import Store

        path = request.path.strip('/')

        # Check for /store/[slug]/ pattern
        if path.startswith('store/'):
            parts = path.split('/')
            if len(parts) >= 2:
                store_slug = parts[1]
                store = Store.objects.filter(slug=store_slug, status='active').first()
                if store:
                    return store

        # Check for X-Store-Slug header (for API requests)
        store_slug = request.headers.get('X-Store-Slug')
        if store_slug:
            store = Store.objects.filter(slug=store_slug, status='active').first()
            if store:
                return store

        # Check session (for admin panel)
        store_id = request.session.get('store_id')
        if store_id:
            store = Store.objects.filter(id=store_id, status='active').first()
            if store:
                return store

        return None
```

### **2. Security Middleware**
```python
# core/middleware/security.py
from django.http import JsonResponse
from django.conf import settings
from django.core.exceptions import RequestDataTooBig
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """
    Security middleware for request validation and protection.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Validate request body size
            if request.method in ['POST', 'PUT', 'PATCH']:
                if request.content_type == 'application/json':
                    try:
                        body = request.body.decode('utf-8')
                        # Check size limit
                        if len(body) > settings.DATA_UPLOAD_MAX_MEMORY_SIZE:
                            return JsonResponse({
                                'error': 'Request body too large',
                                'max_size_mb': settings.DATA_UPLOAD_MAX_MEMORY_SIZE / 1024 / 1024,
                            }, status=413)
                    except UnicodeDecodeError:
                        return JsonResponse({
                            'error': 'Invalid request body encoding'
                        }, status=400)

            # Add security headers
            response = self.get_response(request)

            # Security headers
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

            return response

        except Exception as e:
            logger.error(f"Security middleware error: {str(e)}", exc_info=True)
            return JsonResponse({'error': 'Internal server error'}, status=500)
```

---

## 🌐 URL Configuration

### **1. Main URLs**
```python
# core/urls/__init__.py
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

app_name = 'core'

urlpatterns = [
    # V2 API URLs
    path('', include('core.urls.v2')),
]

# Static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### **2. V2 URLs**
```python
# core/urls/v2.py
from django.urls import path, include

app_name = 'v2'

urlpatterns = [
    # Public APIs (no authentication)
    path('api/public/', include('apps.public.urls')),

    # Customer APIs (customer authentication)
    path('api/customer/', include('apps.customer.urls')),

    # Dashboard APIs (staff authentication)
    path('api/dashboard/', include('apps.dashboard.urls')),

    # Admin
    path('admin/', admin.site.urls),
]
```

---

## 📚 Core Libraries

### **1. Email Utilities**
```python
# core/libs/email.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """
    Centralized email service for sending emails.
    """

    @staticmethod
    def send_template_email(
        to_email,
        subject,
        template_name,
        context,
        from_email=None,
        html_template=None
    ):
        """
        Send email using Django template.
        """
        try:
            # Render email content
            text_content = render_to_string(f'emails/{template_name}.txt', context)

            if html_template:
                html_content = render_to_string(f'emails/{html_template}.html', context)
            else:
                html_content = render_to_string(f'emails/{template_name}.html', context)

            # Send email
            send_mail(
                subject=subject,
                message=text_content,
                from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                html_message=html_content,
                fail_silently=False,
            )

            logger.info(f"Email sent to {to_email} with template {template_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}", exc_info=True)
            return False

    @staticmethod
    def send_welcome_email(user, store):
        """
        Send welcome email to new user.
        """
        context = {
            'user': user,
            'store': store,
            'login_url': f"{store.get_absolute_url()}/login",
        }

        return EmailService.send_template_email(
            to_email=user.email,
            subject=f"Welcome to {store.name}",
            template_name='welcome',
            context=context
        )
```

### **2. Common Choices**
```python
# core/libs/choices.py
from django.utils.translation import gettext_lazy as _

class StatusChoices:
    """Common status choices"""
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    DRAFT = 'draft'
    ARCHIVED = 'archived'

    CHOICES = [
        (ACTIVE, _('Active')),
        (INACTIVE, _('Inactive')),
        (DRAFT, _('Draft')),
        (ARCHIVED, _('Archived')),
    ]

class OrderStatusChoices:
    """Order status choices"""
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'

    CHOICES = [
        (PENDING, _('Pending')),
        (CONFIRMED, _('Confirmed')),
        (PROCESSING, _('Processing')),
        (SHIPPED, _('Shipped')),
        (DELIVERED, _('Delivered')),
        (CANCELLED, _('Cancelled')),
        (REFUNDED, _('Refunded')),
    ]

class PaymentStatusChoices:
    """Payment status choices"""
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    PARTIALLY_REFUNDED = 'partially_refunded'

    CHOICES = [
        (PENDING, _('Pending')),
        (COMPLETED, _('Completed')),
        (FAILED, _('Failed')),
        (REFUNDED, _('Refunded')),
        (PARTIALLY_REFUNDED, _('Partially Refunded')),
    ]
```

### **3. Utilities**
```python
# core/libs/utils.py
import uuid
import re
from django.utils.text import slugify
from django.core.files.uploadedfile import InMemoryUploadedFile
import logging

logger = logging.getLogger(__name__)

def generate_unique_id(length=8):
    """
    Generate a unique ID for models.
    """
    return uuid.uuid4().hex[:length].upper()

def clean_filename(filename):
    """
    Clean filename for safe storage.
    """
    # Remove special characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    # Convert to lowercase
    filename = filename.lower()
    return filename

def get_client_ip(request):
    """
    Get client IP address from request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def validate_file_size(file, max_size_mb):
    """
    Validate file size.
    """
    if isinstance(file, InMemoryUploadedFile):
        size_mb = file.size / (1024 * 1024)
        if size_mb > max_size_mb:
            raise ValueError(f"File size {size_mb:.2f}MB exceeds maximum {max_size_mb}MB")
    return True
```

---

## 🚨 Custom Exceptions

### **1. Tenant Exceptions**
```python
# core/exceptions/custom.py
from django.core.exceptions import ValidationError

class TenantError(Exception):
    """Base tenant exception"""
    pass

class TenantNotFoundError(TenantError):
    """Raised when tenant is not found"""
    pass

class TenantInactiveError(TenantError):
    """Raised when tenant is inactive"""
    pass

class TenantPermissionError(TenantError):
    """Raised when tenant doesn't have permission"""
    pass

class TenantValidationError(ValidationError):
    """Raised when tenant validation fails"""
    pass
```

---

## ⚙️ Configuration Files

### **1. Manage.py**
```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(sys.argv)
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
```

### **2. WSGI/ASGI**
```python
# core/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.production')
application = get_wsgi_application()

# core/asgi.py
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.production')
application = get_asgi_application()
```

---

## 🚀 Deployment

### **Environment Variables**
```bash
# Core Settings
DJANGO_SETTINGS_MODULE=core.settings.production
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=cms_updated
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## 📝 Implementation Notes

1. **Tenant Detection**: Uses URL path `/store/[slug]/` pattern
2. **Middleware Order**: Tenant middleware runs before authentication
3. **No Test Files**: Testing configuration omitted per requirements
4. **Single Database**: Uses tenant_id filtering instead of separate databases
5. **V2 Only**: No backward compatibility with v1

---

## ✅ Checklist

### **Phase 1: Core Setup**
- [ ] Create core directory structure
- [ ] Set up base settings
- [ ] Implement TenantModel
- [ ] Create tenant middleware

### **Phase 2: Configuration**
- [ ] Set up URL routing
- [ ] Configure security middleware
- [ ] Add core libraries

### **Phase 3: Deployment**
- [ ] Create manage.py
- [ ] Set up WSGI/ASGI
- [ ] Configure environment variables

---

Last Updated: January 23, 2026
<!-- ===============================================================================
 END CORE.MD
 ================================================================================= -->




<!-- ===============================================================================
 START ACCOUNTS.MD
 ================================================================================= -->
 # Accounts App Rules v1.0

## 🎯 Purpose

This document defines strict development rules for the **accounts** app in CMS-Updated backend, maintaining DFCMS compatibility while implementing the recommended single database + store-scoped multi-tenant approach.

---

## 🏗️ Accounts App Structure

### **Fixed Directory Structure**
```
apps/
├── public/                    # Public APIs (no authentication)
│   └── accounts/             # Public account APIs (registration, etc.)
│       ├── v2/               # Version 2 (Current Only)
│       │   ├── urls.py
│       │   ├── views.py
│       │   ├── serializers.py
│       │   ├── services.py
│       │   └── tests.py
│       ├── models/             # Shared models across versions
│       │   ├── __init__.py
│       │   ├── user.py
│       │   ├── role.py
│       │   └── preferences.py
│       ├── admin.py
│       ├── apps.py
│       └── migrations/
├── customer/                  # Customer APIs (customer authentication)
│   └── accounts/             # Customer account management
│       ├── v2/               # Version 2 (Current Only)
│       │   ├── urls.py
│       │   ├── views.py
│       │   ├── serializers.py
│       │   ├── services.py
│       │   └── tests.py
│       └── models/             # Same shared models
└── dashboard/                 # Dashboard APIs (admin authentication)
    └── accounts/             # Dashboard account management
        ├── v2/               # Version 2 (Current Only)
        │   ├── urls.py
        │   ├── views.py
        │   ├── serializers.py
        │   ├── services.py
        │   └── tests.py
        └── models/             # Same shared models
```

---

## 👤 User Model Rules (Global + Store-Scoped)

### **1. Global User Model**
```python
# apps/accounts/models/user.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class GlobalUserManager(BaseUserManager):
    """Global user manager - users exist across all stores"""

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not username:
            raise ValueError("The Username field must be set")

        email = self.normalize_email(email)

        # Check global uniqueness
        if self.model.objects.filter(email=email).exists():
            raise ValueError(f"User with email '{email}' already exists")
        if self.model.objects.filter(username=username).exists():
            raise ValueError(f"User with username '{username}' already exists")

        user = self.model(
            email=email,
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """Global user model - exists across all stores"""
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    # Global fields (no store)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = GlobalUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'accounts_user'

### **2. Store User Model**
```python
# apps/accounts/models/store_user.py
from django.db import models
from django.contrib.auth import get_user_model
from .user import User

User = get_user_model()

class StoreUser(models.Model):
    """Store-specific user roles and permissions"""
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('customer', 'Customer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='store_users')
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='store_users')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['user', 'store']]
        indexes = [
            models.Index(fields=['store', 'role']),
            models.Index(fields=['user', 'role']),
        ]
        db_table = 'accounts_store_user'
```

---

## 📁 Directory Structure Update

**Important**: Update the directory structure to use the simplified approach:

```yaml
backend/
├── apps/
│   ├── accounts/
│   │   ├── v2/
│   │   │   ├── urls.py
│   │   │   ├── views.py
│   │   │   ├── serializers.py
│   │   │   ├── services.py
│   │   │   └── tests.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   └── store_user.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── migrations/
│   └── [other apps]/
├── core/
└── services/
```

---

## 🔑 Authentication Rules

### **1. JWT Configuration**
- Use `rest_framework_simplejwt` for token authentication
- Access token: 60 minutes
- Refresh token: 7 days
- Rotate refresh tokens on use

### **2. Store Context**
- All API endpoints must validate store context
- Use `request.store` from middleware
- Filter all queries by store

---

## 📋 Implementation Checklist

### **Phase 1: Core Models**
- [ ] Create global User model
- [ ] Create StoreUser model
- [ ] Update authentication backend
- [ ] Create migrations

### **Phase 2: API Endpoints**
- [ ] Public registration/login
- [ ] Customer authentication
- [ ] Dashboard authentication
- [ ] Store user management

### **Phase 3: Permissions**
- [ ] Store-scoped permissions
- [ ] Role-based access control
- [ ] API permission classes

---

## 🚀 Migration from DFCMS

### **User Migration**
```python
# DFCMS GlobalUser → CMS-Updated User
# DFCMS StoreUser → CMS-Updated StoreUser (with explicit store FK)
```

### **Authentication Migration**
- Keep same JWT settings
- Update token claims to include store_id
- Maintain backward compatibility

---

Last Updated: January 23, 2026

    return Response({
        'error': 'Validation failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStoreUser])
@extend_schema(
    summary="User Logout",
    description="Logout user and invalidate token",
    responses={200: dict}
)
def logout(request):
    """User logout - Django REST Framework"""
    try:
        # Get refresh token from request
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        return Response({
            'message': 'Successfully logged out'
        })
    except Exception:
        return Response({
            'message': 'Logout successful'
        })
```

### **2. REST API ViewSets for User Management**
```python
# apps/dashboard/accounts/v2/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from core.permissions import IsStoreOwner, IsStoreStaff
from core.viewsets import TenantViewSet
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer

class UserViewSet(TenantViewSet):
    """
    User Management API - Django REST Framework
    Store-scoped user management for dashboard
    """

    permission_classes = [IsAuthenticated, IsStoreStaff]
    filterset_fields = ['is_active', 'role', 'is_store_owner']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'email', 'last_login']
    ordering = ['-created_at']

    @extend_schema(
        summary="List Users",
        description="Get paginated list of store users",
        responses={200: UserSerializer}
    )
    def list(self, request, *args, **kwargs):
        """List users with filtering and search"""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create User",
        description="Create new user in store",
        request=UserCreateSerializer,
        responses={201: UserSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Create user with automatic store assignment"""
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Update User",
        description="Update user details",
        request=UserUpdateSerializer,
        responses={200: UserSerializer}
    )
    def update(self, request, *args, **kwargs):
        """Update user with validation"""
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Deactivate User",
        description="Deactivate user account",
        responses={200: dict}
    )
    def deactivate(self, request, pk=None):
        """Deactivate user"""
        user = self.get_object()
        if user.is_store_owner:
            return Response({
                'error': 'Cannot deactivate store owner',
                'code': 'CANNOT_DEACTIVATE_OWNER'
            }, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = False
        user.save(update_fields=['is_active'])

        return Response({
            'message': f'User {user.email} deactivated successfully'
        })

    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Change User Role",
        description="Update user role and permissions",
        request=RoleUpdateSerializer,
        responses={200: dict}
    )
    def change_role(self, request, pk=None):
        """Change user role"""
        user = self.get_object()
        if user.is_store_owner:
            return Response({
                'error': 'Cannot change store owner role',
                'code': 'CANNOT_CHANGE_OWNER_ROLE'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = RoleUpdateSerializer(data=request.data)
        if serializer.is_valid():
            from services.user import UserService
            UserService.update_user_role(user, serializer.validated_data['role'])

            return Response({
                'message': f'User {user.email} role updated successfully',
                'new_role': user.role.name
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

### **3. REST API Profile Management**
```python
# apps/customer/accounts/v2/views.py
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from core.permissions import IsStoreUser
from core.viewsets import TenantViewSet

class ProfileView(generics.RetrieveUpdateAPIView):
    """
    User Profile API - Django REST Framework
    Customer profile management
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = UserProfileSerializer

    def get_object(self):
        """Return current user profile"""
        return self.request.user

    @extend_schema(
        summary="Get User Profile",
        description="Get current user profile information",
        responses={200: UserProfileSerializer}
    )
    def get(self, request, *args, **kwargs):
        """Get user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary="Update User Profile",
        description="Update current user profile",
        request=UserProfileUpdateSerializer,
        responses={200: UserProfileSerializer}
    )
    def patch(self, request, *args, **kwargs):
        """Update user profile"""
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(generics.GenericAPIView):
    """
    Password Change API - Django REST Framework
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = PasswordChangeSerializer

    @extend_schema(
        summary="Change Password",
        description="Change user password",
        request=PasswordChangeSerializer,
        responses={200: dict, 400: dict}
    )
    def post(self, request, *args, **kwargs):
        """Change user password"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            # Verify current password
            if not user.check_password(serializer.validated_data['current_password']):
                return Response({
                    'error': 'Current password is incorrect',
                    'code': 'INVALID_CURRENT_PASSWORD'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save(update_fields=['password'])

            return Response({
                'message': 'Password changed successfully'
            })


### **1. Authentication Service**
```python
# services/auth.py (SHARED across all versions)
from django.contrib.auth import login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """Shared authentication service"""

    @staticmethod
    def generate_token(user):
        """Generate JWT token for user"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @staticmethod
    def verify_token(token):
        """Verify JWT token"""
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token)
            return access_token.payload
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None

    @staticmethod
    def send_password_reset_email(user, store):
        """Send password reset email"""
        from services.email import EmailService
        token = AuthService.generate_reset_token(user)
        EmailService.send_password_reset_email(user, store, token)

    @staticmethod
    def generate_reset_token(user):
        """Generate password reset token"""
        from django.utils.crypto import get_random_string
        return get_random_string(64)
```

### **2. User Service**
```python
# services/user.py (SHARED across all versions)
from django.core.exceptions import ValidationError
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Shared user management service"""

    @staticmethod
    def create_user_store_owner(store, email, username, password):
        """Create store owner user"""
        with transaction.atomic():
            # Create owner role for store
            from apps.public.accounts.models import Role
            owner_role = Role.objects.create(
                store=store,
                name='Store Owner',
                slug='store-owner',
                description='Full access to store',
                can_manage_products=True,
                can_manage_orders=True,
                can_manage_customers=True,
                can_manage_settings=True,
                can_view_analytics=True,
                level=100
            )

            # Create owner user
            from apps.public.accounts.models import User
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password,
                store=store,
                is_store_owner=True,
                is_verified=True,  # Auto-verify store owners
                role=owner_role
            )

            # Update store owner
            store.owner = user
            store.save()

            return user

    @staticmethod
    def update_user_role(user, new_role):
        """Update user role with permission validation"""
        if user.is_store_owner:
            raise ValidationError("Cannot change store owner role")

        user.role = new_role
        user.save(update_fields=['role'])

        logger.info(f"Updated user {user.email} role to {new_role.name}")

    @staticmethod
    def deactivate_user(user):
        """Safely deactivate user"""
        user.is_active = False
        user.save(update_fields=['is_active'])

        logger.info(f"Deactivated user {user.email}")
```

---

## 🔒 Permission Rules

### **1. Store-Scoped Permissions**
```python
# core/permissions.py
from rest_framework.permissions import BasePermission

class IsStoreOwner(BasePermission):
    """Allow access only to store owners"""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'store') and
            request.user.is_store_owner
        )

class IsStoreStaff(BasePermission):
    """Allow access to store staff (owners + staff users)"""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'store') and
            (request.user.is_store_owner or request.user.is_staff)
        )

class IsStoreUser(BasePermission):
    """Allow access to any authenticated store user"""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'store')
        )

class HasStorePermission(BasePermission):
    """Check specific store permissions"""

    def __init__(self, permission_field):
        self.permission_field = permission_field

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        # Check if user has required permission via role
        if hasattr(request.user, 'role') and request.user.role:
            return getattr(request.user.role, self.permission_field, False)

        return False
```

---

## 📡 URL Structure Rules

### **1. Public Account URLs**
```python
# apps/public/accounts/v2/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RegisterView, LoginView, LogoutView,
    PasswordResetView, PasswordResetConfirmView,
    EmailVerificationView
)

router = DefaultRouter()
# No ViewSet registration for auth endpoints - use API views

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('verify-email/', EmailVerificationView.as_view(), name='verify-email'),
]

# Main app URLs
# apps/public/accounts/urls.py
from django.urls import include, path

app_name = 'accounts'

urlpatterns = [
    path('v2/', include('apps.public.accounts.v2.urls')),
]
```

### **2. Customer Account URLs**
```python
# apps/customer/accounts/v2/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProfileView, ChangePasswordView,
    UpdateProfileView, DeleteAccountView
)

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='customer-profile')

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('update-profile/', UpdateProfileView.as_view(), name='update-profile'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
]

# Main app URLs
# apps/customer/accounts/urls.py
from django.urls import include, path

app_name = 'customer_accounts'

urlpatterns = [
    path('v2/', include('apps.customer.accounts.v2.urls')),
]
```

### **3. Dashboard Account URLs**
```python
# apps/dashboard/accounts/v2/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import UserViewSet, RoleViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='dashboard-users')
router.register(r'roles', RoleViewSet, basename='dashboard-roles')

# Nested routes for user management
users_router = routers.NestedDefaultRouter(router, r'users', lookup='user')
users_router.register(r'activity', UserActivityViewSet, basename='user-activity')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(users_router.urls)),
]

# Main app URLs
# apps/dashboard/accounts/urls.py
from django.urls import include, path

app_name = 'dashboard_accounts'

urlpatterns = [
    path('v2/', include('apps.dashboard.accounts.v2.urls')),
]
```

### **4. Main Project URLs**
```python
# config/urls.py
from django.urls import path, include

urlpatterns = [
    # Public account APIs
    path('v2/api/public/accounts/', include('apps.public.accounts.urls')),

    # Customer account APIs
    path('v2/api/customer/accounts/', include('apps.customer.accounts.urls')),

    # Dashboard account APIs
    path('v2/api/dashboard/accounts/', include('apps.dashboard.accounts.urls')),

    # Other workspace APIs...
]
```

---

## 🧪 Testing Rules

### **1. Model Tests**
```python
# apps/public/accounts/tests/test_models.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from ..models import User, Role

class UserModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', slug='test-store')

    def test_create_user(self):
        """Test user creation with store context"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            store=self.store
        )

        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.store, self.store)
        self.assertTrue(user.check_password('testpass123'))

    def test_email_unique_per_store(self):
        """Test email uniqueness within store"""
        User.objects.create_user(
            email='test@example.com',
            username='user1',
            password='pass123',
            store=self.store
        )

        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='test@example.com',
                username='user2',
                password='pass123',
                store=self.store
            )

    def test_same_email_different_store(self):
        """Test same email can exist in different stores"""
        store2 = Store.objects.create(name='Store 2', slug='store-2')

        user1 = User.objects.create_user(
            email='test@example.com',
            username='user1',
            password='pass123',
            store=self.store
        )

        user2 = User.objects.create_user(
            email='test@example.com',
            username='user2',
            password='pass123',
            store=store2
        )

        self.assertNotEqual(user1.store, user2.store)
        self.assertEqual(user1.email, user2.email)
```

---

## 📋 Migration Rules

### **1. DFCMS Compatibility Migration**
```python
# apps/public/accounts/migrations/0002_migrate_dfcms_users.py
from django.db import migrations

def migrate_global_users(apps, schema_editor):
    """Migrate DFCMS GlobalUser to new User model"""
    GlobalUser = apps.get_model('modules', 'GlobalUser')
    Store = apps.get_model('modules', 'Store')
    User = apps.get_model('public_accounts', 'User')

    for global_user in GlobalUser.objects.all():
        # Create user for each store they belong to
        for store in global_user.stores.all():
            User.objects.create(
                email=global_user.email,
                username=global_user.username,
                first_name=global_user.first_name,
                last_name=global_user.last_name,
                is_verified=global_user.is_verified,
                is_active=global_user.is_active,
                is_staff=global_user.is_staff,
                is_superuser=global_user.is_superuser,
                store=store,
                is_store_owner=(store.owner == global_user),
                created_at=global_user.date_joined,
            )

def migrate_store_users(apps, schema_editor):
    """Migrate DFCMS UserAccount to new User model"""
    UserAccount = apps.get_model('modules', 'UserAccount')
    Store = apps.get_model('modules', 'Store')
    User = apps.get_model('public_accounts', 'User')

    for store_user in UserAccount.objects.all():
        # Map to new user model
        User.objects.create(
            email=store_user.email,
            username=store_user.username,
            first_name=store_user.first_name,
            last_name=store_user.last_name,
            is_verified=store_user.is_verified,
            is_active=store_user.is_active,
            is_staff=store_user.is_staff,
            store=store_user.store,
            created_at=store_user.date_joined,
        )

class Migration(migrations.Migration):
    dependencies = [
        ('public_accounts', '0001_initial'),
        ('modules', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_global_users),
        migrations.RunPython(migrate_store_users),
    ]
```

---

## 🎯 Key Benefits of This Approach

### **✅ Complete Store Isolation**
- Same email can exist in different stores
- Users belong to specific stores only
- No cross-store data leakage

### **✅ DFCMS Compatibility**
- Maintains all existing fields and logic
- Smooth migration path
- Preserves user experience

### **✅ Simple Implementation**
- Single database
- Standard Django auth
- Clear separation of concerns

### **✅ Scalable Architecture**
- Works for thousands of stores
- Easy to add new features
- Professional multi-tenancy

---

**🚨 THESE RULES ARE MANDATORY - NO EXCEPTIONS!**

Every accounts app development must follow these rules exactly. Any deviation will result in inconsistent user management and potential security issues.

<!-- ===============================================================================
 END ACCOUNTS.MD
 ================================================================================= -->


<!-- ===============================================================================
 START CACHE.MD
 ================================================================================= -->
 # Cache App Rules v1.0

## 🎯 Purpose

This document defines strict development rules for the **cache** system in CMS-Updated backend, implementing a unified caching strategy with Redis for performance optimization across all modules.

---

## 🏗️ Cache System Structure

### **Fixed Directory Structure**
```
apps/
├── cache/
│   ├── __init__.py
│   ├── services.py
│   ├── tasks.py
│   ├── management/
│   │   └── commands/
│   │       ├── clear_cache.py
│   │       ├── warm_cache.py
│   │       └── analyze_cache.py
│   └── tests/
│       ├── __init__.py
│       └── test_services.py
```

---

## 📋 Cache Key Standards

### **Key Naming Convention**
All cache keys must follow this pattern:

```
{store_slug}:{module}:{object_type}:{object_id}:{version}
```

**Examples:**
- `my-store:pages:page:123:v1`
- `my-store:ecommerce:product:456:v1`
- `my-store:translations:translation:en_US:v1`

### **Key Prefixes**
```python
# Cache key prefixes by module
CACHE_PREFIXES = {
    'pages': 'pages',
    'posts': 'posts',
    'ecommerce': 'ecommerce',
    'translations': 'translations',
    'themes': 'themes',
    'media': 'media',
    'forms': 'forms',
    'webhooks': 'webhooks',
    'notifications': 'notifications',
    'search': 'search',
}
```

---

## 🛠️ Services Layer

### **CacheService**
```python
# apps/cache/services.py
from django.core.cache import cache
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """Shared cache management service"""

    @staticmethod
    def get_cache_key(store, module, object_type, object_id, version='v1'):
        """
        Generate standardized cache key
        """
        return f"{store.slug}:{module}:{object_type}:{object_id}:{version}"

    @staticmethod
    def get(store, module, object_type, object_id, default=None):
        """
        Get value from cache
        """
        key = CacheService.get_cache_key(store, module, object_type, object_id)
        value = cache.get(key)

        if value is not None:
            logger.debug(f"Cache HIT: {key}")
        else:
            logger.debug(f"Cache MISS: {key}")

        return value

    @staticmethod
    def set(store, module, object_type, object_id, value, timeout=3600):
        """
        Set value in cache
        """
        key = CacheService.get_cache_key(store, module, object_type, object_id)
        cache.set(key, value, timeout)

        logger.debug(f"Cache SET: {key} (timeout: {timeout}s)")
        return True

    @staticmethod
    def delete(store, module, object_type, object_id):
        """
        Delete value from cache
        """
        key = CacheService.get_cache_key(store, module, object_type, object_id)
        cache.delete(key)

        logger.debug(f"Cache DELETE: {key}")
        return True

    @staticmethod
    def delete_pattern(store, pattern):
        """
        Delete all keys matching pattern
        """
        from django.core.cache.backends.redis import RedisCache

        if not isinstance(cache, RedisCache):
            logger.warning("Pattern deletion only works with Redis cache")
            return False

        # Get Redis client
        client = cache._client

        # Build pattern
        full_pattern = f"{store.slug}:{pattern}*"

        # Find and delete keys
        keys = client.keys(full_pattern)
        if keys:
            client.delete(*keys)
            logger.debug(f"Cache DELETE PATTERN: {full_pattern} ({len(keys)} keys)")

        return True

    @staticmethod
    def invalidate_store(store):
        """
        Invalidate all cache for a store
        """
        return CacheService.delete_pattern(store, '*')

    @staticmethod
    def invalidate_module(store, module):
        """
        Invalidate all cache for a module in a store
        """
        return CacheService.delete_pattern(store, f"{module}:*")

    @staticmethod
    def get_or_set(store, module, object_type, object_id, callback, timeout=3600):
        """
        Get value from cache or set using callback
        """
        value = CacheService.get(store, module, object_type, object_id)

        if value is None:
            value = callback()
            CacheService.set(store, module, object_type, object_id, value, timeout)

        return value

    @staticmethod
    def cache_json(store, module, object_type, object_id, data, timeout=3600):
        """
        Cache JSON data
        """
        key = CacheService.get_cache_key(store, module, object_type, object_id)
        cache.set(key, json.dumps(data), timeout)

        logger.debug(f"Cache JSON: {key}")
        return True

    @staticmethod
    def get_json(store, module, object_type, object_id):
        """
        Get JSON data from cache
        """
        value = CacheService.get(store, module, object_type, object_id)

        if value is not None:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON from cache: {key}")
                return None

        return None

    @staticmethod
    def get_cache_stats():
        """
        Get cache statistics
        """
        from django.core.cache.backends.redis import RedisCache

        if not isinstance(cache, RedisCache):
            return {'error': 'Only Redis cache supports stats'}

        client = cache._client
        info = client.info('stats')

        return {
            'hits': info.get('keyspace_hits', 0),
            'misses': info.get('keyspace_misses', 0),
            'hit_rate': info.get('keyspace_hits', 0) / (info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1)) * 100,
        }
```

---

## 🔄 Cache Invalidation Strategies

### **Invalidation Rules**

#### **1. Time-Based Invalidation**
```python
# Short-lived cache (5 minutes)
CacheService.set(store, 'ecommerce', 'product', product.id, data, timeout=300)

# Medium-lived cache (1 hour)
CacheService.set(store, 'pages', 'page', page.id, data, timeout=3600)

# Long-lived cache (24 hours)
CacheService.set(store, 'translations', 'translation', lang_code, data, timeout=86400)
```

#### **2. Event-Based Invalidation**
```python
# Invalidate on model save
from django.db.models.signals import post_save, post_delete

@receiver(post_save, sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    CacheService.delete(instance.store, 'ecommerce', 'product', instance.id)
    CacheService.delete_pattern(instance.store, 'ecommerce:product:*')

@receiver(post_delete, sender=Product)
def invalidate_product_cache_delete(sender, instance, **kwargs):
    CacheService.delete(instance.store, 'ecommerce', 'product', instance.id)
```

#### **3. Manual Invalidation**
```python
# Invalidate specific object
CacheService.delete(store, 'pages', 'page', page.id)

# Invalidate all pages for a store
CacheService.delete_pattern(store, 'pages:*')

# Invalidate entire store
CacheService.invalidate_store(store)
```

---

## 📊 Cache Warming Strategies

### **Cache Warming Service**
```python
# apps/cache/services.py (continued)

class CacheWarmupService:
    """Cache warming service"""

    @staticmethod
    def warm_store_cache(store):
        """
        Warm cache for a store
        """
        logger.info(f"Warming cache for store: {store.slug}")

        # Warm pages
        CacheWarmupService._warm_pages(store)

        # Warm products
        CacheWarmupService._warm_products(store)

        # Warm translations
        CacheWarmupService._warm_translations(store)

        logger.info(f"Cache warming complete for store: {store.slug}")

    @staticmethod
    def _warm_pages(store):
        """Warm page cache"""
        from apps.pages.models import Page

        pages = Page.objects.filter(
            store=store,
            status='published'
        ).select_related('store')

        for page in pages:
            data = {
                'id': page.id,
                'title': page.title,
                'slug': page.slug,
                'content': page.content,
                'url': page.get_absolute_url()
            }
            CacheService.cache_json(store, 'pages', 'page', page.id, data, timeout=3600)

    @staticmethod
    def _warm_products(store):
        """Warm product cache"""
        from apps.ecommerce.models import Product

        products = Product.objects.filter(
            store=store,
            is_active=True
        ).select_related('store').prefetch_related('variants')

        for product in products:
            data = {
                'id': product.id,
                'title': product.title,
                'description': product.description,
                'price': float(product.price),
                'is_active': product.is_active
            }
            CacheService.cache_json(store, 'ecommerce', 'product', product.id, data, timeout=3600)

    @staticmethod
    def _warm_translations(store):
        """Warm translation cache"""
        from apps.translations.models import Translation

        translations = Translation.objects.filter(
            store=store
        ).select_related('language', 'translation_key')

        for translation in translations:
            key = f"{translation.language.code}:{translation.translation_key.key}"
            CacheService.set(store, 'translations', 'translation', key, translation.text, timeout=86400)
```

---

## 🚀 Celery Tasks

### **Cache Management Tasks**
```python
# apps/cache/tasks.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def clear_cache(store_id=None):
    """
    Clear cache for store or all stores
    """
    if store_id:
        from .models import Store
        store = Store.objects.get(id=store_id)
        CacheService.invalidate_store(store)
        logger.info(f"Cleared cache for store: {store.slug}")
    else:
        # Clear all cache
        cache.clear()
        logger.info("Cleared all cache")

@shared_task
def warm_cache(store_id):
    """
    Warm cache for a store
    """
    from .models import Store
    from .services import CacheWarmupService

    store = Store.objects.get(id=store_id)
    CacheWarmupService.warm_store_cache(store)

@shared_task
def analyze_cache():
    """
    Analyze cache performance
    """
    stats = CacheService.get_cache_stats()

    logger.info(f"Cache Stats: {stats}")

    # Alert if hit rate is low
    if stats.get('hit_rate', 0) < 50:
        logger.warning(f"Low cache hit rate: {stats['hit_rate']:.2f}%")
```

---

## 🔧 Management Commands

### **Clear Cache**
```bash
# Clear all cache
python manage.py clear_cache

# Clear cache for specific store
python manage.py clear_cache --store=my-store

# Clear cache for specific module
python manage.py clear_cache --store=my-store --module=pages
```

### **Warm Cache**
```bash
# Warm cache for a store
python manage.py warm_cache --store=my-store
```

### **Analyze Cache**
```bash
# Analyze cache performance
python manage.py analyze_cache
```

---

## 📚 Cache Best Practices

### **DO:**
1. **Use consistent key patterns** - Follow the naming convention
2. **Set appropriate timeouts** - Match data freshness requirements
3. **Invalidate on changes** - Use signals for automatic invalidation
4. **Warm critical data** - Preload frequently accessed data
5. **Monitor hit rates** - Track cache performance
6. **Use JSON for complex data** - Serialize complex objects
7. **Cache database queries** - Reduce database load
8. **Cache expensive computations** - Improve response times
9. **Use get_or_set pattern** - Simplify cache logic
10. **Log cache operations** - Debug cache issues

### **DON'T:**
1. **Don't cache sensitive data** - Never cache passwords, tokens, etc.
2. **Don't cache forever** - Always set timeouts
3. **Don't cache without invalidation** - Stale data is worse than no data
4. **Don't cache large objects** - Keep cache entries small
5. **Don't ignore cache failures** - Handle cache errors gracefully
6. **Don't cache user-specific data without user ID** - Include user in key
7. **Don't cache mutable objects** - Always return copies
8. **Don't cache without versioning** - Use version numbers for schema changes
9. **Don't rely on cache** - Always have fallback logic
10. **Don't cache everything** - Only cache what's expensive to compute

---

## 🔗 Integration Examples

### **Integration with pages.md**
```python
# apps/pages/services.py
from apps.cache.services import CacheService

class PageService:
    @staticmethod
    def get_page(store, page_id):
        """Get page with caching"""
        # Try cache first
        cached = CacheService.get_json(store, 'pages', 'page', page_id)
        if cached:
            return cached

        # Fetch from database
        page = Page.objects.get(store=store, id=page_id)

        # Cache the result
        data = {
            'id': page.id,
            'title': page.title,
            'slug': page.slug,
            'content': page.content,
            'url': page.get_absolute_url()
        }
        CacheService.cache_json(store, 'pages', 'page', page.id, data, timeout=3600)

        return data
```

### **Integration with ecommerce.md**
```python
# apps/ecommerce/services.py
from apps.cache.services import CacheService

class ProductService:
    @staticmethod
    def get_product(store, product_id):
        """Get product with caching"""
        # Try cache first
        cached = CacheService.get_json(store, 'ecommerce', 'product', product_id)
        if cached:
            return cached

        # Fetch from database
        product = Product.objects.get(store=store, id=product_id)

        # Cache the result
        data = {
            'id': product.id,
            'title': product.title,
            'description': product.description,
            'price': float(product.price),
            'is_active': product.is_active
        }
        CacheService.cache_json(store, 'ecommerce', 'product', product.id, data, timeout=3600)

        return data
```

### **Integration with translations.md**
```python
# apps/translations/services.py
from apps.cache.services import CacheService

class TranslationService:
    @staticmethod
    def get_translation(store, language_code, key):
        """Get translation with caching"""
        cache_key = f"{language_code}:{key}"

        # Try cache first
        cached = CacheService.get(store, 'translations', 'translation', cache_key)
        if cached:
            return cached

        # Fetch from database
        translation = Translation.objects.get(
            store=store,
            language__code=language_code,
            translation_key__key=key
        )

        # Cache the result
        CacheService.set(store, 'translations', 'translation', cache_key, translation.text, timeout=86400)

        return translation.text
```

---

## 📊 Cache Configuration

### **Redis Configuration**
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'cms-updated',
        'TIMEOUT': 3600,
    }
}
```

### **Cache Timeout Standards**
```python
CACHE_TIMEOUTS = {
    'short': 300,      # 5 minutes
    'medium': 3600,    # 1 hour
    'long': 86400,     # 24 hours
    'very_long': 604800,  # 7 days
}
```

---

## 🧪 Testing Rules

### **Required Coverage**
- **Services**: 100% code coverage
- **Integration**: Critical path testing

### **Test Examples**
```python
# apps/cache/tests/test_services.py
from django.test import TestCase
from ..services import CacheService

class CacheServiceTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', slug='test-store')

    def test_cache_set_and_get(self):
        """Test cache set and get"""
        data = {'test': 'data'}

        CacheService.set(self.store, 'test', 'object', '1', data)
        cached = CacheService.get(self.store, 'test', 'object', '1')

        self.assertEqual(cached, data)

    def test_cache_delete(self):
        """Test cache delete"""
        data = {'test': 'data'}

        CacheService.set(self.store, 'test', 'object', '1', data)
        CacheService.delete(self.store, 'test', 'object', '1')

        cached = CacheService.get(self.store, 'test', 'object', '1')
        self.assertIsNone(cached)

    def test_cache_get_or_set(self):
        """Test cache get_or_set"""
        callback_called = []

        def callback():
            callback_called.append(True)
            return {'test': 'data'}

        # First call - should execute callback
        result1 = CacheService.get_or_set(self.store, 'test', 'object', '1', callback)
        self.assertEqual(len(callback_called), 1)

        # Second call - should use cache
        result2 = CacheService.get_or_set(self.store, 'test', 'object', '1', callback)
        self.assertEqual(len(callback_called), 1)

        self.assertEqual(result1, result2)
```

---

## 📈 Monitoring

### **Cache Metrics to Track**
- **Hit Rate**: Percentage of cache hits vs misses
- **Memory Usage**: Total memory used by cache
- **Key Count**: Number of keys in cache
- **Eviction Rate**: Rate at which keys are evicted
- **Latency**: Average cache response time

### **Alerting**
- **Low Hit Rate**: Alert if hit rate < 50%
- **High Memory Usage**: Alert if memory > 80%
- **Cache Errors**: Alert on cache connection errors

---

## 🎯 Implementation Checklist

- [ ] Create CacheService with standard methods
- [ ] Implement cache key naming convention
- [ ] Create cache invalidation strategies
- [ ] Implement cache warming service
- [ ] Create Celery tasks for cache management
- [ ] Add management commands
- [ ] Create tests (services)
- [ ] Add monitoring and logging
- [ ] Document cache best practices
- [ ] Add integration examples
- [ ] Configure Redis cache backend
- [ ] Set up cache monitoring

---

<!-- ===============================================================================
 END CACHE.MD
 ================================================================================= -->


<!-- ===============================================================================
 START ENTITIES.MD
 ================================================================================= -->
# Entities Rules v1.0

## 🎯 Purpose

This document defines strict development rules for the **entities** app in CMS-Updated backend, implementing a generic entity action system (Like, Heart, Upvote, DownVote, Wishlist, Favorites, etc.) for any content type, following the clean V2-only architecture.

---

## 🏗️ Entities App Structure

### **Fixed Directory Structure**
```
apps/
├── customer/                  # Customer APIs (customer authentication)
│   └── entities/             # Customer entity APIs
│       ├── v2/               # Version 2 (Current Only)
│       │   ├── urls.py
│       │   ├── views.py
│       │   ├── serializers.py
│       │   ├── services.py
│       │   └── tests.py
│       ├── models/             # Shared models across versions
│       │   ├── __init__.py
│       │   ├── actions.py      # EntityAction model
│       │   └── interactions.py # EntityInteraction model
│       ├── admin.py
│       ├── apps.py
│       └── migrations/
├── public/                    # Public APIs (no authentication)
│   └── entities/             # Public entity APIs
│       ├── v2/               # Version 2 (Current Only)
│       │   ├── urls.py
│       │   ├── views.py
│       │   ├── serializers.py
│       │   ├── services.py
│       │   └── tests.py
│       └── models/             # Same shared models
└── dashboard/                 # Dashboard APIs (admin authentication)
    └── entities/             # Dashboard entity APIs
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
All entities models must inherit from `TenantModel` for store scoping:

```python
from core.models import TenantModel
from django.db import models

class EntityAction(TenantModel):
    # Store-scoped entity action model
    pass
```

### **EntityAction Model**
```python
# apps/public/entities/models/actions.py
from django.db import models
from core.models import TenantModel

class EntityAction(TenantModel):
    """
    Store-scoped entity actions (Like, Heart, Upvote, DownVote, etc.)
    Defines available actions for content types
    """

    # Core fields
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    description = models.TextField(blank=True)

    # Action configuration
    ACTION_TYPES = [
        ('toggle', 'Toggle (Like/Unlike)'),
        ('single', 'Single (Upvote only)'),
        ('rating', 'Rating (1-5 stars)'),
        ('counter', 'Counter (View count)'),
    ]
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES, default='toggle')

    # Visual configuration
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=20, blank=True)

    # Content type targeting
    content_types = models.JSONField(
        default=list,
        help_text="Which models this action applies to"
    )

    # Settings
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    allow_anonymous = models.BooleanField(default=False)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    class Meta(TenantModel.Meta):
        db_table = 'entities_entity_action'
        unique_together = [['store', 'slug']]
        indexes = [
            models.Index(fields=['store', 'is_active']),
            models.Index(fields=['content_types']),
        ]
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.action_type})"
```

### **EntityInteraction Model**
```python
# apps/public/entities/models/interactions.py
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from core.models import TenantModel

class EntityInteraction(TenantModel):
    """
    User interactions with entities (likes, votes, etc.)
    Generic relationship to any model
    """

    # Relationships
    action = models.ForeignKey(
        'entities.EntityAction',
        on_delete=models.CASCADE,
        related_name='interactions'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='entity_interactions',
        null=True,
        blank=True
    )

    # Generic foreign key to any model
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Interaction data
    value = models.JSONField(default=dict, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = 'entities_entity_interaction'
        unique_together = [
            ['store', 'action', 'user', 'content_type', 'object_id']
        ]
        indexes = [
            models.Index(fields=['action', 'content_type', 'object_id']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} {self.action.name} {self.content_object}"
```

---

## 🛠️ Services Layer

### **EntityService**
```python
# apps/public/entities/services.py
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
import logging

logger = logging.getLogger(__name__)

class EntityService:
    """Shared entity interaction service"""

    @staticmethod
    @transaction.atomic
    def toggle_action(user, content_object, action_slug, store=None):
        """Toggle an action (like/unlike, favorite/unfavorite)"""
        from .models import EntityAction, EntityInteraction

        # Get action
        action = EntityAction.objects.get(store=store, slug=action_slug)

        if action.action_type != 'toggle':
            raise ValueError(f"Action '{action.name}' is not a toggle action")

        # Get content type
        content_type = ContentType.objects.get_for_model(content_object)

        # Check existing interaction
        try:
            interaction = EntityInteraction.objects.get(
                store=store,
                action=action,
                user=user,
                content_type=content_type,
                object_id=content_object.id
            )

            # Remove existing interaction
            interaction.delete()
            action_performed = 'removed'

        except EntityInteraction.DoesNotExist:
            # Create new interaction
            interaction = EntityInteraction.objects.create(
                store=store,
                action=action,
                user=user,
                content_type=content_type,
                object_id=content_object.id
            )
            action_performed = 'added'

        # Log action
        log_event_async(
            user=user,
            store=store,
            action=f'entity_{action_performed}',
            object_type='entity_interaction',
            object_id=interaction.id if action_performed == 'added' else None,
            details={
                'action_slug': action_slug,
                'content_type': content_type.model,
                'object_id': content_object.id
            }
        )

        return {
            'action': action_performed,
            'entity_action': action,
            'interaction': interaction if action_performed == 'added' else None
        }

    @staticmethod
    def get_interaction_count(content_object, action_slug, store=None):
        """Get total count for an action"""
        from .models import EntityAction, EntityInteraction

        action = EntityAction.objects.get(store=store, slug=action_slug)
        content_type = ContentType.objects.get_for_model(content_object)

        return EntityInteraction.objects.filter(
            store=store,
            action=action,
            content_type=content_type,
            object_id=content_object.id,
            is_active=True
        ).count()

    @staticmethod
    def get_user_interactions(user, content_object, store=None):
        """Get all user interactions for an object"""
        from .models import EntityInteraction

        content_type = ContentType.objects.get_for_model(content_object)

        return EntityInteraction.objects.filter(
            store=store,
            user=user,
            content_type=content_type,
            object_id=content_object.id,
            is_active=True
        ).select_related('action')

    @staticmethod
    def get_popular_objects(action_slug, limit=10, store=None):
        """Get most popular objects for an action"""
        from .models import EntityAction, EntityInteraction

        action = EntityAction.objects.get(store=store, slug=action_slug)

        return EntityInteraction.objects.filter(
            store=store,
            action=action,
            is_active=True
        ).values('content_type', 'object_id').annotate(
            count=models.Count('id')
        ).order_by('-count')[:limit]
```

---

## 🔌 API Endpoints

### **CustomerEntityViewSet**
```python
# apps/customer/entities/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreUser
from drf_spectacular.utils import extend_schema

class CustomerEntityViewSet(TenantViewSet):
    """
    Customer entity interaction endpoints
    """
    permission_classes = [IsAuthenticated, IsStoreUser]

    @extend_schema(
        summary="Toggle Entity Action",
        request=EntityActionSerializer,
        responses={200: EntityInteractionSerializer}
    )
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Toggle an entity action (like/unlike, etc.)"""
        serializer = EntityActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        content_type = ContentType.objects.get(
            model=serializer.validated_data['content_type']
        )
        model_class = content_type.model_class()
        content_object = model_class.objects.get(
            id=serializer.validated_data['object_id']
        )

        result = EntityService.toggle_action(
            user=request.user,
            content_object=content_object,
            action_slug=serializer.validated_data['action_slug'],
            store=request.store
        )

        return Response(result)

    @extend_schema(
        summary="Get Entity Stats",
        responses={200: dict}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get interaction statistics for an object"""
        content_type = request.query_params.get('content_type')
        object_id = request.query_params.get('object_id')
        action_slug = request.query_params.get('action_slug')

        if not all([content_type, object_id]):
            return Response(
                {'error': 'content_type and object_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        content_type_obj = ContentType.objects.get(model=content_type)
        model_class = content_type_obj.model_class()
        content_object = model_class.objects.get(id=object_id)

        count = EntityService.get_interaction_count(
            content_object=content_object,
            action_slug=action_slug,
            store=request.store
        )

        user_interactions = EntityService.get_user_interactions(
            user=request.user,
            content_object=content_object,
            store=request.store
        )

        return Response({
            'count': count,
            'user_interactions': EntityInteractionSerializer(
                user_interactions, many=True
            ).data
        })
```

---

## 🔄 Usage Examples

### **Adding Entity Actions to Models**
```python
# Example: Adding entity actions to a Post model
class Post(TenantModel):
    # ... existing fields ...

    @property
    def like_count(self):
        """Get total likes"""
        from entities.services import EntityService
        return EntityService.get_interaction_count(
            content_object=self,
            action_slug='like',
            store=self.store
        )

    def user_liked(self, user):
        """Check if user liked this post"""
        from entities.services import EntityService
        interactions = EntityService.get_user_interactions(
            user=user,
            content_object=self,
            store=self.store
        )
        return interactions.filter(action__slug='like').exists()

    def toggle_like(self, user):
        """Toggle like for user"""
        from entities.services import EntityService
        return EntityService.toggle_action(
            user=user,
            content_object=self,
            action_slug='like',
            store=self.store
        )
```

### **Frontend Integration**
```javascript
// Example JavaScript for entity interactions
async function toggleLike(postId) {
    try {
        const response = await fetch('/v2/api/customer/entities/toggle/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                action_slug: 'like',
                content_type: 'post',
                object_id: postId
            })
        });

        const result = await response.json();

        if (result.action === 'added') {
            updateLikeButton(true, result.interaction);
        } else {
            updateLikeButton(false, null);
        }

    } catch (error) {
        console.error('Error toggling like:', error);
    }
}
```

---

## 🛡️ Security Rules

### **Access Control**
- **User Authentication**: Required for all interactions
- **Store Scoping**: All interactions are store-scoped
- **Content Validation**: Validate content objects exist
- **Rate Limiting**: Prevent spam interactions

### **Privacy Rules**
- **Anonymous Actions**: Configurable per action type
- **Public Visibility**: Only show public interaction counts
- **User Privacy**: Hide user interactions from others

---

## 📊 Performance Rules

### **Database Optimization**
- **Proper Indexing**: All foreign keys and common queries indexed
- **Count Caching**: Cache interaction counts
- **Bulk Operations**: Support for bulk interaction queries

### **API Performance**
- **Pagination**: For popular objects lists
- **Caching**: Cache action definitions and counts
- **Efficient Queries**: Use `select_related` and `prefetch_related`

---

## 🧪 Testing Rules

### **Required Coverage**
- **Models**: 95% code coverage
- **Services**: 100% code coverage
- **Views**: 90% code coverage

### **Test Examples**
```python
# apps/customer/entities/tests/test_services.py
from django.test import TestCase
from ..models import EntityAction, EntityInteraction
from ..services import EntityService

class EntityServiceTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', slug='test-store')
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.post = Post.objects.create(
            store=self.store,
            title='Test Post',
            slug='test-post'
        )

        # Create like action
        self.like_action = EntityAction.objects.create(
            store=self.store,
            name='Like',
            slug='like',
            action_type='toggle'
        )

    def test_toggle_like_add(self):
        """Test adding a like"""
        result = EntityService.toggle_action(
            user=self.user,
            content_object=self.post,
            action_slug='like',
            store=self.store
        )

        self.assertEqual(result['action'], 'added')
        self.assertIsNotNone(result['interaction'])

    def test_toggle_like_remove(self):
        """Test removing a like"""
        # Add like first
        EntityService.toggle_action(
            user=self.user,
            content_object=self.post,
            action_slug='like',
            store=self.store
        )

        # Remove like
        result = EntityService.toggle_action(
            user=self.user,
            content_object=self.post,
            action_slug='like',
            store=self.store
        )

        self.assertEqual(result['action'], 'removed')
        self.assertIsNone(result['interaction'])
```

---

## 🔗 Integration Rules

### **Required Integrations**
- **accounts.md**: User authentication and permissions
- **stores.md**: Store scoping and multi-tenancy
- **logs.md**: Activity logging and audit trails

---

## 📈 Improvement Suggestions

### **Enhanced Features**
- **Action Groups**: Group related actions (Like/Dislike)
- **Conditional Actions**: Actions based on user roles
- **Action Chains**: Trigger multiple actions at once
- **Analytics Dashboard**: Track engagement metrics

---

## 🤖 AI Guidelines

### **Allowed Actions**
- **Recommendation Engine**: Suggest relevant actions
- **Engagement Analytics**: Generate insights from interaction data
- **Content Categorization**: Auto-categorize popular content

---

## 📅 Implementation Timeline

### **Phase 1: Core Infrastructure (Week 1)**
- Set up models and basic API endpoints
- Implement toggle functionality
- Create service layer

### **Phase 2: Features & Testing (Week 2)**
- Add statistics and analytics
- Implement security measures
- Create comprehensive tests

### **Phase 3: Integration & Polish (Week 3)**
- Integrate with existing modules
- Add caching and performance optimizations
- Complete documentation

<!-- ===============================================================================
 END ENTITIES.MD
 ================================================================================= -->


<!-- ===============================================================================
 START FORMS.MD
 ================================================================================= -->
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

<!-- ===============================================================================
 END FORMS.MD
 ================================================================================= -->


<!-- ===============================================================================
 START GIFTCARDS.MD
 ================================================================================= -->
# Gift Cards Module

## Overview
The Gift Cards module provides a comprehensive system for managing digital and physical gift cards, supporting multiple types, redemption flows, and deep e-commerce integration. This document outlines the architecture, models, services, and APIs required to implement this functionality.

## Table of Contents
1. [Architecture](#architecture)
2. [Models](#models)
3. [Services](#services)
4. [API Endpoints](#api-endpoints)
5. [Email Templates](#email-templates)
6. [Analytics](#analytics)
7. [E-commerce Integration](#e-commerce-integration)
8. [Security](#security)
9. [Performance](#performance)
10. [Testing](#testing)
11. [Deployment](#deployment)

## Architecture

### Key Components
- **GiftCard**: Core model representing a gift card with balance, status, and metadata
- **GiftCardHistory**: Audit trail for all gift card transactions
- **GiftCardService**: Business logic for gift card operations
- **GiftCardViewSet**: REST API endpoints
- **GiftCardEmailService**: Handles gift card email notifications
- **GiftCardAnalytics**: Tracks and reports on gift card usage

### Dependencies
- `ecommerce` for order integration
- `smtp` for email notifications
- `accounts` for user management
- `logs` for audit trails

## Models

### GiftCard
```python
class GiftCard(TenantModel):
    GIFT_CARD_TYPES = (
        ('digital', 'Digital'),
        ('physical', 'Physical'),
        ('promotional', 'Promotional'),
        ('refund', 'Refund'),
        ('loyalty', 'Loyalty'),
    )

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('redeemed', 'Redeemed'),
        ('expired', 'Expired'),
        ('voided', 'Voided'),
    )

    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    initial_balance = models.DecimalField(max_digits=10, decimal_places=2)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    gift_card_type = models.CharField(max_length=20, choices=GIFT_CARD_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    expires_at = models.DateTimeField(null=True, blank=True)
    sender_name = models.CharField(max_length=100, blank=True)
    sender_email = models.EmailField(blank=True)
    recipient_name = models.CharField(max_length=100, blank=True)
    recipient_email = models.EmailField(blank=True)
    message = models.TextField(blank=True)
    metadata = JSONField(default=dict, blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['status']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.current_balance}/{self.initial_balance} {self.currency}"

    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at

    def is_redeemable(self):
        return (
            self.status == 'active' and
            self.current_balance > 0 and
            not self.is_expired()
        )
```

### GiftCardHistory
```python
class GiftCardHistory(TenantModel):
    ACTION_CHOICES = (
        ('created', 'Created'),
        ('sent', 'Sent'),
        ('redeemed', 'Redeemed'),
        ('refunded', 'Refunded'),
        ('expired', 'Expired'),
        ('voided', 'Voided'),
    )

    gift_card = models.ForeignKey(GiftCard, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    order = models.ForeignKey('ecommerce.Order', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    metadata = JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Gift Card History'

    def __str__(self):
        return f"{self.gift_card.code} - {self.get_action_display()} - {self.amount if self.amount else ''}"
```

## Services

### GiftCardService
```python
class GiftCardService:
    @staticmethod
    @transaction.atomic
    def create_gift_card(store, created_by, **kwargs):
        """
        Create a new gift card with validation and history logging
        """
        # Generate unique code
        code = kwargs.get('code') or GiftCardService._generate_code()

        # Create gift card
        gift_card = GiftCardService.create_gift_card(
            store=store,
            created_by=created_by,
            code=code,
            **{k: v for k, v in kwargs.items() if k != 'code'}
        )

        # Log creation
        # Handled by GiftCardService.create_gift_card

        return gift_card

    @staticmethod
    @transaction.atomic
    def redeem_gift_card(code, amount, user=None, order=None, method='online'):
        """
        Redeem a gift card
        """
        gift_card = GiftCard.objects.get(code=code, status='active')
        if gift_card.is_expired():
            raise ValueError("Gift card has expired")

        if amount > gift_card.current_balance:
            raise ValueError("Insufficient balance")

        gift_card.current_balance -= amount
        gift_card.save()

        GiftCardHistory.objects.create(
            gift_card=gift_card,
            action='redeemed',
            amount=amount,
            order=order,
            created_by=user
        )

        return gift_card

    @staticmethod
    def get_gift_card_balance(code):
        """Get current balance of a gift card"""
        try:
            gift_card = GiftCard.objects.get(code=code, status='active')
            return {
                'code': gift_card.code,
                'balance': gift_card.current_balance,
                'currency': gift_card.currency,
                'is_expired': gift_card.is_expired()
            }
        except GiftCard.DoesNotExist:
            return None

    @staticmethod
    def _generate_code(length=12):
        """Generate a random gift card code"""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=length))

    @staticmethod
    def get_gift_card_analytics(store, start_date=None, end_date=None):
        """Generate analytics for gift cards"""
        return GiftCardQueryHelper.get_store_analytics(store, start_date, end_date)
```

## API Endpoints

### Base URL: `/api/v2/gift-cards/`

#### List/Search Gift Cards (GET)
- **Permissions**: `IsAuthenticated`, `IsStoreUser`
- **Query Params**:
  - `status`: Filter by status (active, redeemed, expired, voided)
  - `gift_card_type`: Filter by type (digital, physical, etc.)
  - `search`: Search by code, recipient name, or email
  - `expires_before`: Filter by expiration date
  - `ordering`: Sort field (-created_at, current_balance, etc.)

#### Create Gift Card (POST)
- **Permissions**: `IsAuthenticated`, `IsStoreUser`
- **Request Body**:
  ```json
  {
    "gift_card_type": "digital",
    "initial_balance": 100.00,
    "currency": "USD",
    "expires_at": "2024-12-31T23:59:59Z",
    "recipient_name": "John Doe",
    "recipient_email": "john@example.com",
    "message": "Enjoy your gift!",
    "metadata": {}
  }
  ```

#### Gift Card Detail (GET /{code})
- **Permissions**: `IsAuthenticated`, `IsStoreUser`
- **Response**:
  ```json
  {
    "code": "ABC123XYZ456",
    "gift_card_type": "digital",
    "initial_balance": "100.00",
    "current_balance": "100.00",
    "currency": "USD",
    "status": "active",
    "expires_at": "2024-12-31T23:59:59Z",
    "recipient_name": "John Doe",
    "recipient_email": "john@example.com",
    "created_at": "2023-01-15T10:30:00Z",
    "history": [
      {
        "action": "created",
        "amount": "100.00",
        "created_at": "2023-01-15T10:30:00Z"
      }
    ]
  }
  ```

#### Redeem Gift Card (POST /{code}/redeem)
- **Permissions**: `IsAuthenticated` (for online) or API key (for in-store)
- **Request Body**:
  ```json
  {
    "amount": 25.50,
    "order_id": "ORD-12345",
    "method": "online" // or "in_store"
  }
  ```

## Email Templates

### Gift Card Purchased
- **Trigger**: When a new gift card is purchased
- **Recipients**: Sender (confirmation) and Recipient (gift card)
- **Variables**:
  - `gift_card_code`
  - `recipient_name`
  - `sender_name`
  - `message`
  - `amount`
  - `expiration_date`
  - `redeem_url`

### Gift Card Redeemed
- **Trigger**: When a gift card is used
- **Recipients**: Sender (notification)
- **Variables**:
  - `gift_card_code`
  - `amount_used`
  - `remaining_balance`
  - `order_id`
  - `redemption_date`

## Analytics

### Key Metrics
1. **Redemption Rate**: Percentage of issued gift cards that have been redeemed
2. **Breakage**: Value of unredeemed gift cards
3. **Average Order Value (AOV)**: For orders using gift cards
4. **Popular Gift Card Types**: Distribution across different types
5. **Time to Redemption**: Average time between issuance and first use

### Sample Queries
```python
# Redemption rate
total_issued = GiftCard.objects.filter(store=store).count()
redeemed = GiftCard.objects.filter(store=store, status='redeemed').count()
redemption_rate = (redeemed / total_issued) * 100 if total_issued > 0 else 0

# Breakage
breakage = GiftCard.objects.filter(
    store=store,
    status='active',
    expires_at__lt=timezone.now()
).aggregate(total=Sum('current_balance'))['total'] or 0

# Average Order Value with Gift Cards
from django.db.models import Avg, F
orders_with_gift_cards = Order.objects.filter(
    store=store,
    gift_card_history__isnull=False
).annotate(
    gift_card_total=Sum('gift_card_history__amount')
).aggregate(
    avg_order_value=Avg(F('total') + F('gift_card_total'))
)
```

## E-commerce Integration

### Cart Application Flow
1. Customer applies gift card code to cart
2. System validates code and checks balance
3. If valid, apply discount to order total
4. Store gift card usage in session until checkout

### Order Processing
1. On order completion, redeem gift card amount
2. Create GiftCardHistory entry linked to order
3. Update gift card balance
4. Send redemption confirmation if balance remains

### Refunds
1. If order is refunded, optionally refund amount to gift card
2. Create new gift card with refunded amount
3. Link to original order for tracking

## Security

### Rate Limiting
- 5 redemption attempts per minute per IP
- 10 gift card lookups per minute per user

### Validation
- Validate gift card codes against regex pattern
- Prevent duplicate codes
- Enforce minimum/maximum gift card values

### Access Control
- Store staff can view all gift cards
- Customers can only view their own gift cards
- API keys required for in-store redemption

## Performance

### Caching
- Cache gift card balances for 5 minutes
- Cache gift card validation results for 1 minute
- Use cache stampede protection

### Database Optimization
- Index on code, status, expires_at
- Select related for common queries
- Use `only()` and `defer()` to limit field selection

### Background Tasks
- Send emails asynchronously
- Process batch operations in background
- Schedule expiration checks

## Testing

### Unit Tests
- Gift card creation and validation
- Balance calculations
- Expiration logic
- Redemption scenarios

### Integration Tests
- API endpoints
- E-commerce flow
- Email delivery
- Concurrent redemptions

### Performance Tests
- Load testing for high-volume redemption
- Stress testing for concurrent access

## Deployment

### Migrations
```python
# 0001_initial.py
class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('ecommerce', '0001_initial'),
        ('accounts', '0001_initial'),
        ('stores', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GiftCard',
            fields=[
                # Model fields
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['code'], name='giftcards_g_code_123456_idx'),
                    models.Index(fields=['status'], name='giftcards_g_status_123456_idx'),
                    models.Index(fields=['expires_at'], name='giftcards_g_expires_123456_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='GiftCardHistory',
            fields=[
                # Model fields
            ],
            options={
                'ordering': ['-created_at'],
                'verbose_name_plural': 'Gift Card History',
            },
        ),
    ]
```

### Required Environment Variables
```bash
# Gift card settings
GIFT_CARD_CODE_LENGTH=12
GIFT_CARD_CODE_PREFIX=GC
GIFT_CARD_EXPIRY_DAYS=365
GIFT_CARD_MIN_AMOUNT=10.00
GIFT_CARD_MAX_AMOUNT=1000.00
```

### Monitoring
- Track gift card creation and redemption rates
- Monitor for failed redemption attempts
- Alert on suspicious activity

## Implementation Checklist

### Phase 1: Core Functionality
- [ ] Create GiftCard and GiftCardHistory models
- [ ] Implement GiftCardService with basic CRUD operations
- [ ] Create API endpoints for gift card management
- [ ] Add unit tests for core functionality

### Phase 2: E-commerce Integration
- [ ] Integrate with cart/checkout flow
- [ ] Implement order processing hooks
- [ ] Add refund handling
- [ ] Create integration tests

### Phase 3: Email & Notifications
- [ ] Design email templates
- [ ] Implement email sending
- [ ] Add notification preferences

### Phase 4: Analytics & Reporting
- [ ] Implement analytics queries
- [ ] Create admin reports
- [ ] Set up monitoring

### Phase 5: Optimization
- [ ] Add caching
- [ ] Optimize database queries
- [ ] Implement background tasks

## Future Enhancements
1. Bulk import/export of gift cards
2. Gift card categories with different rules
3. Scheduled gift card delivery
4. Multi-currency support
5. Gift card marketplaces
6. Loyalty program integration

<!-- ===============================================================================
 END GIFTCARDS.MD
 ================================================================================= -->


<!-- ===============================================================================
 START LOGS.MD
================================================================================ -->
# Logs App Rules - DFCMS Compatible

## 🎯 Purpose
This document defines strict development rules for the **logs** app in CMS-Updated backend, implementing a unified, store-scoped audit logging system for all modules.

## 🏗️ Logs App Structure
```
apps/logs/
├── __init__.py
├── apps.py
├── models.py                    # Single LogEntry model
├── admin.py
├── middleware.py                 # Auto-request logging
├── signals.py                   # Auto-model change logging
├── services.py                  # Business logic
├── tasks.py                     # Celery async tasks
├── management/
│   └── commands/
│       └── migrate_logs.py      # Legacy migration command
├── migrations/
├── v2/
│   ├── __init__.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_services.py
│   └── test_views.py
└── api.md                       # API documentation
```

## 🧾 Authority
- Owner: Backend Lead
- Enforced By: models.py, services.py, middleware, views
- Scope: Store-scoped

## 📋 Core Models
```python
# apps/logs/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import TenantModel

User = get_user_model()

class LogEntry(TenantModel):
    # Event types - unified for all logging
    EVENT_TYPES = [
        # System
        ('SYSTEM_STARTUP', 'System Startup'),
        ('SYSTEM_ERROR', 'System Error'),

        # User actions
        ('USER_LOGIN', 'User Login'),
        ('USER_LOGOUT', 'User Logout'),
        ('USER_REGISTER', 'User Registration'),
        ('PASSWORD_CHANGE', 'Password Change'),
        ('PASSWORD_RESET', 'Password Reset'),

        # Content actions
        ('CONTENT_CREATE', 'Content Created'),
        ('CONTENT_UPDATE', 'Content Updated'),
        ('CONTENT_DELETE', 'Content Deleted'),
        ('CONTENT_PUBLISH', 'Content Published'),

        # Visitor analytics
        ('PAGE_VIEW', 'Page View'),
        ('CLICK', 'Click Event'),
        ('FORM_SUBMIT', 'Form Submit'),
        ('FILE_DOWNLOAD', 'File Download'),
        ('BOUNCE', 'Bounce (quick exit)'),

        # Security
        ('LOGIN_FAILED', 'Failed Login'),
        ('SUSPICIOUS_ACTIVITY', 'Suspicious Activity'),
        ('RATE_LIMIT', 'Rate Limit Exceeded'),
        ('BLOCKED_IP', 'IP Blocked'),

        # API
        ('API_CALL', 'API Call'),
        ('API_ERROR', 'API Error'),
    ]

    LOG_LEVELS = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]

    # Core fields
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    level = models.CharField(max_length=20, choices=LOG_LEVELS, default='INFO')
    message = models.TextField(blank=True)

    # User tracking
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    session_id = models.CharField(max_length=100, blank=True)  # For anonymous visitors

    # Request tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_id = models.CharField(max_length=100, blank=True)

    # Event details
    entity_type = models.CharField(max_length=100, blank=True)  # 'Product', 'Order', etc.
    entity_id = models.PositiveIntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict)  # Flexible event data

    # Analytics
    page_url = models.URLField(blank=True)
    referrer = models.URLField(blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    # Security
    is_suspicious = models.BooleanField(default=False)
    risk_score = models.PositiveSmallIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta(TenantModel.Meta):
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['store', 'event_type', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['session_id']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['is_suspicious']),
        ]

    def __str__(self):
        return f"{self.store.name} - {self.event_type} - {self.created_at}"
```

## 🧠 Auto-Logging Implementation

### 3.1 Request Logging Middleware
```python
# apps/logs/middleware.py
import time
import uuid
from django.utils import timezone
from .models import LogEntry
from .tasks import log_event_async

class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip static files and admin
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return self.get_response(request)

        # Generate request ID
        request.request_id = str(uuid.uuid4())
        start_time = time.time()

        response = self.get_response(request)

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Log page view asynchronously
        log_data = {
            'event_type': 'PAGE_VIEW',
            'level': 'INFO',
            'message': f"Page view: {request.path}",
            'store': getattr(request, 'store', None),
            'user': request.user if request.user.is_authenticated else None,
            'session_id': request.session.session_key,
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'request_id': request.request_id,
            'page_url': request.build_absolute_uri(),
            'referrer': request.META.get('HTTP_REFERER', ''),
            'duration_ms': duration_ms,
            'metadata': {
                'method': request.method,
                'status_code': response.status_code,
                'query_params': dict(request.GET),
            }
        }

        # Use async for performance
        log_event_async.delay(log_data)

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
```

### 3.2 Model Change Signals
```python
# apps/logs/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .tasks import log_event_async

@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    # Skip logging models and system models
    if sender._meta.app_label in ['logs', 'sessions', 'admin', 'contenttypes']:
        return

    event_type = 'CONTENT_CREATE' if created else 'CONTENT_UPDATE'

    log_data = {
        'event_type': event_type,
        'level': 'INFO',
        'message': f"{'Created' if created else 'Updated'} {sender.__name__} #{instance.pk}",
        'entity_type': sender.__name__,
        'entity_id': instance.pk,
        'metadata': {
            'created': created,
            'changed_fields': getattr(instance, '_changed_fields', {}),
        }
    }

    # Add store if model has it
    if hasattr(instance, 'store'):
        log_data['store'] = instance.store

    log_event_async.delay(log_data)

@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    if sender._meta.app_label in ['logs', 'sessions', 'admin', 'contenttypes']:
        return

    log_data = {
        'event_type': 'CONTENT_DELETE',
        'level': 'WARNING',
        'message': f"Deleted {sender.__name__} #{instance.pk}",
        'entity_type': sender.__name__,
        'entity_id': instance.pk,
        'metadata': {}
    }

    if hasattr(instance, 'store'):
        log_data['store'] = instance.store

    log_event_async.delay(log_data)
```

### 3.3 Client-Side Event Tracking
```python
# apps/logs/v2/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .tasks import log_event_async

@api_view(['POST'])
@permission_classes([AllowAny])
def track_event(request):
    """Track client-side events (clicks, hovers, etc.)"""
    try:
        event_data = {
            'event_type': request.data.get('event_type', 'CLICK'),
            'level': 'INFO',
            'message': request.data.get('message', ''),
            'store': getattr(request, 'store', None),
            'user': request.user if request.user.is_authenticated else None,
            'session_id': request.session.session_key,
            'ip_address': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'page_url': request.data.get('page_url', ''),
            'metadata': request.data.get('metadata', {}),
        }

        log_event_async.delay(event_data)
        return Response({'status': 'logged'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

## 4. Services
```python
# apps/logs/services.py
from datetime import timedelta
from django.db.models import Count, Q, Avg
from django.utils import timezone
from .models import LogEntry

class LogService:
    @staticmethod
    def get_store_analytics(store, days=30):
        """Get analytics for a store"""
        since = timezone.now() - timedelta(days=days)

        # Basic metrics
        total_visits = LogEntry.objects.filter(
            store=store,
            event_type='PAGE_VIEW',
            created_at__gte=since
        ).count()

        unique_visitors = LogEntry.objects.filter(
            store=store,
            event_type='PAGE_VIEW',
            created_at__gte=since
        ).values('session_id').distinct().count()

        # Bounce rate (single page view sessions)
        bounce_sessions = LogEntry.objects.filter(
            store=store,
            event_type='PAGE_VIEW',
            created_at__gte=since
        ).values('session_id').annotate(
            page_views=Count('id')
        ).filter(page_views=1).count()

        total_sessions = LogEntry.objects.filter(
            store=store,
            event_type='PAGE_VIEW',
            created_at__gte=since
        ).values('session_id').distinct().count()

        bounce_rate = (bounce_sessions / total_sessions * 100) if total_sessions > 0 else 0

        # Top pages
        top_pages = LogEntry.objects.filter(
            store=store,
            event_type='PAGE_VIEW',
            created_at__gte=since
        ).values('page_url').annotate(
            views=Count('id')
        ).order_by('-views')[:10]

        # Security events
        security_events = LogEntry.objects.filter(
            store=store,
            is_suspicious=True,
            created_at__gte=since
        ).count()

        return {
            'total_visits': total_visits,
            'unique_visitors': unique_visitors,
            'bounce_rate': round(bounce_rate, 2),
            'top_pages': list(top_pages),
            'security_events': security_events,
            'period_days': days,
        }

    @staticmethod
    def detect_suspicious_activity(store, hours=24):
        """Detect suspicious patterns"""
        since = timezone.now() - timedelta(hours=hours)

        suspicious = []

        # Failed logins from same IP
        failed_logins = LogEntry.objects.filter(
            store=store,
            event_type='LOGIN_FAILED',
            created_at__gte=since
        ).values('ip_address').annotate(
            count=Count('id')
        ).filter(count__gt=5)

        for item in failed_logins:
            suspicious.append({
                'type': 'brute_force',
                'ip': item['ip_address'],
                'count': item['count'],
                'risk_score': min(100, item['count'] * 10),
            })

        # Unusual page access patterns
        rapid_requests = LogEntry.objects.filter(
            store=store,
            event_type='PAGE_VIEW',
            created_at__gte=since
        ).values('ip_address').annotate(
            count=Count('id')
        ).filter(count__gt=1000)

        for item in rapid_requests:
            suspicious.append({
                'type': 'bot_activity',
                'ip': item['ip_address'],
                'count': item['count'],
                'risk_score': min(100, item['count'] // 10),
            })

        return suspicious
```

## 5. Celery Tasks
```python
# apps/logs/tasks.py
from celery import shared_task
from .models import LogEntry

@shared_task
def log_event_async(log_data):
    """Async logging to avoid blocking requests"""
    try:
        LogEntry.objects.create(**log_data)
    except Exception as e:
        # Fallback to sync logging if async fails
        LogEntry.objects.create(**log_data)
        # Log the error
        print(f"Async logging failed: {e}")

@shared_task
def cleanup_old_logs(days=90):
    """Clean up old logs to prevent table bloat"""
    from datetime import timedelta
    from django.utils import timezone

    cutoff = timezone.now() - timedelta(days=days)
    deleted_count = LogEntry.objects.filter(created_at__lt=cutoff).delete()[0]
    return f"Deleted {deleted_count} old log entries"
```

## 6. API Endpoints
```python
# apps/logs/v2/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.LogEntryViewSet.as_view({'get': 'list'}), name='log-list'),
    path('<int:pk>/', views.LogEntryViewSet.as_view({'get': 'retrieve'}), name='log-detail'),
    path('analytics/', views.StoreAnalyticsView.as_view(), name='store-analytics'),
    path('security/', views.SecurityEventsView.as_view(), name='security-events'),
    path('track-event/', views.track_event, name='track-event'),
]
```

## 7. Migration from Legacy Activity Logs
```python
# apps/logs/management/commands/migrate_logs.py
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.logs.models import LogEntry

class Command(BaseCommand):
    help = 'Migrate old activity_logs to new logs system'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be migrated')
        parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for migration')

    def handle(self, *args, **options):
        from apps.activity_logs.models import ActivityLog  # Old model

        queryset = ActivityLog.objects.all().order_by('id')
        batch_size = options['batch_size']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(f"Would migrate {queryset.count()} records")
            return

        migrated = 0
        for i in range(0, queryset.count(), batch_size):
            batch = queryset[i:i + batch_size]

            with transaction.atomic():
                for old_log in batch:
                    # Map old action to new event_type
                    event_type = self.map_action_to_event_type(old_log.action)

                    LogEntry.objects.create(
                        store=old_log.storeId,
                        user=old_log.userId,
                        event_type=event_type,
                        level='INFO',
                        message=old_log.descriptions,
                        ip_address=old_log.ipAddress,
                        user_agent=old_log.userAgent,
                        entity_type=old_log.entityType,
                        entity_id=old_log.entityId,
                        metadata=old_log.metadata or {},
                        created_at=old_log.createdAt,
                    )
                    migrated += 1

            self.stdout.write(f"Migrated {migrated} records...")

        self.stdout.write(self.style.SUCCESS(f"Successfully migrated {migrated} log entries"))

    def map_action_to_event_type(self, old_action):
        """Map old action choices to new event types"""
        mapping = {
            'login': 'USER_LOGIN',
            'logout': 'USER_LOGOUT',
            'create': 'CONTENT_CREATE',
            'update': 'CONTENT_UPDATE',
            'delete': 'CONTENT_DELETE',
            # Add more mappings as needed
        }
        return mapping.get(old_action, 'SYSTEM_ERROR')
```

## 8. Testing Rules
```python
# apps/logs/tests/test_models.py
import pytest
from django.test import TestCase
from apps.logs.models import LogEntry

class TestLogEntry(TestCase):
    def test_create_log_entry(self):
        log = LogEntry.objects.create(
            store=self.store,
            event_type='PAGE_VIEW',
            message='Test page view',
            ip_address='192.168.1.1'
        )
        self.assertEqual(log.event_type, 'PAGE_VIEW')
        self.assertEqual(log.level, 'INFO')

    def test_str_representation(self):
        log = LogEntry.objects.create(
            store=self.store,
            event_type='USER_LOGIN',
            message='User logged in'
        )
        expected = f"{self.store.name} - USER_LOGIN - {log.created_at}"
        self.assertEqual(str(log), expected)
```

## 9. Settings Configuration
```python
# settings.py
INSTALLED_APPS += ['apps.logs']

# Middleware - add after authentication
MIDDLEWARE = [
    ...
    'apps.logs.middleware.LoggingMiddleware',
    ...
]

# Celery for async logging
CELERY_BEAT_SCHEDULE = {
    'cleanup-old-logs': {
        'task': 'apps.logs.tasks.cleanup_old_logs',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}

# Log retention
LOG_RETENTION_DAYS = 90
```

## 10. API Documentation (api.md)
```markdown
# Logs API Documentation

## Base URL
```
/v2/api/logs/
```

## Endpoints

### GET /v2/api/logs/
List log entries with filtering
- Query params: store, event_type, level, user, date_from, date_to

### GET /v2/api/logs/analytics/
Store analytics dashboard data
- Returns: visits, visitors, bounce_rate, top_pages, security_events

### GET /v2/api/logs/security/
Security events and suspicious activity
- Returns: detected threats, risk scores, recommendations

### POST /v2/api/logs/track-event/
Track client-side events
- Body: {event_type, message, page_url, metadata}
```

## 🔒 Security
Enforced At: models.py, services.py, middleware, views
- MUST NOT log sensitive PII (passwords, credit cards) in clear text
- MUST enforce store isolation on all queries
- MUST validate and sanitize all log metadata
- MUST use rate limiting on public logging endpoints

## 🧪 Testing
- Unit tests MUST cover LogEntry creation, event type validation, and tenant isolation
- Integration tests MUST validate middleware auto-logging and Celery async tasks
- Regression tests MUST ensure no PII leakage in logs and proper cleanup
- Coverage MUST be >= 95%

## 🚫 Forbidden Patterns
- MUST NOT use synchronous logging in request/response paths
- MUST NOT bypass tenant filtering in log queries
- MUST NOT store raw request bodies without sanitization
- MUST NOT expose log entries across tenant boundaries

## 🔗 Cross-References
- accounts.md for user scoping and authentication events
- cache.md for log aggregation and caching strategies
- media.md for file download logging

## 11. Performance Notes
- All logging is async via Celery
- Database indexes on frequently queried fields
- Automatic cleanup of old logs
- Batch operations for migrations

## 12. Security Notes
- IP addresses are logged but can be anonymized
- No sensitive data in metadata
- Rate limiting on track-event endpoint
- Store-scoped queries prevent data leaks

<!-- ===============================================================================
 END LOGS.MD
 ================================================================================= -->


<!-- ===============================================================================
 START MEDIAFILE.MD
 ================================================================================= -->
# Media App Rules - Cloudflare R2 + ImageKit.io

## Directory Structure
```
mediafile/
├── __init__.py
├── apps.py
├── models/
│   ├── __init__.py
│   ├── media_file.py
│   └── media_folder.py
├── services/
│   ├── __init__.py
│   ├── media_service.py
│   └── imagekit_service.py
├── tasks.py
├── admin.py
├── signals.py
├── exceptions.py
└── v2/
    ├── __init__.py
    ├── urls.py
    ├── serializers/
    │   ├── __init__.py
    │   ├── media_file.py
    │   └── media_folder.py
    └── views/
        ├── __init__.py
        ├── media_views.py
        └── folder_views.py
```

## Core Models

### MediaFile
```python
# media/models/media_file.py
import os
from django.db import models
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from django.conf import settings

class MediaFile(models.Model):
    """
    Represents a media file stored in Cloudflare R2 with ImageKit.io processing.
    """
    # File types and size limits (in bytes)
    IMAGE_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    VIDEO_MAX_SIZE = 100 * 1024 * 1024  # 100MB
    DOCUMENT_MAX_SIZE = 20 * 1024 * 1024  # 20MB

    RESOURCE_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('other', 'Other')
    ]

    # Core fields
    original_filename = models.CharField(max_length=255)
    file_extension = models.CharField(max_length=10)
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)

    # R2 storage path (format: store_{id}/media/{folder_path}/filename.xxx)
    storage_path = models.CharField(max_length=512)

    # ImageKit.io specific
    imagekit_id = models.CharField(max_length=255, blank=True, null=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)

    # Metadata
    alt_text = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    # Relations
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='media_files')
    folder = models.ForeignKey(
        'mediaFile.MediaFolder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='media_files'
    )
    uploaded_by = models.ForeignKey(
        'accounts.UserAccount',
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_files'
    )

    # Reverse relationships for user media
    # These are defined here for documentation and type hinting
    user_avatars = models.ManyToManyField(
        'accounts.UserAccount',
        related_name='avatar_media',
        blank=True,
        help_text="Users who use this file as their avatar"
    )
    user_cover_photos = models.ManyToManyField(
        'accounts.UserAccount',
        related_name='cover_photo_media',
        blank=True,
        help_text="Users who use this file as their cover photo"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['store', 'resource_type']),
            models.Index(fields=['store', 'folder']),
            models.Index(fields=['created_at']),
            models.Index(fields=['file_size']),
        ]

    def __str__(self):
        return self.original_filename

    @property
    def file_size_formatted(self):
        """Return human-readable file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} GB"

    @property
    def is_image(self):
        return self.resource_type == 'image'

    @property
    def is_video(self):
        return self.resource_type == 'video'

    @property
    def is_document(self):
        return self.resource_type == 'document'

    def get_absolute_url(self, transformation=None):
        """
        Get the public URL for this media file with optional transformations

        Args:
            transformation (str, optional): ImageKit transformation string

        Returns:
            str: Public URL with transformations applied
        """
        from .services.media_service import MediaService
        return MediaService().get_media_url(self, transformation)

    def get_thumbnail_url(self, width=200, height=200, crop='fill'):
        """
        Get a thumbnail URL for this media file

        Args:
            width (int): Width in pixels
            height (int): Height in pixels
            crop (str): Crop mode (fill, fit, etc.)

        Returns:
            str: Thumbnail URL or None if not applicable
        """
        if not self.is_image and not self.is_video:
            return None

        transformation = f'tr:w-{width},h-{height},c-{crop}'
        return self.get_absolute_url(transformation)

    def get_presigned_url(self, expires_in=3600):
        """
        Generate a presigned URL for private file access

        Args:
            expires_in (int): Expiration time in seconds

        Returns:
            str: Presigned URL or None if not applicable
        """
        from .services.media_service import MediaService
        return MediaService().get_presigned_url(self, expires_in)
```

### MediaFolder
```python
# media/models/media_folder.py
from django.db import models
from django.utils.text import slugify

class MediaFolder(models.Model):
    """
    Represents a folder for organizing media files within a store.
    Supports nested folder structure.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='media_folders')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created_by = models.ForeignKey('accounts.UserAccount', on_delete=models.SET_NULL, null=True, related_name='created_folders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('store', 'parent', 'slug')
        ordering = ['name']
        indexes = [
            models.Index(fields=['store']),
            models.Index(fields=['parent']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def path(self):
        """Get full folder path as string"""
        if self.parent:
            return f"{self.parent.path}/{self.slug}"
        return self.slug
```

## Service Layer

### MediaService
```python
# media/services/media_service.py
import os
import mimetypes
import logging
from urllib.parse import urljoin
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
import boto3
from botocore.exceptions import ClientError
import imagekit
from imagekitio import ImageKit

from ..models.media_file import MediaFile
from ..models.media_folder import MediaFolder
from ..exceptions import (
    MediaUploadError,
    InvalidFileTypeError,
    FileTooLargeError,
    StorageError
)

logger = logging.getLogger(__name__)

class MediaService:
    """
    Service class for handling media file operations with Cloudflare R2 and ImageKit.io
    """

    # Allowed MIME types and their corresponding resource types
    ALLOWED_MIME_TYPES = {
        'image': [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'image/svg+xml', 'image/tiff', 'image/bmp'
        ],
        'video': [
            'video/mp4', 'video/webm', 'video/ogg', 'video/quicktime',
            'video/x-msvideo', 'video/x-ms-wmv', 'video/x-matroska'
        ],
        'document': [
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'text/plain', 'text/csv', 'application/rtf',
            'application/zip', 'application/x-rar-compressed',
            'application/x-7z-compressed', 'application/x-tar',
            'application/x-gzip'
        ]
    }

    def __init__(self):
        """Initialize R2 and ImageKit clients"""
        # Initialize R2 client
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name='auto',
            config=boto3.session.Config(signature_version='s3v4')
        )

        # Initialize ImageKit
        self.imagekit = ImageKit(
            private_key=settings.IMAGEKIT_PRIVATE_KEY,
            public_key=settings.IMAGEKIT_PUBLIC_KEY,
            url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
        )

    def upload_file(self, file_obj, store, user, folder=None, metadata=None):
        """
        Upload a file to R2 and create a MediaFile record

        Args:
            file_obj: File object or InMemoryUploadedFile
            store: Store instance
            user: UserAccount instance
            folder: Optional MediaFolder instance
            metadata: Optional dict of metadata

        Returns:
            MediaFile: Created media file instance

        Raises:
            InvalidFileTypeError: If file type is not allowed
            FileTooLargeError: If file exceeds size limits
            StorageError: If upload to R2 fails
            MediaUploadError: For other upload errors
        """
        try:
            # Validate file
            if not file_obj or not hasattr(file_obj, 'name'):
                raise MediaUploadError("Invalid file object")

            # Get file metadata
            file_name = file_obj.name
            file_size = file_obj.size
            mime_type = getattr(file_obj, 'content_type',
                              mimetypes.guess_type(file_name)[0] or 'application/octet-stream')

            # Determine resource type and validate
            resource_type = self._get_resource_type(mime_type, file_name)
            if not resource_type:
                raise InvalidFileTypeError(
                    f"File type {mime_type} is not allowed. "
                    f"Allowed types: {', '.join(self.ALLOWED_MIME_TYPES.keys())}"
                )

            # Validate file size
            max_size = getattr(MediaFile, f"{resource_type.upper()}_MAX_SIZE")
            if file_size > max_size:
                raise FileTooLargeError(
                    f"{resource_type.capitalize()} exceeds maximum size of "
                    f"{max_size / (1024 * 1024):.1f}MB"
                )

            # Generate storage path
            file_extension = os.path.splitext(file_name)[1].lower()
            base_filename = os.path.splitext(os.path.basename(file_name))[0]
            safe_filename = f"{slugify(base_filename)}{file_extension}"

            # Create folder path
            folder_path = f"store_{store.id}/media"
            if folder:
                folder_path = f"{folder_path}/{folder.path}"

            # Upload to R2
            r2_key = f"{folder_path}/{safe_filename}"

            try:
                if hasattr(file_obj, 'temporary_file_path'):
                    # File is stored on disk
                    self.s3_client.upload_file(
                        file_obj.temporary_file_path(),
                        settings.AWS_STORAGE_BUCKET_NAME,
                        r2_key,
                        ExtraArgs={
                            'ContentType': mime_type,
                            'ACL': 'public-read' if resource_type in ['image', 'video'] else 'private'
                        }
                    )
                else:
                    # File is in memory
                    self.s3_client.upload_fileobj(
                        file_obj,
                        settings.AWS_STORAGE_BUCKET_NAME,
                        r2_key,
                        ExtraArgs={
                            'ContentType': mime_type,
                            'ACL': 'public-read' if resource_type in ['image', 'video'] else 'private'
                        }
                    )
            except ClientError as e:
                logger.error(f"Failed to upload to R2: {str(e)}")
                raise StorageError("Failed to upload file to storage")

            # Get file dimensions if image
            width, height = None, None
            if resource_type == 'image':
                try:
                    from PIL import Image
                    if hasattr(file_obj, 'temporary_file_path'):
                        with Image.open(file_obj.temporary_file_path()) as img:
                            width, height = img.size
                    else:
                        # For in-memory files, we need to seek to start
                        file_obj.seek(0)
                        with Image.open(file_obj) as img:
                            width, height = img.size
                        # Reset file pointer for potential reuse
                        file_obj.seek(0)
                except Exception as e:
                    logger.warning(f"Could not get image dimensions: {str(e)}")

            # Create MediaFile record
            media_file = MediaFile.objects.create(
                original_filename=file_name,
                file_extension=file_extension.lstrip('.'),
                file_size=file_size,
                mime_type=mime_type,
                resource_type=resource_type,
                storage_path=r2_key,
                width=width,
                height=height,
                store=store,
                folder=folder,
                uploaded_by=user,
                metadata=metadata or {}
            )

            # Register with ImageKit for images and videos
            if resource_type in ['image', 'video']:
                try:
                    # Get public URL from R2
                    public_url = f"{settings.AWS_S3_PUBLIC_URL}/{r2_key}"

                    # Upload to ImageKit
                    result = self.imagekit.upload(
                        file=public_url,
                        file_name=safe_filename,
                        options={
                            'folder': folder_path,
                            'is_private_file': False,
                            'use_unique_file_name': False,
                            'response_fields': ['url', 'fileId']
                        }
                    )

                    # Update MediaFile with ImageKit ID
                    media_file.imagekit_id = result['fileId']
                    media_file.save(update_fields=['imagekit_id'])

                except Exception as e:
                    logger.error(f"Failed to register with ImageKit: {str(e)}")
                    # Don't fail the upload, just log the error

            # Log the upload
            self._log_media_action(
                action='UPLOAD',
                user=user,
                store=store,
                media_file=media_file,
                metadata={
                    'file_size': file_size,
                    'mime_type': mime_type,
                    'folder': folder.name if folder else None
                }
            )

            return media_file

        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            if not isinstance(e, (InvalidFileTypeError, FileTooLargeError, StorageError)):
                raise MediaUploadError(f"Failed to upload file: {str(e)}")
            raise

    def delete_media(self, media_file, user):
        """
        Delete a media file from storage and database

        Args:
            media_file: MediaFile instance to delete
            user: UserAccount performing the deletion

        Returns:
            bool: True if deletion was successful
        """
        try:
            store = media_file.store

            # Delete from R2
            try:
                self.s3_client.delete_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=media_file.storage_path
                )
            except ClientError as e:
                logger.error(f"Failed to delete from R2: {str(e)}")
                # Continue with DB deletion even if R2 delete fails

            # Delete from ImageKit if it exists
            if media_file.imagekit_id:
                try:
                    self.imagekit.delete_file(media_file.imagekit_id)
                except Exception as e:
                    logger.error(f"Failed to delete from ImageKit: {str(e)}")

            # Log before deletion (to have the ID)
            self._log_media_action(
                action='DELETE',
                user=user,
                store=store,
                media_file=media_file
            )

            # Delete from database
            media_file.delete()

            return True

        except Exception as e:
            logger.error(f"Error deleting media file {media_file.id}: {str(e)}")
            raise MediaUploadError(f"Failed to delete media file: {str(e)}")

    def get_media_url(self, media_file, transformation=None):
        """
        Get URL for a media file with optional transformations

        Args:
            media_file: MediaFile instance
            transformation: Optional transformation string for ImageKit

        Returns:
            str: Public URL to the media file
        """
        if not media_file:
            return None

        # For private files, generate a presigned URL
        if media_file.resource_type not in ['image', 'video']:
            return self.get_presigned_url(media_file)

        # For public files, use ImageKit if available
        if media_file.imagekit_id:
            try:
                url = f"{settings.IMAGEKIT_URL}/{media_file.storage_path}"
                if transformation:
                    url = f"{url}?tr={transformation}"
                return url
            except Exception as e:
                logger.warning(f"Failed to get ImageKit URL: {str(e)}")
                # Fall back to R2 URL

        # Fallback to R2 public URL
        return f"{settings.AWS_S3_PUBLIC_URL}/{media_file.storage_path}"

    def get_presigned_url(self, media_file, expires_in=3600):
        """
        Generate a presigned URL for private file access

        Args:
            media_file: MediaFile instance
            expires_in: Expiration time in seconds

        Returns:
            str: Presigned URL or None if not applicable
        """
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': media_file.storage_path,
                    'ResponseContentType': media_file.mime_type,
                    'ResponseContentDisposition': f'attachment; filename="{media_file.original_filename}"'
                },
                ExpiresIn=expires_in
            )
            return response
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            return None

    def get_thumbnail_url(self, media_file, width=200, height=200, crop='fill'):
        """
        Get a thumbnail URL for a media file

        Args:
            media_file: MediaFile instance
            width: Thumbnail width in pixels
            height: Thumbnail height in pixels
            crop: Crop mode (fill, fit, etc.)

        Returns:
            str: Thumbnail URL or None if not applicable
        """
        if not media_file or media_file.resource_type not in ['image', 'video']:
            return None

        transformation = f'w-{width},h-{height},c-{crop}'
        return self.get_media_url(media_file, transformation)

    def _get_resource_type(self, mime_type, file_name):
        """
        Determine resource type from MIME type and file name

        Args:
            mime_type: MIME type string
            file_name: Original file name

        Returns:
            str: Resource type (image, video, document, other) or None if not allowed
        """
        if not mime_type:
            # Try to determine from file extension as fallback
            ext = os.path.splitext(file_name)[1].lower().lstrip('.')
            mime_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'

        for resource_type, allowed_mimes in self.ALLOWED_MIME_TYPES.items():
            if mime_type in allowed_mimes:
                return resource_type

        return None

    def _log_media_action(self, action, user, store, media_file, metadata=None):
        """
        Log media-related actions to the activity log

        Args:
            action: Action type (UPLOAD, DELETE, etc.)
            user: UserAccount performing the action
            store: Store the action belongs to
            media_file: MediaFile being acted upon
            metadata: Additional metadata to include in the log
        """
        from logs.services.log_service import log_event_async

        log_data = {
            'event_type': 'MEDIA_' + action,
            'message': f"Media file {action.lower()}: {media_file.original_filename}",
            'user': user,
            'store': store,
            'entity_type': 'MediaFile',
            'entity_id': media_file.id,
            'metadata': {
                'file_size': media_file.file_size,
                'mime_type': media_file.mime_type,
                'resource_type': media_file.resource_type,
                'folder': media_file.folder.name if media_file.folder else None,
                **(metadata or {})
            }
        }

        log_event_async.delay(log_data)
```

### ImageKitService (Optional)
```python
# media/services/imagekit_service.py
from imagekitio import ImageKit
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ImageKitService:
    """
    Service class for advanced ImageKit.io operations
    """

    def __init__(self):
        self.client = ImageKit(
            private_key=settings.IMAGEKIT_PRIVATE_KEY,
            public_key=settings.IMAGEKIT_PUBLIC_KEY,
            url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
        )

    def get_transformed_url(self, image_url, transformations):
        """
        Get URL for an image with transformations applied

        Args:
            image_url: Source image URL
            transformations: List of transformation dicts
                Example: [{"height": 300, "width": 400}]

        Returns:
            str: Transformed image URL
        """
        try:
            return self.client.url({
                'path': image_url,
                'transformation': transformations
            })
        except Exception as e:
            logger.error(f"Failed to generate transformed URL: {str(e)}")
            return image_url

    def get_video_thumbnail(self, video_url, width=320, height=180):
        """
        Generate a thumbnail for a video

        Args:
            video_url: Source video URL
            width: Thumbnail width
            height: Thumbnail height

        Returns:
            str: URL to the generated thumbnail
        """
        try:
            return self.client.url({
                'path': video_url,
                'transformation': [
                    {
                        'format': 'jpg',
                        'height': height,
                        'width': width,
                        'crop': 'fill',
                        'quality': '80',
                        'progressive': 'true'
                    }
                ]
            })
        except Exception as e:
            logger.error(f"Failed to generate video thumbnail: {str(e)}")
            return None

    def bulk_optimize(self, file_ids, transformations=None):
        """
        Optimize multiple images in bulk

        Args:
            file_ids: List of ImageKit file IDs
            transformations: Optional transformations to apply

        Returns:
            dict: Result of the bulk operation
        """
        try:
            return self.client.bulk_file_operations(
                file_ids=file_ids,
                transformations=transformations or []
            )
        except Exception as e:
            logger.error(f"Bulk optimize failed: {str(e)}")
            return {'success': False, 'error': str(e)}
```

## Configuration

### Django Settings
```python
# settings/base.py

# Cloudflare R2 Configuration
AWS_ACCESS_KEY_ID = env('R2_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('R2_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('R2_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = env('R2_ENDPOINT_URL')  # e.g., 'https://<account-id>.r2.cloudflarestorage.com'
AWS_S3_PUBLIC_URL = env('R2_PUBLIC_URL')  # e.g., 'https://<bucket>.<account-id>.r2.dev'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_DEFAULT_ACL = None  # Will be set per object
AWS_QUERYSTRING_AUTH = False  # Don't add auth to query strings
AWS_S3_FILE_OVERWRITE = False  # Prevent overwriting files with same name

# ImageKit.io Configuration
IMAGEKIT_PUBLIC_KEY = env('IMAGEKIT_PUBLIC_KEY')
IMAGEKIT_PRIVATE_KEY = env('IMAGEKIT_PRIVATE_KEY')
IMAGEKIT_URL_ENDPOINT = env('IMAGEKIT_URL_ENDPOINT')  # e.g., 'https://ik.imagekit.io/your_imagekit_id'
IMAGEKIT_URL = env('IMAGEKIT_URL', default=IMAGEKIT_URL_ENDPOINT)

# Media settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ...
    'storages',  # For S3/R2 storage
    'imagekit',  # For image processing
    'media',     # Our media app
]

# Default file storage (for media files)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# For serving media files in development
if DEBUG:
    from .dev import *  # noqa
```

### Environment Variables
```bash
# .env
# Cloudflare R2
R2_ACCESS_KEY_ID=your_r2_access_key
R2_SECRET_ACCESS_KEY=your_r2_secret_key
R2_BUCKET_NAME=your-bucket-name
R2_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
R2_PUBLIC_URL=https://<bucket>.<account-id>.r2.dev

# ImageKit.io
IMAGEKIT_PUBLIC_KEY=your_public_key
IMAGEKIT_PRIVATE_KEY=your_private_key
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_imagekit_id
```

## API Views

### MediaFileViewSet
```python
# media/v2/views/media_views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from django.db.models import Q
from django.core.exceptions import ValidationError

from ...models.media_file import MediaFile
from ...models.media_folder import MediaFolder
from ..serializers.media_file import MediaFileSerializer, MediaFileUploadSerializer
from ...services.media_service import MediaService
from ...exceptions import InvalidFileTypeError, FileTooLargeError, StorageError, MediaUploadError
from stores.permissions import IsStoreStaffOrReadOnly

class MediaFileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing media files.
    """
    serializer_class = MediaFileSerializer
    permission_classes = [IsStoreStaffOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['original_filename', 'alt_text', 'description']
    ordering_fields = ['created_at', 'file_size', 'original_filename']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return media files for the current store"""
        store = self.request.store
        queryset = MediaFile.objects.filter(store=store)

        # Filter by folder
        folder_id = self.request.query_params.get('folder_id')
        if folder_id:
            if folder_id == 'uncategorized':
                queryset = queryset.filter(folder__isnull=True)
            else:
                try:
                    folder = MediaFolder.objects.get(id=folder_id, store=store)
                    queryset = queryset.filter(folder=folder)
                except (ValueError, MediaFolder.DoesNotExist):
                    queryset = queryset.none()

        # Filter by resource type
        resource_type = self.request.query_params.get('type')
        if resource_type in dict(MediaFile.RESOURCE_TYPES):
            queryset = queryset.filter(resource_type=resource_type)

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'create':
            return MediaFileUploadSerializer
        return MediaFileSerializer

    def perform_create(self, serializer):
        """Handle file upload and create MediaFile instance"""
        file_obj = self.request.FILES.get('file')
        if not file_obj:
            raise ValidationError({"file": ["No file was submitted."]})

        folder_id = self.request.data.get('folder')
        folder = None
        if folder_id:
            try:
                folder = MediaFolder.objects.get(id=folder_id, store=self.request.store)
            except (ValueError, MediaFolder.DoesNotExist):
                raise ValidationError({"folder": ["Invalid folder ID."]})

        media_service = MediaService()
        try:
            media_file = media_service.upload_file(
                file_obj=file_obj,
                store=self.request.store,
                user=self.request.user,
                folder=folder,
                metadata={
                    'uploaded_via': 'api',
                    'user_agent': self.request.META.get('HTTP_USER_AGENT', ''),
                    'ip_address': self.get_client_ip()
                }
            )

            # Set the instance for the serializer
            serializer.instance = media_file

        except (InvalidFileTypeError, FileTooLargeError, StorageError) as e:
            raise ValidationError({"file": [str(e)]})
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise ValidationError({"detail": "An error occurred while uploading the file."})

    @action(detail=True, methods=['get'])
    def thumbnail(self, request, pk=None):
        """Get a thumbnail URL for the media file"""
        media_file = self.get_object()
        width = request.query_params.get('width', 200)
        height = request.query_params.get('height', 200)
        crop = request.query_params.get('crop', 'fill')

        try:
            thumbnail_url = media_file.get_thumbnail_url(
                width=int(width),
                height=int(height),
                crop=crop
            )
            return Response({'url': thumbnail_url})
        except (ValueError, TypeError):
            return Response(
                {"detail": "Invalid width/height parameters"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Get a presigned URL for downloading the file"""
        media_file = self.get_object()
        expires_in = min(int(request.query_params.get('expires_in', 3600)), 86400)  # Max 24 hours

        download_url = media_file.get_presigned_url(expires_in=expires_in)
        if not download_url:
            return Response(
                {"detail": "Could not generate download URL"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            'url': download_url,
            'expires_in': expires_in
        })

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """Bulk delete media files"""
        media_ids = request.data.get('ids', [])
        if not isinstance(media_ids, list):
            return Response(
                {"ids": ["Expected a list of media IDs"]},
                status=status.HTTP_400_BAD_REQUEST
            )

        store = request.store
        media_service = MediaService()
        deleted_count = 0

        for media_id in media_ids:
            try:
                media_file = MediaFile.objects.get(id=media_id, store=store)
                if media_service.delete_media(media_file, request.user):
                    deleted_count += 1
            except (MediaFile.DoesNotExist, MediaUploadError):
                continue

        return Response({
            'deleted_count': deleted_count,
            'total_count': len(media_ids)
        })

    def get_client_ip(self):
        """Get the client's IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return self.request.META.get('REMOTE_ADDR')
```

### MediaFolderViewSet
```python
# media/v2/views/folder_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q

from ...models.media_folder import MediaFolder
from ..serializers.media_folder import MediaFolderSerializer, MediaFolderTreeSerializer
from stores.permissions import IsStoreStaffOrReadOnly

class MediaFolderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing media folders.
    """
    serializer_class = MediaFolderSerializer
    permission_classes = [IsStoreStaffOrReadOnly]

    def get_queryset(self):
        """Return folders for the current store"""
        store = self.request.store
        return MediaFolder.objects.filter(store=store).select_related('parent')

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'tree':
            return MediaFolderTreeSerializer
        return MediaFolderSerializer

    def perform_create(self, serializer):
        """Set the store and created_by fields"""
        serializer.save(
            store=self.request.store,
            created_by=self.request.user
        )

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get folder hierarchy as a tree"""
        store = request.store
        folders = MediaFolder.objects.filter(store=store)

        # Get count of files in each folder
        from ...models.media_file import MediaFile
        file_counts = MediaFile.objects.filter(store=store).values('folder').annotate(
            file_count=Count('id')
        )
        file_count_map = {fc['folder']: fc['file_count'] for fc in file_counts if fc['folder']}

        # Build tree
        folder_map = {}
        root_folders = []

        # First pass: create all folder nodes
        for folder in folders:
            folder_map[folder.id] = {
                'id': folder.id,
                'name': folder.name,
                'slug': folder.slug,
                'parent_id': folder.parent_id,
                'file_count': file_count_map.get(folder.id, 0),
                'children': []
            }

        # Second pass: build hierarchy
        for folder_id, folder_data in folder_map.items():
            if folder_data['parent_id'] is None:
                root_folders.append(folder_data)
            else:
                parent = folder_map.get(folder_data['parent_id'])
                if parent:
                    parent['children'].append(folder_data)

        # Add uncategorized count
        uncategorized_count = MediaFile.objects.filter(
            store=store,
            folder__isnull=True
        ).count()

        return Response({
            'folders': root_folders,
            'uncategorized_count': uncategorized_count
        })

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """Move a folder to a new parent"""
        folder = self.get_object()
        parent_id = request.data.get('parent_id')

        if parent_id == str(folder.id):
            return Response(
                {"parent_id": ["A folder cannot be its own parent"]},
                status=status.HTTP_400_BAD_REQUEST
            )

        if parent_id is None:
            folder.parent = None
        else:
            try:
                parent_folder = MediaFolder.objects.get(id=parent_id, store=request.store)
                # Check for circular reference
                if self._is_descendant(parent_folder, folder):
                    return Response(
                        {"parent_id": ["Cannot move folder to its own descendant"]},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                folder.parent = parent_folder
            except MediaFolder.DoesNotExist:
                return Response(
                    {"parent_id": ["Invalid parent folder"]},
                    status=status.HTTP_400_BAD_REQUEST
                )

        folder.save()
        return Response(self.get_serializer(folder).data)

    def _is_descendant(self, parent, child):
        """Check if child is a descendant of parent"""
        if not child.parent:
            return False
        if child.parent_id == parent.id:
            return True
        return self._is_descendant(parent, child.parent)
```

## Serializers

### MediaFileSerializer
```python
# media/v2/serializers/media_file.py
from rest_framework import serializers
from ...models.media_file import MediaFile

class MediaFileSerializer(serializers.ModelSerializer):
    """Serializer for MediaFile model"""
    url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    file_size_formatted = serializers.SerializerMethodField()

    class Meta:
        model = MediaFile
        fields = [
            'id', 'original_filename', 'file_extension', 'file_size', 'file_size_formatted',
            'mime_type', 'resource_type', 'width', 'height', 'alt_text', 'description',
            'folder', 'created_at', 'updated_at', 'url', 'thumbnail_url'
        ]
        read_only_fields = [
            'id', 'original_filename', 'file_extension', 'file_size', 'file_size_formatted',
            'mime_type', 'resource_type', 'width', 'height', 'created_at', 'updated_at',
            'url', 'thumbnail_url'
        ]

    def get_url(self, obj):
        """Get public URL for the media file"""
        return obj.get_absolute_url()

    def get_thumbnail_url(self, obj):
        """Get thumbnail URL for the media file"""
        return obj.get_thumbnail_url()

    def get_file_size_formatted(self, obj):
        """Get human-readable file size"""
        return obj.file_size_formatted


class MediaFileUploadSerializer(serializers.ModelSerializer):
    """Serializer for file uploads"""
    file = serializers.FileField(write_only=True)
    folder = serializers.PrimaryKeyRelatedField(
        queryset=MediaFolder.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = MediaFile
        fields = ['file', 'folder', 'alt_text', 'description']
        read_only_fields = ['id']
```

### MediaFolderSerializer
```python
# media/v2/serializers/media_folder.py
from rest_framework import serializers
from ...models.media_folder import MediaFolder

class MediaFolderSerializer(serializers.ModelSerializer):
    """Serializer for MediaFolder model"""
    file_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = MediaFolder
        fields = ['id', 'name', 'slug', 'parent', 'file_count', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'file_count', 'created_at', 'updated_at']

    def validate_parent(self, value):
        """Validate that parent folder belongs to the same store"""
        if value and value.store != self.context['request'].store:
            raise serializers.ValidationError("Parent folder does not belong to this store.")
        return value


class MediaFolderTreeSerializer(serializers.ModelSerializer):
    """Serializer for folder tree view"""
    children = serializers.SerializerMethodField()

    class Meta:
        model = MediaFolder
        fields = ['id', 'name', 'slug', 'file_count', 'children']

    def get_children(self, obj):
        """Recursively serialize children"""
        serializer = self.__class__(obj.children.all(), many=True, context=self.context)
        return serializer.data
```

## Migration Command

### migrate_media.py
```python
# media/management/commands/migrate_media.py
import os
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
import cloudinary
from cloudinary import uploader, api

from ...models import MediaFile, MediaFolder
from ...services.media_service import MediaService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Migrate media files from Cloudinary to Cloudflare R2 + ImageKit.io'

    def add_arguments(self, parser):
        parser.add_argument(
            '--store-id',
            type=str,
            help='Store ID to migrate media for (default: all stores)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of files to migrate (default: 100)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making any changes'
        )

    def handle(self, *args, **options):
        store_id = options.get('store_id')
        limit = options.get('limit')
        dry_run = options.get('dry_run')

        self.stdout.write(self.style.SUCCESS(
            f'Starting media migration for store {store_id or "all"} (dry run: {dry_run})'
        ))

        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET
        )

        # Get media files to migrate
        queryset = MediaFile.objects.all()
        if store_id:
            queryset = queryset.filter(store_id=store_id)

        total_count = queryset.count()
        self.stdout.write(f'Found {total_count} media files to migrate')

        if not total_count:
            self.stdout.write(self.style.SUCCESS('No media files to migrate'))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run - no changes will be made'))

        migrated_count = 0
        skipped_count = 0
        error_count = 0

        media_service = MediaService()

        for media_file in queryset[:limit]:
            try:
                self.stdout.write(f'Processing {media_file.original_filename}... ', ending='')

                # Skip if already migrated
                if media_file.storage_path and media_file.storage_path.startswith('store_'):
                    self.stdout.write(self.style.WARNING('Already migrated'))
                    skipped_count += 1
                    continue

                # Download from Cloudinary
                try:
                    cloudinary_url = f"v{media_file.version}/{media_file.public_id}.{media_file.format}"
                    temp_file = f'/tmp/{media_file.public_id}.{media_file.format}'

                    if not dry_run:
                        # Download the file
                        with open(temp_file, 'wb') as f:
                            result = cloudinary.utils.cloudinary_url(cloudinary_url)[0]
                            f.write(requests.get(result).content)

                        # Upload to R2 + ImageKit
                        with open(temp_file, 'rb') as f:
                            uploaded_file = SimpleUploadedFile(
                                name=media_file.original_filename,
                                content=f.read(),
                                content_type=media_file.mime_type
                            )

                            # Get folder if exists
                            folder = None
                            if media_file.folder_id:
                                try:
                                    folder = MediaFolder.objects.get(id=media_file.folder_id)
                                except MediaFolder.DoesNotExist:
                                    pass

                            # Upload the file
                            media_service.upload_file(
                                file_obj=uploaded_file,
                                store=media_file.store,
                                user=media_file.uploaded_by,
                                folder=folder,
                                metadata={
                                    'migrated_from_cloudinary': True,
                                    'cloudinary_public_id': media_file.public_id
                                }
                            )

                        # Delete local temp file
                        os.remove(temp_file)

                        # Delete from Cloudinary if migration is successful
                        if not dry_run and settings.CLOUDINARY_DELETE_AFTER_MIGRATE:
                            try:
                                uploader.destroy(media_file.public_id)
                            except Exception as e:
                                logger.error(f"Failed to delete from Cloudinary: {str(e)}")

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
                    error_count += 1
                    continue

                migrated_count += 1
                self.stdout.write(self.style.SUCCESS('Done'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Unexpected error: {str(e)}'))
                error_count += 1
                continue

        # Print summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('Migration complete!'))
        self.stdout.write(f'Total processed: {migrated_count + skipped_count + error_count}')
        self.stdout.write(f'Successfully migrated: {migrated_count}')
        self.stdout.write(f'Skipped (already migrated): {skipped_count}')
        self.stdout.write(f'Errors: {error_count}')

        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a dry run. No changes were made.'))
```

## API Documentation

### Media Files

#### List Media Files
```
GET /api/v2/media/files/
```

**Query Parameters:**
- `folder_id` - Filter by folder ID (use 'uncategorized' for files without a folder)
- `type` - Filter by resource type (image, video, document, other)
- `search` - Search in filename, alt text, or description
- `ordering` - Sort by field (created_at, file_size, original_filename, -created_at, etc.)

**Response:**
```json
{
  "count": 42,
  "next": "https://api.example.com/api/v2/media/files/?page=2",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "original_filename": "example.jpg",
      "file_extension": "jpg",
      "file_size": 1024000,
      "file_size_formatted": "1.0 MB",
      "mime_type": "image/jpeg",
      "resource_type": "image",
      "width": 1920,
      "height": 1080,
      "alt_text": "Example image",
      "description": "An example image",
      "folder": "550e8400-e29b-41d4-a716-446655440001",
      "created_at": "2023-01-01T12:00:00Z",
      "updated_at": "2023-01-01T12:00:00Z",
      "url": "https://ik.imagekit.io/your_imagekit_id/path/to/file.jpg",
      "thumbnail_url": "https://ik.imagekit.io/your_imagekit_id/tr:w-200,h-200,c-fill/path/to/file.jpg"
    }
  ]
}
```

#### Upload File
```
POST /api/v2/media/files/
Content-Type: multipart/form-data

file: <file>
folder: <folder_id> (optional)
alt_text: "Alternative text" (optional)
description: "Description" (optional)
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "original_filename": "example.jpg",
  "file_extension": "jpg",
  "file_size": 1024000,
  "file_size_formatted": "1.0 MB",
  "mime_type": "image/jpeg",
  "resource_type": "image",
  "width": 1920,
  "height": 1080,
  "alt_text": "Alternative text",
  "description": "Description",
  "folder": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z",
  "url": "https://ik.imagekit.io/your_imagekit_id/path/to/file.jpg",
  "thumbnail_url": "https://ik.imagekit.io/your_imagekit_id/tr:w-200,h-200,c-fill/path/to/file.jpg"
}
```

#### Get Thumbnail
```
GET /api/v2/media/files/{id}/thumbnail/
```

**Query Parameters:**
- `width` - Thumbnail width in pixels (default: 200)
- `height` - Thumbnail height in pixels (default: 200)
- `crop` - Crop mode: fill, fit, etc. (default: fill)

**Response:**
```json
{
  "url": "https://ik.imagekit.io/your_imagekit_id/tr:w-200,h-200,c-fill/path/to/file.jpg"
}
```

#### Download File
```
GET /api/v2/media/files/{id}/download/
```

**Query Parameters:**
- `expires_in` - URL expiration time in seconds (default: 3600, max: 86400)

**Response:**
```json
{
  "url": "https://your-bucket.r2.dev/path/to/file.jpg?X-Amz-Expires=3600&...",
  "expires_in": 3600
}
```

### Folders

#### List Folders (Tree View)
```
GET /api/v2/media/folders/tree/
```

**Response:**
```json
{
  "folders": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Products",
      "slug": "products",
      "file_count": 10,
      "children": [
        {
          "id": "550e8400-e29b-41d4-a716-446655440002",
          "name": "Featured",
          "slug": "featured",
          "file_count": 5,
          "children": []
        }
      ]
    }
  ],
  "uncategorized_count": 3
}
```

#### Move Folder
```
POST /api/v2/media/folders/{id}/move/
Content-Type: application/json

{
  "parent_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

## Cost Analysis

### Cloudflare R2
- **Storage**: $0.015 per GB/month (first 10GB free)
- **Class A Operations**: $0.36 per million requests (first 1M requests/month free)
- **Class B Operations**: $0.01 per million requests (first 10M requests/month free)
- **Egress**: Free (unlimited)

### ImageKit.io
- **Transformations**: $0.50 per 1,000 transformations (first 20GB of transformations free)
- **Storage**: $0.10 per GB/month (first 20GB free)
- **Bandwidth**: $0.10 per GB (first 200GB free)

### Estimated Monthly Cost (Example)
- **Assumptions**:
  - 100GB storage
  - 1M Class A operations
  - 10M Class B operations
  - 1M transformations
  - 1TB bandwidth

- **Cloudflare R2 Cost**:
  - Storage: (100GB - 10GB) * $0.015 = $1.35
  - Class A: (1M - 1M free) * $0.36 = $0.00
  - Class B: (10M - 10M free) * $0.01 = $0.00
  - **Total R2 Cost**: $1.35

- **ImageKit.io Cost**:
  - Transformations: (1M / 1,000) * $0.50 = $500
  - Storage: (100GB - 20GB) * $0.10 = $8.00
  - Bandwidth: (1,000GB - 200GB) * $0.10 = $80.00
  - **Total ImageKit Cost**: $588.00

- **Total Estimated Cost**: $589.35/month

## Allowed AI Actions

1. **Code Generation**
   - Generate model fields and methods
   - Create API views and serializers
   - Write service layer logic
   - Generate migration scripts
   - Create test cases

2. **Documentation**
   - Document API endpoints
   - Write code comments
   - Create usage examples
   - Document configuration steps

3. **Refactoring**
   - Optimize database queries
   - Improve error handling
   - Enhance performance
   - Update code to follow best practices

## Forbidden AI Actions

1. **Security Sensitive**
   - Generate API keys or secrets
   - Bypass authentication/authorization
   - Expose sensitive information

2. **Architectural Changes**
   - Change the database schema without approval
   - Modify core business logic
   - Change storage providers (R2/ImageKit)

3. **Production Operations**
   - Run migrations on production
   - Delete production data
   - Modify production configurations

## Implementation Checklist

### Setup
- [ ] Create Cloudflare R2 bucket
- [ ] Configure CORS for the R2 bucket
- [ ] Set up ImageKit.io account
- [ ] Configure environment variables
- [ ] Install required packages (boto3, imagekitio, etc.)

### Development
- [ ] Implement models (MediaFile, MediaFolder)
- [ ] Create MediaService with R2 + ImageKit integration
- [ ] Implement API views and serializers
- [ ] Add authentication and permissions
- [ ] Write unit tests
- [ ] Document API endpoints

### Migration
- [ ] Test migration with a small subset of files
- [ ] Back up Cloudinary data
- [ ] Run migration script
- [ ] Verify all files were migrated correctly
- [ ] Update any hardcoded Cloudinary URLs in the database

### Deployment
- [ ] Set up monitoring for storage usage
- [ ] Configure backups for R2 bucket
- [ ] Set up alerts for quota limits
- [ ] Document operational procedures

## Security & Privacy Rules

### Access Control
- All non-image/video files (documents) MUST use private ACL on R2
- Use presigned URLs with `expires_in` ≤ 3600 seconds for private file downloads
- Implement IP-based rate limiting for upload endpoints
- Enforce MIME type validation for all uploads
- Restrict file uploads by extension and content type

### Data Protection
- Anonymize IP addresses in metadata for non-authenticated visitors
- Never store passwords, API tokens, or PII in file metadata
- Encrypt sensitive metadata at rest
- Implement secure deletion of files when removed from trash

### File Security
- Scan all uploaded files for malware (integrate ClamAV or VirusTotal API)
- Validate image/video files for potential exploits
- Set appropriate Content-Security-Policy headers for media delivery
- Implement CORS restrictions for media domains

## Performance Rules

### Processing
- Use Celery for async post-upload processing:
  - Thumbnail generation
  - Metadata extraction
  - Virus scanning
  - File optimization
- Process large uploads in chunks (resumable uploads)
- Implement background processing for batch operations

### Caching
- Cache ImageKit URLs aggressively: `Cache-Control: max-age=31536000` for public assets
- Implement CDN caching for frequently accessed media
- Use stale-while-revalidate for dynamic transformations
- Cache folder hierarchies to reduce database load

### Optimization
- Enable gzip/brotli compression for text-based assets
- Use WebP/AVIF formats for web images when supported
- Implement lazy loading for below-the-fold media
- Optimize video delivery with adaptive bitrate streaming

## Cost & Quota Rules

### Monitoring
- Monitor R2 storage usage monthly via Cloudflare dashboard
- Set up alerts for 70%, 85%, and 95% of storage quota
- Track ImageKit transformation and bandwidth usage
- Log and analyze storage growth trends

### Optimization
- Implement automatic cleanup of old/unused files
- Set storage quotas per store/tenant
- Use lifecycle rules to transition old files to cheaper storage
- Compress and optimize images during upload

### Cost Controls
- ImageKit free tier: 20GB transformations + 200GB bandwidth — warn when approaching limits
- Use 'f-auto' for automatic format selection
- Apply 'q-80' quality for non-critical images
- Implement usage-based throttling for high-volume tenants
- Consider cost allocation tags for multi-tenant billing

## Implementation Timeline

### Phase 1: Core Functionality (Week 1-2)
1. Set up R2 bucket and IAM policies
2. Implement basic file upload/download
3. Create folder structure
4. Set up basic permissions

### Phase 2: Advanced Features (Week 3-4)
1. Implement thumbnail generation
2. Add bulk operations
3. Set up monitoring and alerts
4. Implement file scanning

### Phase 3: Optimization (Week 5-6)
1. Add caching layer
2. Implement async processing
3. Optimize delivery
4. Final security review

### Phase 4: Migration (Week 7-8)
1. Test migration with sample data
2. Schedule maintenance window
3. Execute full migration
4. Validate and monitor

<!-- ===============================================================================
 END MEDIAFILE.MD
 ================================================================================= -->


<!-- ===============================================================================
 START METAFIELDS.MD
 ================================================================================= -->
# Metafields System v2.0

## 🎯 Purpose

This document defines the architecture and implementation rules for the Metafields system, enabling dynamic custom fields for any model in the CMS-Updated platform.

## 📚 Related Documents
- [Core Architecture](../core.md)
- [Store Management](../stores.md)
- [Content Types](../content-types.md)

## 🔍 Implementation Status

### Core Components
- [ ] `MetafieldDefinition` model
- [ ] `Metafield` model
- [ ] `MetafieldService`
- [ ] API endpoints

### Integration Points
- [ ] User Profiles
- [ ] Products
- [ ] Pages
- [ ] Collections

---

## 🏗️ Architecture

### Core Models

#### MetafieldDefinition
```python
# apps/public/metafields/models/definitions.py
from django.db import models
from core.models import TenantModel

class MetafieldDefinition(TenantModel):
    """Defines the structure and validation for metafields"""

    # Core Identification
    name = models.CharField(max_length=100)
    namespace = models.CharField(max_length=50, help_text="Category for grouping fields")
    key = models.CharField(max_length=50, help_text="Unique identifier within namespace")

    # Type and Validation
    TYPE_CHOICES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('boolean', 'True/False'),
        ('date', 'Date'),
        ('url', 'URL'),
        ('json', 'JSON'),
        ('select', 'Dropdown'),
        ('multiselect', 'Multi-select'),
        ('image', 'Image'),
        ('file', 'File'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    # Configuration
    is_required = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    is_filterable = models.BooleanField(default=False)
    is_sortable = models.BooleanField(default=False)

    class Meta(TenantModel.Meta):
        db_table = 'metafields_definition'
        unique_together = [['store', 'namespace', 'key']]
        ordering = ['namespace', 'key']

    def __str__(self):
        return f"{self.namespace}.{self.key}"

#### Metafield
```python
# apps/public/metafields/models/fields.py
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from core.models import TenantModel

class Metafield(TenantModel):
    """Stores actual metafield values with generic relations"""

    # Reference to the definition
    definition = models.ForeignKey(
        'metafields.MetafieldDefinition',
        on_delete=models.CASCADE,
        related_name='values'
    )

    # Generic relation to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Value storage (type-specific)
    value_text = models.TextField(blank=True, null=True)
    value_number = models.FloatField(blank=True, null=True)
    value_boolean = models.BooleanField(blank=True, null=True)
    value_date = models.DateField(blank=True, null=True)
    value_json = models.JSONField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = 'metafields_metafield'
        unique_together = [['store', 'definition', 'content_type', 'object_id']]
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.definition} on {self.content_object}"
```

## 🔄 Integration Patterns

### 1. Adding Metafields to a Model

```python
# Example: Adding to Product model
from django.contrib.contenttypes.fields import GenericRelation

class Product(TenantModel):
    # ... existing fields ...
    metafields = GenericRelation(
        'metafields.Metafield',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='product'
    )
```

### 2. Using MetafieldService

```python
# Get a metafield value
value = MetafieldService.get_metafield(
    store=store,
    content_object=product,
    namespace='inventory',
    key='stock_warning_level'
)

# Set a metafield value
MetafieldService.set_metafield(
    store=store,
    content_object=product,
    namespace='inventory',
    key='stock_warning_level',
    value=10
)
```

## 🔐 Permissions

### Required Permissions
- `metafields.add_metafielddefinition`
- `metafields.change_metafielddefinition`
- `metafields.view_metafielddefinition`
- `metafields.add_metafield`
- `metafields.change_metafield`
- `metafields.view_metafield`

## 🚀 Best Practices

1. **Namespace Organization**
   - Use consistent namespaces (e.g., 'seo', 'inventory', 'display')
   - Document all namespaces in use

2. **Performance**
   - Use `select_related` and `prefetch_related` when querying metafields
   - Cache frequently accessed metafields

3. **Validation**
   - Always validate metafield values against their definitions
   - Use the provided validation methods in `MetafieldService`

## 🔄 Migration Strategy

1. Add new metafield tables
2. Create data migration for existing fields
3. Update views to use new metafield system
4. Remove old field columns in subsequent release

## 📊 Monitoring

### Key Metrics
- Metafield usage by type
- Query performance
- Storage usage

## 🧪 Testing

### Test Cases

```python
# tests/test_metafields.py
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from apps.products.models import Product
from ..models import MetafieldDefinition, Metafield

class MetafieldTests(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name="Test Store", slug="test-store")
        self.product = Product.objects.create(
            store=self.store,
            name="Test Product",
            sku="TEST-001"
        )

        # Create a test metafield definition
        self.defn = MetafieldDefinition.objects.create(
            store=self.store,
            name="Stock Warning Level",
            namespace="inventory",
            key="stock_warning_level",
            type="number"
        )

    def test_metafield_creation(self):
        """Test creating a metafield"""
        metafield = Metafield.objects.create(
            store=self.store,
            definition=self.defn,
            content_object=self.product,
            value_number=10
        )

        self.assertEqual(metafield.value_number, 10)
        self.assertEqual(metafield.content_object, self.product)
```

## 📝 Version History

### v2.0 (Current)
- Consolidated metafields documentation
- Added integration patterns and examples
- Improved type safety and validation

### v1.0 (Legacy)
- Initial implementation
        ('post', 'Post'),
        ('product', 'Product'),
        ('collection', 'Collection'),
        ('store', 'Store'),
    ]
    content_types = models.JSONField(
        default=list,
        help_text="Which models this field applies to"
    )

    # UI Configuration
    ui = models.JSONField(
        default=dict,
        help_text="UI configuration (placeholder, help text, etc.)"
    )

    class Meta(TenantModel.Meta):
        db_table = 'metafields_definition'
        unique_together = [['store', 'namespace', 'key']]
        indexes = [
            models.Index(fields=['namespace', 'key']),
            models.Index(fields=['is_visible']),
            models.Index(fields=['content_types'], name='content_types_idx')
        ]

    def __str__(self):
        return f"{self.namespace}.{self.key}"

    def clean(self):
        """Validate the definition"""
        from django.core.exceptions import ValidationError

        # Validate namespace/key format
        if not self.namespace.islower():
            raise ValidationError("Namespace must be lowercase")

        if not self.key.islower():
            raise ValidationError("Key must be lowercase")

        # Validate options for select fields
        if self.type in ['select', 'multiselect'] and not self.options:
            raise ValidationError("Select fields must have options defined")
```

#### **Metafield**
```python
# apps/public/metafields/models/values.py
from core.models import TenantModel
from django.db import models

class Metafield(TenantModel):
    """
    Stores actual metafield values with generic relations
    """

    # Link to definition
    definition = models.ForeignKey(
        'metafields.MetafieldDefinition',
        on_delete=models.CASCADE,
        related_name='values'
    )

    # Generic relation to any model
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = models.GenericForeignKey('content_type', 'object_id')

    # Value storage (type-specific)
    value_text = models.TextField(blank=True, null=True)
    value_number = models.FloatField(blank=True, null=True)
    value_boolean = models.BooleanField(blank=True, null=True)
    value_date = models.DateTimeField(blank=True, null=True)
    value_json = models.JSONField(blank=True, null=True)

    # Media fields (for image/file types)
    value_media = models.ForeignKey(
        'media.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = 'metafields_value'
        unique_together = [
            'store', 'definition', 'content_type', 'object_id'
        ]
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['definition', 'value_text']),
            models.Index(fields=['definition', 'value_number']),
            models.Index(fields=['definition', 'value_boolean']),
        ]

    def __str__(self):
        return f"{self.definition} = {self.get_value()}"

    def get_value(self):
        """Get the value in the correct type"""
        if self.definition.type in ['image', 'file']:
            return self.value_media
        return getattr(self, f'value_{self.definition.type}', None)

    def set_value(self, value):
        """Set the value with type conversion"""
        if self.definition.type in ['image', 'file']:
            self.value_media = value
        else:
            field_name = f'value_{self.definition.type}'
            setattr(self, field_name, value)

            # Clear other value fields
            for t in ['text', 'number', 'boolean', 'date', 'json']:
                if t != self.definition.type:
                    setattr(self, f'value_{t}', None)
            self.value_media = None
```

---

## 🛠️ Services Layer

### **MetafieldService**
```python
# apps/public/metafields/services.py
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType

class MetafieldService:
    """Core service for metafield operations"""

    @staticmethod
    def get_metafield_definition(store, namespace, key):
        """Get a metafield definition by namespace and key"""
        from .models import MetafieldDefinition
        return MetafieldDefinition.objects.get(
            store=store,
            namespace=namespace,
            key=key
        )

    @staticmethod
    def get_metafield(instance, definition):
        """Get a metafield value for an instance"""
        from .models import Metafield

        content_type = ContentType.objects.get_for_model(instance)
        return Metafield.objects.filter(
            definition=definition,
            content_type=content_type,
            object_id=instance.id,
            store=instance.store
        ).first()

    @staticmethod
    def set_metafield(instance, namespace, key, value):
        """Set a metafield value for an instance"""
        from .models import Metafield, MetafieldDefinition

        # Get or create definition
        definition, created = MetafieldDefinition.objects.get_or_create(
            store=instance.store,
            namespace=namespace,
            key=key,
            defaults={
                'name': f"{namespace}.{key}",
                'type': MetafieldService._infer_type(value),
                'content_types': [ContentType.objects.get_for_model(instance).model]
            }
        )

        # Get or create metafield
        content_type = ContentType.objects.get_for_model(instance)
        metafield, created = Metafield.objects.get_or_create(
            definition=definition,
            content_type=content_type,
            object_id=instance.id,
            store=instance.store
        )

        # Set and save value
        metafield.set_value(value)
        metafield.save()

        return metafield

    @staticmethod
    def _infer_type(value):
        """Infer metafield type from Python type"""
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, (int, float)):
            return 'number'
        elif isinstance(value, dict):
            return 'json'
        return 'text'

    @staticmethod
    def get_metafields_for_object(instance, namespace=None):
        """Get all metafields for an object, optionally filtered by namespace"""
        from .models import Metafield, MetafieldDefinition

        content_type = ContentType.objects.get_for_model(instance)
        queryset = Metafield.objects.filter(
            store=instance.store,
            content_type=content_type,
            object_id=instance.id
        ).select_related('definition')

        if namespace:
            queryset = queryset.filter(definition__namespace=namespace)

        return queryset

    @staticmethod
    def get_metafields_by_namespace(store, namespace):
        """Get all metafield definitions for a namespace"""
        from .models import MetafieldDefinition
        return MetafieldDefinition.objects.filter(
            store=store,
            namespace=namespace
        )

    @staticmethod
    @transaction.atomic
    def bulk_update_metafields(instance, metafield_data):
        """Update multiple metafields for an instance"""
        from .models import Metafield, MetafieldDefinition

        content_type = ContentType.objects.get_for_model(instance)
        updated_metafields = []

        for namespace_key, value in metafield_data.items():
            if '.' not in namespace_key:
                continue

            namespace, key = namespace_key.split('.', 1)

            # Get or create definition
            definition, created = MetafieldDefinition.objects.get_or_create(
                store=instance.store,
                namespace=namespace,
                key=key,
                defaults={
                    'name': f"{namespace}.{key}",
                    'type': MetafieldService._infer_type(value),
                    'content_types': [content_type.model]
                }
            )

            # Get or create metafield
            metafield, created = Metafield.objects.get_or_create(
                definition=definition,
                content_type=content_type,
                object_id=instance.id,
                store=instance.store
            )

            # Set value
            metafield.set_value(value)
            metafield.save()
            updated_metafields.append(metafield)

        return updated_metafields
```

---

## 🌐 API Endpoints

### **MetafieldDefinitionViewSet**
```python
# apps/dashboard/metafields/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema

class MetafieldDefinitionViewSet(TenantViewSet):
    """
    CRUD operations for metafield definitions
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = MetafieldDefinitionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = ['namespace', 'type', 'is_required', 'is_visible']
    search_fields = ['name', 'namespace', 'key']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        return MetafieldDefinition.objects.filter(store=self.request.store)

    @extend_schema(
        summary="List Metafield Definitions",
        description="Get paginated list of metafield definitions"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create Metafield Definition",
        request=MetafieldDefinitionSerializer,
        responses={201: MetafieldDefinitionSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
```

### **MetafieldViewSet**
```python
# apps/dashboard/metafields/v2/views.py
class MetafieldViewSet(TenantViewSet):
    """
    CRUD operations for metafield values
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = MetafieldSerializer

    def get_queryset(self):
        return Metafield.objects.filter(store=self.request.store)

    @extend_schema(
        summary="Get Metafields for Object",
        description="Get all metafields for a specific object"
    )
    @action(detail=False, methods=['get'])
    def for_object(self, request):
        """Get all metafields for a specific object"""
        content_type = request.query_params.get('content_type')
        object_id = request.query_params.get('object_id')

        if not content_type or not object_id:
            return Response(
                {"error": "content_type and object_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        metafields = Metafield.objects.filter(
            store=request.store,
            content_type__model=content_type,
            object_id=object_id
        )

        serializer = self.get_serializer(metafields, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Bulk Update Metafields",
        request=BulkMetafieldSerializer,
        responses={200: MetafieldSerializer(many=True)}
    )
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update metafields for an object"""
        content_type = request.query_params.get('content_type')
        object_id = request.query_params.get('object_id')

        if not content_type or not object_id:
            return Response(
                {"error": "content_type and object_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the object
        content_type_obj = ContentType.objects.get(model=content_type)
        model_class = content_type_obj.model_class()
        instance = model_class.objects.get(id=object_id)

        # Update metafields
        metafields = MetafieldService.bulk_update_metafields(
            instance, request.data
        )

        serializer = self.get_serializer(metafields, many=True)
        return Response(serializer.data)
```

---

## 🔄 Usage Examples

### **Adding Metafields to Models**
```python
# apps/public/users/models.py
from django.db import models
from core.models import TenantModel

class UserProfile(TenantModel):
    """Example model with metafields support"""

    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE)
    bio = models.TextField(blank=True)

    # Metafields property
    @property
    def metafields(self):
        """Access metafields as attributes"""
        from metafields.services import MetafieldService
        return MetafieldService.get_metafields_for_object(self)

    def get_metafield(self, namespace, key):
        """Get a specific metafield"""
        from metafields.services import MetafieldService
        try:
            definition = MetafieldService.get_metafield_definition(
                self.store, namespace, key
            )
            return MetafieldService.get_metafield(self, definition)
        except:
            return None

    def set_metafield(self, namespace, key, value):
        """Set a metafield value"""
        from metafields.services import MetafieldService
        return MetafieldService.set_metafield(self, namespace, key, value)

    def get_all_metafields(self):
        """Get all metafields as a dictionary"""
        metafields = {}
        for metafield in self.metafields:
            key = f"{metafield.definition.namespace}.{metafield.definition.key}"
            metafields[key] = metafield.get_value()
        return metafields
```

### **Using Metafields in Views**
```python
# Example: Setting metafields
profile = UserProfile.objects.first()
profile.set_metafield("social", "twitter_handle", "@example")
profile.set_metafield("social", "website_url", "https://example.com")
profile.set_metafield("preferences", "theme_color", "#FF5722")

# Example: Getting metafields
handle = profile.get_metafield("social", "twitter_handle")
print(handle.get_value())  # Output: @example

# Example: Getting all metafields
all_metafields = profile.get_all_metafields()
print(all_metafields)
# Output: {
#   "social.twitter_handle": "@example",
#   "social.website_url": "https://example.com",
#   "preferences.theme_color": "#FF5722"
# }
```

### **Frontend Integration**
```javascript
// Example JavaScript for metafield management
async function updateMetafields(objectType, objectId, metafields) {
    try {
        const response = await fetch(
            `/v2/api/dashboard/metafields/bulk_update/?content_type=${objectType}&object_id=${objectId}`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(metafields)
            }
        );

        const result = await response.json();
        return result;

    } catch (error) {
        console.error('Error updating metafields:', error);
    }
}

// Usage
updateMetafields('user', 123, {
    'social.twitter_handle': '@newhandle',
    'preferences.theme_color': '#2196F3'
});
```

---

## 🛡️ Security & Permissions

### **Access Control**
- **Store Owners**: Full CRUD on all metafields
- **Staff**: Read-only access to metafields
- **Public**: Read-only access to public metafields (if `is_visible=True`)

### **Validation Rules**
- Namespace and keys must be lowercase alphanumeric with underscores
- Values are validated against their type definition
- Required fields must have values
- Select fields must have valid options

---

## 🚀 Performance Considerations

### **Indexing**
- All foreign keys are indexed
- Common query patterns are optimized with indexes
- JSON fields use GIN indexes for efficient querying

### **Caching**
- Metafield definitions are cached per store
- Object metafields are cached for the request duration

### **Batch Operations**
- Bulk create/update operations are supported
- Efficient querying with `select_related` and `prefetch_related`

---

## 📊 Database Schema

### **metafields_definition**
```sql
CREATE TABLE metafields_definition (
    id SERIAL PRIMARY KEY,
    store_id INTEGER REFERENCES stores_store(id),
    namespace VARCHAR(50) NOT NULL,
    key VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL,
    is_required BOOLEAN DEFAULT false,
    is_visible BOOLEAN DEFAULT true,
    options JSONB DEFAULT '[]'::jsonb,
    validations JSONB DEFAULT '{}'::jsonb,
    content_types JSONB DEFAULT '[]'::jsonb,
    ui JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(store_id, namespace, key)
);

CREATE INDEX idx_metafields_definition_store ON metafields_definition(store_id);
CREATE INDEX idx_metafields_definition_lookup ON metafields_definition(namespace, key);
CREATE INDEX idx_metafields_definition_visible ON metafields_definition(is_visible);
```

### **metafields_value**
```sql
CREATE TABLE metafields_value (
    id SERIAL PRIMARY KEY,
    store_id INTEGER REFERENCES stores_store(id),
    definition_id INTEGER REFERENCES metafields_definition(id),
    content_type_id INTEGER REFERENCES django_content_type(id),
    object_id INTEGER NOT NULL,
    value_text TEXT,
    value_number DOUBLE PRECISION,
    value_boolean BOOLEAN,
    value_date TIMESTAMPTZ,
    value_json JSONB,
    value_media_id INTEGER REFERENCES media_mediafile(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(store_id, definition_id, content_type_id, object_id)
);

CREATE INDEX idx_metafields_value_lookup ON metafields_value(content_type_id, object_id);
CREATE INDEX idx_metafields_value_definition ON metafields_value(definition_id);
CREATE INDEX idx_metafields_value_text ON metafields_value USING GIN (value_text gin_trgm_ops);
CREATE INDEX idx_metafields_value_number ON metafields_value(value_number);
CREATE INDEX idx_metafields_value_boolean ON metafields_value(value_boolean);
```

---

## 📝 Implementation Checklist

### **Core Features**
- [x] Metafield definitions with types and validation
- [x] Generic foreign key to any model
- [x] Store-scoped metafields
- [x] Type-safe value storage
- [x] Bulk operations support
- [x] Media integration for image/file types

### **API Endpoints**
- [x] CRUD for metafield definitions
- [x] CRUD for metafield values
- [x] Filtering and searching
- [x] Bulk operations
- [x] Object-specific metafield retrieval

### **Security**
- [x] Store isolation
- [x] Permission checks
- [x] Input validation
- [x] Rate limiting

### **Performance**
- [x] Proper indexing
- [x] Query optimization
- [x] Caching layer
- [x] Batch operations

### **Documentation**
- [x] API documentation
- [x] Usage examples
- [x] Database schema
- [x] Security considerations

<!-- ===============================================================================
 END METAFIELDS.MD
 ================================================================================= -->


<!-- ===============================================================================
 START NOTIFICATIONS.MD
 ================================================================================= -->
# Notifications App Rules v1.0

## 🎯 Purpose

This document defines strict development rules for the **notifications** app in CMS-Updated backend, implementing a unified, multi-channel notification system supporting email, in-app, push, and SMS notifications.

---

## 🏗️ Notifications App Structure

### **Fixed Directory Structure**
```
apps/
├── notifications/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── admin.py
│   ├── services.py
│   ├── tasks.py
│   ├── channels/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── email.py
│   │   ├── in_app.py
│   │   ├── push.py
│   │   └── sms.py
│   ├── management/
│   │   └── commands/
│   │       ├── cleanup_notifications.py
│   │       └── send_digest.py
│   ├── migrations/
│   ├── v2/
│   │   ├── __init__.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_services.py
│       └── test_channels.py
```

---

## 📋 Core Models

### **Model Inheritance**
All notifications models must inherit from `TenantModel` for store scoping:

```python
from core.models import TenantModel
from django.db import models

class Notification(TenantModel):
    # Store-scoped notification model
    pass
```

### **Notification Model**
```python
# apps/notifications/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import TenantModel

User = get_user_model()

class NotificationType(models.TextChoices):
    """Predefined notification types"""
    ORDER_CREATED = 'order.created', 'Order Created'
    ORDER_SHIPPED = 'order.shipped', 'Order Shipped'
    ORDER_DELIVERED = 'order.delivered', 'Order Delivered'
    PAYMENT_RECEIVED = 'payment.received', 'Payment Received'
    PRODUCT_LOW_STOCK = 'product.low_stock', 'Product Low Stock'
    PRODUCT_OUT_OF_STOCK = 'product.out_of_stock', 'Product Out of Stock'
    FORM_SUBMITTED = 'form.submitted', 'Form Submitted'
    USER_REGISTERED = 'user.registered', 'User Registered'
    SYSTEM_ALERT = 'system.alert', 'System Alert'
    CUSTOM = 'custom', 'Custom Notification'

class NotificationChannel(models.TextChoices):
    """Available notification channels"""
    EMAIL = 'email', 'Email'
    IN_APP = 'in_app', 'In-App'
    PUSH = 'push', 'Push'
    SMS = 'sms', 'SMS'

class NotificationStatus(models.TextChoices):
    """Notification delivery status"""
    PENDING = 'pending', 'Pending'
    SENT = 'sent', 'Sent'
    DELIVERED = 'delivered', 'Delivered'
    FAILED = 'failed', 'Failed'
    READ = 'read', 'Read'

class Notification(TenantModel):
    """
    Store-scoped notification for multi-channel delivery
    """

    # Core fields
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        db_index=True
    )
    title = models.CharField(max_length=255)
    message = models.TextField()

    # Relationships
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )

    # Targeting
    target_type = models.CharField(
        max_length=50,
        choices=[
            ('user', 'User'),
            ('role', 'Role'),
            ('store', 'Store'),
            ('all', 'All')
        ],
        default='user'
    )
    target_id = models.CharField(max_length=100, blank=True)

    # Channels
    channels = models.JSONField(
        default=list,
        help_text="List of channels to send notification through"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default='pending'
    )

    # Delivery tracking
    delivery_attempts = models.PositiveSmallIntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = 'notifications_notification'
        indexes = [
            models.Index(fields=['store', 'user', 'status']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.email if self.user else 'No user'}"

    def mark_as_read(self):
        """Mark notification as read"""
        if self.status != 'read':
            self.status = 'read'
            self.read_at = timezone.now()
            self.save(update_fields=['status', 'read_at'])

    def is_delivered(self):
        """Check if notification is delivered"""
        return self.status in ['delivered', 'read']

    def should_send_via_channel(self, channel):
        """Check if notification should be sent via specific channel"""
        return channel in self.channels
```

### **NotificationPreference Model**
```python
class NotificationPreference(TenantModel):
    """
    User notification preferences per channel and type
    """

    # Relationships
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )

    # Preferences
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices
    )
    channel_preferences = models.JSONField(
        default=dict,
        help_text="Channel preferences: {email: true, in_app: true, push: false, sms: false}"
    )

    # Digest settings
    digest_enabled = models.BooleanField(default=False)
    digest_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediate'),
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly')
        ],
        default='immediate'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = 'notifications_preference'
        unique_together = [['store', 'user', 'notification_type']]
        ordering = ['user', 'notification_type']

    def __str__(self):
        return f"{self.user.email} - {self.notification_type}"

    def is_channel_enabled(self, channel):
        """Check if channel is enabled for this notification type"""
        return self.channel_preferences.get(channel, True)
```

### **NotificationTemplate Model**
```python
class NotificationTemplate(TenantModel):
    """
    Reusable notification templates
    """

    # Core fields
    name = models.CharField(max_length=255)
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices
    )

    # Template content
    title_template = models.CharField(max_length=255)
    message_template = models.TextField()

    # Channel-specific templates
    email_subject_template = models.CharField(max_length=255, blank=True)
    email_body_template = models.TextField(blank=True)
    push_title_template = models.CharField(max_length=255, blank=True)
    push_body_template = models.TextField(blank=True)
    sms_template = models.TextField(blank=True)

    # Variables documentation
    variables = models.JSONField(
        default=dict,
        help_text="Available variables and their descriptions"
    )

    # Status
    is_active = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = 'notifications_template'
        unique_together = [['store', 'notification_type', 'name']]
        ordering = ['notification_type', 'name']

    def __str__(self):
        return f"{self.name} - {self.notification_type}"

    def render(self, context):
        """Render template with context variables"""
        from django.template import Template, Context

        def render_template(template_string):
            template = Template(template_string)
            return template.render(Context(context))

        return {
            'title': render_template(self.title_template),
            'message': render_template(self.message_template),
            'email_subject': render_template(self.email_subject_template) if self.email_subject_template else None,
            'email_body': render_template(self.email_body_template) if self.email_body_template else None,
            'push_title': render_template(self.push_title_template) if self.push_title_template else None,
            'push_body': render_template(self.push_body_template) if self.push_body_template else None,
            'sms': render_template(self.sms_template) if self.sms_template else None,
        }
```

---

## 🔌 API Endpoints

### **V2-Only Implementation**
All notification endpoints must be V2-only with clean architecture:

#### NotificationViewSet
```python
# apps/notifications/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class NotificationViewSet(TenantViewSet):
    """
    Notification management endpoints for dashboard
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    filterset_fields = ['status', 'notification_type', 'user']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    @extend_schema(
        summary="Mark as Read",
        description="Mark notification as read",
        responses={200: NotificationSerializer}
    )
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.mark_as_read()

        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Resend Notification",
        description="Resend failed notification",
        responses={200: NotificationSerializer}
    )
    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        """Resend notification"""
        notification = self.get_object()

        from services.notification import NotificationService
        NotificationService.send_notification(notification)

        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)
```

#### NotificationPreferenceViewSet
```python
class NotificationPreferenceViewSet(TenantViewSet):
    """
    Notification preference management endpoints
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    queryset = NotificationPreference.objects.all()
    serializer_class = NotificationPreferenceSerializer
    filterset_fields = ['notification_type']
    ordering_fields = ['notification_type']
    ordering = ['notification_type']
```

---

## 🛠️ Services Layer

### **Business Logic Centralization**
All notification business logic must be in services.py:

#### NotificationService
```python
# apps/notifications/services.py
from django.db import transaction
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """Shared notification management service"""

    @staticmethod
    @transaction.atomic
    def create_notification(
        store,
        notification_type,
        title,
        message,
        user=None,
        channels=None,
        metadata=None
    ):
        """
        Create a new notification
        """
        if channels is None:
            channels = ['in_app']

        notification = Notification.objects.create(
            store=store,
            notification_type=notification_type,
            title=title,
            message=message,
            user=user,
            channels=channels,
            metadata=metadata or {}
        )

        # Trigger async sending
        from .tasks import send_notification
        send_notification.delay(notification.id)

        return notification

    @staticmethod
    def send_notification(notification):
        """
        Send notification via all enabled channels
        """
        # Check user preferences
        if notification.user:
            preferences = NotificationPreference.objects.filter(
                store=notification.store,
                user=notification.user,
                notification_type=notification.notification_type
            ).first()

            if preferences:
                # Filter channels based on preferences
                enabled_channels = [
                    channel for channel in notification.channels
                    if preferences.is_channel_enabled(channel)
                ]
                notification.channels = enabled_channels
                notification.save(update_fields=['channels'])

        # Send via each channel
        for channel in notification.channels:
            try:
                NotificationService._send_via_channel(notification, channel)
            except Exception as e:
                logger.error(f"Failed to send notification via {channel}: {e}")

        # Update status
        notification.status = 'sent'
        notification.delivery_attempts += 1
        notification.last_attempt_at = timezone.now()
        notification.save(update_fields=['status', 'delivery_attempts', 'last_attempt_at'])

        return notification

    @staticmethod
    def _send_via_channel(notification, channel):
        """Send notification via specific channel"""
        if channel == 'email':
            from .channels.email import EmailChannel
            EmailChannel.send(notification)
        elif channel == 'in_app':
            from .channels.in_app import InAppChannel
            InAppChannel.send(notification)
        elif channel == 'push':
            from .channels.push import PushChannel
            PushChannel.send(notification)
        elif channel == 'sms':
            from .channels.sms import SMSChannel
            SMSChannel.send(notification)

    @staticmethod
    def get_user_notifications(user, status=None, limit=50):
        """Get notifications for a user"""
        queryset = Notification.objects.filter(user=user)

        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-created_at')[:limit]

    @staticmethod
    def get_unread_count(user):
        """Get unread notification count for user"""
        return Notification.objects.filter(
            user=user,
            status='pending'
        ).count()

    @staticmethod
    def mark_all_as_read(user):
        """Mark all user notifications as read"""
        count = Notification.objects.filter(
            user=user,
            status='pending'
        ).update(status='read', read_at=timezone.now())

        return count
```

---

## 📡 Channel Implementations

### **Base Channel**
```python
# apps/notifications/channels/base.py
from abc import ABC, abstractmethod

class BaseChannel(ABC):
    """Base channel class"""

    @staticmethod
    @abstractmethod
    def send(notification):
        """Send notification via this channel"""
        pass

    @staticmethod
    @abstractmethod
    def validate_config(notification):
        """Validate channel configuration"""
        pass
```

### **Email Channel**
```python
# apps/notifications/channels/email.py
from .base import BaseChannel
from services.smtp import SMTPService

class EmailChannel(BaseChannel):
    """Email notification channel"""

    @staticmethod
    def send(notification):
        """Send notification via email"""
        if not notification.user or not notification.user.email:
            logger.warning(f"No email for notification #{notification.id}")
            return

        # Get or create email template
        template = NotificationTemplate.objects.filter(
            store=notification.store,
            notification_type=notification.notification_type
        ).first()

        if template:
            rendered = template.render(notification.metadata)
            subject = rendered.get('email_subject', notification.title)
            body = rendered.get('email_body', notification.message)
        else:
            subject = notification.title
            body = notification.message

        # Send via SMTP service
        SMTPService.send_template_email(
            template_name='notification',
            recipients=[notification.user.email],
            subject=subject,
            html_content=body,
            text_content=notification.message,
            store=notification.store
        )

        logger.info(f"Email notification sent to {notification.user.email}")

    @staticmethod
    def validate_config(notification):
        """Validate email configuration"""
        return notification.user and notification.user.email
```

### **In-App Channel**
```python
# apps/notifications/channels/in_app.py
from .base import BaseChannel

class InAppChannel(BaseChannel):
    """In-app notification channel"""

    @staticmethod
    def send(notification):
        """Store notification for in-app display"""
        # In-app notifications are stored in the database
        # No additional action needed
        notification.status = 'delivered'
        notification.delivered_at = timezone.now()
        notification.save(update_fields=['status', 'delivered_at'])

        logger.info(f"In-app notification #{notification.id} delivered")

    @staticmethod
    def validate_config(notification):
        """Validate in-app configuration"""
        return True  # Always valid
```

### **Push Channel**
```python
# apps/notifications/channels/push.py
from .base import BaseChannel

class PushChannel(BaseChannel):
    """Push notification channel"""

    @staticmethod
    def send(notification):
        """Send notification via push"""
        # Get user's push tokens
        from .models import PushToken
        tokens = PushToken.objects.filter(
            user=notification.user,
            is_active=True
        )

        if not tokens.exists():
            logger.warning(f"No push tokens for user {notification.user.email}")
            return

        # Get template
        template = NotificationTemplate.objects.filter(
            store=notification.store,
            notification_type=notification.notification_type
        ).first()

        if template:
            rendered = template.render(notification.metadata)
            title = rendered.get('push_title', notification.title)
            body = rendered.get('push_body', notification.message)
        else:
            title = notification.title
            body = notification.message

        # Send via FCM/APNs (implementation depends on provider)
        # This is a placeholder for actual push service integration
        for token in tokens:
            # Send push notification
            logger.info(f"Push notification sent to {token.token}")

    @staticmethod
    def validate_config(notification):
        """Validate push configuration"""
        from .models import PushToken
        return PushToken.objects.filter(
            user=notification.user,
            is_active=True
        ).exists()
```

### **SMS Channel**
```python
# apps/notifications/channels/sms.py
from .base import BaseChannel

class SMSChannel(BaseChannel):
    """SMS notification channel"""

    @staticmethod
    def send(notification):
        """Send notification via SMS"""
        if not notification.user or not notification.user.phone:
            logger.warning(f"No phone number for notification #{notification.id}")
            return

        # Get template
        template = NotificationTemplate.objects.filter(
            store=notification.store,
            notification_type=notification.notification_type
        ).first()

        if template:
            rendered = template.render(notification.metadata)
            message = rendered.get('sms', notification.message)
        else:
            message = notification.message

        # Send via SMS service (implementation depends on provider)
        # This is a placeholder for actual SMS service integration
        logger.info(f"SMS notification sent to {notification.user.phone}")

    @staticmethod
    def validate_config(notification):
        """Validate SMS configuration"""
        return notification.user and notification.user.phone
```

---

## 🔄 Celery Tasks

### **Async Notification Sending**
```python
# apps/notifications/tasks.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_notification(self, notification_id):
    """
    Async notification sending task
    """
    from .models import Notification
    from .services import NotificationService

    try:
        notification = Notification.objects.get(id=notification_id)
        result = NotificationService.send_notification(notification)

        return {
            'notification_id': notification_id,
            'status': result.status
        }

    except Notification.DoesNotExist:
        logger.error(f"Notification #{notification_id} not found")
        raise

    except Exception as exc:
        logger.error(f"Notification sending failed: {exc}")
        raise self.retry(exc=exc, countdown=60)

@shared_task
def cleanup_old_notifications(days=90):
    """
    Clean up old notification records
    """
    from django.utils import timezone
    from .models import Notification

    cutoff = timezone.now() - timezone.timedelta(days=days)
    deleted_count = Notification.objects.filter(
        created_at__lt=cutoff,
        status='read'
    ).delete()[0]

    logger.info(f"Cleaned up {deleted_count} old notifications")
    return deleted_count

@shared_task
def send_digest_notifications():
    """
    Send digest notifications for users with digest enabled
    """
    from .models import Notification, NotificationPreference
    from django.utils import timezone

    # Get users with digest enabled
    preferences = NotificationPreference.objects.filter(
        digest_enabled=True
    ).select_related('user')

    for preference in preferences:
        # Get pending notifications
        cutoff = timezone.now() - timezone.timedelta(hours=24)
        notifications = Notification.objects.filter(
            user=preference.user,
            store=preference.store,
            status='pending',
            created_at__gte=cutoff
        )

        if notifications.exists():
            # Create digest notification
            NotificationService.create_notification(
                store=preference.store,
                notification_type='digest',
                title=f'Your Daily Digest',
                message=f'You have {notifications.count()} new notifications',
                user=preference.user,
                channels=['email'],
                metadata={'notification_count': notifications.count()}
            )

            # Mark as delivered
            notifications.update(status='delivered', delivered_at=timezone.now())

    logger.info("Digest notifications sent")
```

---

## 🔒 Security Rules

### **Notification Security**
- **User Privacy**: Only send notifications to authorized users
- **Data Minimization**: Only include necessary data in notifications
- **Rate Limiting**: Implement rate limiting on notification endpoints
- **Content Validation**: Validate all notification content
- **Channel Validation**: Validate channel configurations
- **Opt-out Support**: Allow users to opt-out of notifications
- **Secure Templates**: Prevent template injection attacks
- **Audit Logging**: Log all notification events

---

## 📊 Performance Rules

### **Delivery Optimization**
- **Async Sending**: All notification sending must be asynchronous
- **Batch Processing**: Process multiple notifications in batches
- **Queue Management**: Use Celery for notification queue
- **Cleanup**: Regular cleanup of old notifications
- **Caching**: Cache notification templates

### **Database Optimization**
- **Indexes**: Add indexes on frequently queried fields
- **Query Optimization**: Use `select_related` for user lookups
- **Bulk Operations**: Use bulk operations for cleanup
- **Partitioning**: Consider partitioning large notification tables by date

---

## 🧪 Testing Rules

### **Required Coverage**
- **Models**: 95% code coverage
- **Services**: 100% code coverage
- **Channels**: 100% code coverage
- **Views**: 90% code coverage

### **Test Examples**
```python
# apps/notifications/tests/test_services.py
from django.test import TestCase
from ..models import Notification, NotificationPreference
from ..services import NotificationService

class NotificationServiceTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', slug='test-store')
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password'
        )

    def test_create_notification(self):
        """Test notification creation"""
        notification = NotificationService.create_notification(
            store=self.store,
            notification_type='order.created',
            title='Order Created',
            message='Your order has been created',
            user=self.user
        )

        self.assertEqual(notification.notification_type, 'order.created')
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.status, 'pending')

    def test_mark_as_read(self):
        """Test marking notification as read"""
        notification = Notification.objects.create(
            store=self.store,
            notification_type='order.created',
            title='Order Created',
            message='Your order has been created',
            user=self.user
        )

        notification.mark_as_read()

        self.assertEqual(notification.status, 'read')
        self.assertIsNotNone(notification.read_at)
```

---

## 🔗 Integration Rules

### **Required Integrations**
- **smtp.md**: Email channel implementation
- **accounts.md**: User authentication and preferences
- **stores.md**: Store scoping
- **logs.md**: Activity logging
- **core.md**: TenantModel and TenantViewSet

### **Integration Examples**
```python
# Integration with ecommerce.md for order notifications
from signals import order_created

@receiver(order_created)
def send_order_notifications(sender, instance, **kwargs):
    """Send notifications on order creation"""
    NotificationService.create_notification(
        store=instance.store,
        notification_type='order.created',
        title='Order Created',
        message=f'Your order #{instance.order_number} has been created',
        user=instance.customer.user,
        channels=['email', 'in_app'],
        metadata={
            'order_id': instance.id,
            'order_number': instance.order_number,
            'total': float(instance.total)
        }
    )

# Integration with forms.md for form submissions
from signals import form_submitted

@receiver(form_submitted)
def send_form_notifications(sender, instance, **kwargs):
    """Send notifications on form submission"""
    NotificationService.create_notification(
        store=instance.form_template.store,
        notification_type='form.submitted',
        title='Form Submitted',
        message=f'New form submission: {instance.form_template.title}',
        channels=['email', 'in_app'],
        metadata={
            'form_id': instance.form_template.form_id,
            'submission_id': instance.id
        }
    )
```

---

## 📈 Notification Types Reference

### **Ecommerce Notifications**
- `order.created` - New order created
- `order.shipped` - Order shipped
- `order.delivered` - Order delivered
- `payment.received` - Payment received
- `product.low_stock` - Product low stock warning
- `product.out_of_stock` - Product out of stock

### **Content Notifications**
- `page.published` - Page published
- `post.published` - Blog post published
- `comment.added` - Comment added

### **User Notifications**
- `user.registered` - New user registered
- `password.reset` - Password reset requested
- `email.verified` - Email verified

### **System Notifications**
- `system.alert` - System alert
- `digest` - Daily digest
- `custom` - Custom notification

---

## 🚀 Deployment Notes

### **Required Dependencies**
```python
# requirements.txt
celery>=5.3.0
```

### **Celery Configuration**
```python
# settings.py
CELERY_BEAT_SCHEDULE = {
    'cleanup-notifications': {
        'task': 'apps.notifications.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'send-digest-notifications': {
        'task': 'apps.notifications.tasks.send_digest_notifications',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
}
```

### **Monitoring**
- Monitor notification delivery success rates
- Track channel-specific failures
- Alert on high failure rates
- Monitor queue sizes

---

## 📚 Best Practices

1. **Always use async sending** - Never block on notification delivery
2. **Respect user preferences** - Honor opt-out requests
3. **Validate all content** - Prevent injection attacks
4. **Log all deliveries** - Maintain audit trail
5. **Rate limit endpoints** - Prevent abuse
6. **Clean up old records** - Prevent table bloat
7. **Monitor performance** - Track delivery times and success rates
8. **Provide clear messages** - Help users understand notifications
9. **Use templates** - Ensure consistent messaging
10. **Support digest mode** - Reduce notification fatigue

---

## 🔧 Management Commands

### **Cleanup Old Notifications**
```bash
python manage.py cleanup_notifications --days=90
```

### **Send Digest Notifications**
```bash
python manage.py send_digest
```

---

## 📝 API Documentation

### **Base URL**
```
/v2/api/notifications/
```

### **Endpoints**

#### Notifications
- `GET /v2/api/notifications/` - List notifications
- `POST /v2/api/notifications/` - Create notification
- `GET /v2/api/notifications/{id}/` - Get notification details
- `POST /v2/api/notifications/{id}/mark_read/` - Mark as read
- `POST /v2/api/notifications/{id}/resend/` - Resend notification

#### Notification Preferences
- `GET /v2/api/notification-preferences/` - List preferences
- `POST /v2/api/notification-preferences/` - Create preference
- `GET /v2/api/notification-preferences/{id}/` - Get preference details
- `PUT /v2/api/notification-preferences/{id}/` - Update preference

---

## 🎯 Implementation Checklist

- [ ] Create Notification, NotificationPreference, NotificationTemplate models
- [ ] Implement NotificationService
- [ ] Create channel implementations (Email, In-App, Push, SMS)
- [ ] Create Celery tasks for async sending
- [ ] Create API endpoints (NotificationViewSet, NotificationPreferenceViewSet)
- [ ] Add admin interface
- [ ] Implement notification preferences
- [ ] Add digest functionality
- [ ] Create tests (models, services, channels)
- [ ] Add monitoring and logging
- [ ] Implement cleanup tasks
- [ ] Create management commands
- [ ] Add integration examples
- [ ] Document notification types

---

## 📖 Version History

- **v1.0** - Initial version with multi-channel notification support

<!-- ===============================================================================
 END NOTIFICATIONS.MD
 ================================================================================= -->


<!-- ===============================================================================
 START POSTS.MD
 ================================================================================= -->
# Posts Module Rules v1.1

## 🎯 Purpose
This document defines strict development rules for the **posts** module in CMS-Updated backend, providing a unified content model for pages, blogs, and custom post types with V2-only clean architecture.

## 🏗️ Posts Module Structure

```
apps/backend/modules/posts/
├── __init__.py
├── admin.py
├── apps.py
├── migrations/
├── v1/                      # Legacy implementation
│   ├── blogs/
│   ├── ctp/
│   ├── pages/
│   └── views.py
└── v2/                      # Current implementation
    ├── __init__.py
    ├── admin.py
    ├── serializers.py
    ├── services.py
    ├── urls.py
    ├── views/
    │   ├── __init__.py
    │   ├── posts.py
    │   ├── taxonomies.py
    │   └── terms.py
    ├── models.py
    └── tests/
        ├── __init__.py
        ├── test_models.py
        ├── test_views.py
        └── test_services.py
```

## 🧾 Authority
- Owner: Content Lead
- Enforced By: models.py, services.py, views
- Scope: Store-scoped

## 📋 Core Models

### 2.1 PostType
```python
class PostType(models.Model):
    """Define content types (blog, page, or custom)"""
    BUILTIN_TYPES = ['post', 'page']

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, null=True, blank=True)
    is_public = models.BooleanField(default=True)
    is_hierarchical = models.BooleanField(default=False)
    # ... other fields ...
```

### 2.2 Post
```python
class Post(models.Model):
    """Unified post model for all content types"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('scheduled', 'Scheduled'),
        ('private', 'Private'),
        ('trash', 'Trash'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, db_index=True)
    content = models.TextField()
    post_type = models.ForeignKey(PostType, on_delete=models.CASCADE)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    # ... other fields ...
```

### 2.3 Taxonomy & Terms
```python
class Taxonomy(models.Model):
    """Categories, Tags, and custom taxonomies"""
    TAXONOMY_TYPES = [
        ('category', 'Category'),
        ('tag', 'Tag'),
        ('custom', 'Custom'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    taxonomy_type = models.CharField(max_length=20, choices=TAXONOMY_TYPES)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    # ... other fields ...

class Term(models.Model):
    """Taxonomy terms (individual categories/tags)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    taxonomy = models.ForeignKey(Taxonomy, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    # ... other fields ...
```

## 🌐 API Endpoints

### 3.1 Posts API
```
GET    /v2/api/posts/             # List posts (with filters)
POST   /v2/api/posts/             # Create post
GET    /v2/api/posts/{id}/        # Get post
PUT    /v2/api/posts/{id}/        # Update post
DELETE /v2/api/posts/{id}/        # Delete post
POST   /v2/api/posts/{id}/publish/ # Publish post
```

### 3.2 Taxonomies API
```
GET    /v2/api/taxonomies/        # List taxonomies
POST   /v2/api/taxonomies/        # Create taxonomy
GET    /v2/api/taxonomies/{id}/   # Get taxonomy
PUT    /v2/api/taxonomies/{id}/   # Update taxonomy
DELETE /v2/api/taxonomies/{id}/   # Delete taxonomy
```

## ⚙️ Services Layer

### 4.1 PostService with Logging
```python
# v2/services.py
from apps.logs.tasks import log_event_async
from django.utils import timezone

class PostService:
    @staticmethod
    def create_post(store, user, post_type, **data):
        """Create a new post with validation and logging"""
        from .models import Post

        # Create post logic
        post = Post.objects.create(
            store=store,
            post_type=post_type,
            author=user,
            **data
        )

        # Log the creation
        log_event_async.delay(
            event_type='POST_CREATED',
            message=f'Created {post_type.name} "{post.title}"',
            store=store,
            user=user.id,
            metadata={
                'post_id': str(post.id),
                'post_type': post_type.slug,
                'status': post.status
            }
        )
        return post

    @staticmethod
    def update_post(post, user, **data):
        """Update existing post with revision tracking and logging"""
        from .models import PostRevision

        # Create revision before update
        revision = PostRevision.objects.create(
            post=post,
            user=user,
            title=post.title,
            content=post.content,
            excerpt=post.excerpt,
            custom_fields=post.custom_fields,
            revision_number=post.revisions.count() + 1
        )

        # Update post
        for field, value in data.items():
            setattr(post, field, value)
        post.save()

        # Log the update
        log_event_async.delay(
            event_type='POST_UPDATED',
            message=f'Updated {post.post_type.name} "{post.title}"',
            store=post.store,
            user=user.id,
            metadata={
                'post_id': str(post.id),
                'revision_id': str(revision.id),
                'status': post.status
            }
        )
        return post
```

## 🛡️ Security & Permissions

### 5.1 Store-Scoped Views
```python
# v2/views/base.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

class StoreScopedViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet that automatically filters by store.
    All ViewSets must inherit from this and filter by request.store
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request, 'store'):
            return queryset.filter(store=self.request.store)
        return queryset.none()

    def perform_create(self, serializer):
        if hasattr(self.request, 'store'):
            serializer.save(store=self.request.store)
        else:
            raise PermissionDenied("Store context is required")

# Example usage
class PostViewSet(StoreScopedViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, PostPermissions]
```

### 5.2 Permission Classes
```python
# v2/permissions.py
from rest_framework import permissions

class PostPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check store access and user permissions
        return request.user.has_perm('posts.add_post')

    def has_object_permission(self, request, view, obj):
        # Object-level permission check
        return obj.store in request.user.stores.all()
```

## 🧪 Testing Examples

### 6.1 Model Tests
```python
# tests/test_models.py
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from ..models import Post, PostType, Store
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestPostModel:
    def test_create_post(self):
        """Test post creation and string representation"""
        store = Store.objects.create(name="Test Store")
        post_type = PostType.objects.create(
            name="Blog Post",
            slug="blog",
            store=store
        )
        post = Post.objects.create(
            title="Test Post",
            content="Test content",
            post_type=post_type,
            store=store
        )
        assert str(post) == "Test Post"
        assert post.slug == "test-post"

@pytest.mark.django_db
class TestPostViews:
    def test_list_posts(self, client, store, user, post_factory):
        """Test post listing with store filtering"""
        # Create test data
        post1 = post_factory(store=store, title="Store 1 Post")
        other_store = Store.objects.create(name="Other Store")
        post2 = post_factory(store=other_store, title="Store 2 Post")

        # Authenticate and make request
        client.force_authenticate(user=user)
        url = reverse('v2:post-list')
        response = client.get(url, HTTP_X_STORE_ID=str(store.id))

        # Verify response
        assert response.status_code == 200
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['title'] == "Store 1 Post"

    def test_permission_denied(self, client, other_store, user, post_factory):
        """Test access control for other store's posts"""
        post = post_factory(store=other_store)

        client.force_authenticate(user=user)
        url = reverse('v2:post-detail', args=[post.id])
        response = client.get(url, HTTP_X_STORE_ID=str(user.stores.first().id))

        assert response.status_code == 404  # Not 403 to avoid leaking existence
```

## 💡 Best Practices

### 7.1 Content Management
- Use PostType for different content types (blog, page, etc.)
- Implement proper slug generation and validation
- Support both hierarchical and non-hierarchical content
- Include revision history for all content changes

### 7.2 Performance
- Use select_related/prefetch_related for related lookups
- Implement caching for frequently accessed content
- Use pagination for post listings
- Optimize media handling with CDN support

### 7.3 SEO
- Generate SEO-friendly URLs
- Support meta tags and OpenGraph
- Implement canonical URLs
- Generate sitemaps for content

## 🔄 Migration & Legacy Support

### 8.1 Migration Command
```python
# management/commands/migrate_posts.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.stores.models import Store
from ...v2.models import PostType, Post

class Command(BaseCommand):
    help = 'Migrate legacy posts to v2 structure'

    def handle(self, *args, **options):
        self.stdout.write("Starting post migration...")

        # Create default post types for each store
        for store in Store.objects.all():
            # Create or get blog post type
            post_type, created = PostType.objects.get_or_create(
                store=store,
                slug='blog',
                defaults={
                    'name': 'Blog Post',
                    'is_public': True,
                    'supports_comments': True
                }
            )

            if created:
                self.stdout.write(f"Created post type 'blog' for {store.name}")

        # Migrate legacy posts
        from ...v1.blogs.models import BlogPost
        migrated = 0

        for legacy_post in BlogPost.objects.all():
            post_type = PostType.objects.get(store=legacy_post.store, slug='blog')

            Post.objects.update_or_create(
                legacy_id=legacy_post.id,
                store=legacy_post.store,
                defaults={
                    'title': legacy_post.title,
                    'content': legacy_post.content,
                    'post_type': post_type,
                    'status': 'published' if legacy_post.is_published else 'draft',
                    'created_at': legacy_post.created_at,
                    'updated_at': legacy_post.updated_at,
                    'published_at': legacy_post.published_date
                }
            )
            migrated += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully migrated {migrated} posts')
        )
```

## 9. Integration

### 9.1 Media Handling
- Store media in store-specific directories
- Support image optimization
- Implement responsive images
- Secure file uploads

### 9.2 Search Integration
- Index content for search
- Support full-text search
- Implement search filters
- Highlight search terms in results

## 10. Versioning & Backward Compatibility

### 10.1 API Versioning
- Maintain v1 for backward compatibility
- Use URL versioning (/v1/, /v2/)
- Document deprecated endpoints
- Provide migration guides

### 10.2 Data Migration
- Write data migrations for schema changes
- Test migrations with production-like data
- Provide rollback procedures
- Document breaking changes

## 11. Monitoring & Logging

### 11.1 Logging Events
Key events to log:
- `POST_CREATED`: When a new post is created
- `POST_UPDATED`: When a post is modified
- `POST_DELETED`: When a post is deleted
- `POST_PUBLISHED`: When a post is published
- `POST_VIEWED`: When a post is viewed (via tracking middleware)

### 11.2 Logging Implementation
```python
# Example logging in views
log_event_async.delay(
    event_type='POST_PUBLISHED',
    message=f'Published post: {post.title}',
    store=request.store,
    user=request.user.id,
    metadata={
        'post_id': str(post.id),
        'post_type': post.post_type.slug
    }
)
```

## 12. Security & Compliance

### 12.1 Store Isolation
- All ViewSets must inherit from `StoreScopedViewSet`
- Always filter by `request.store` in querysets
- Use `get_object_or_404` to prevent information disclosure

### 12.2 Data Protection
- Anonymize IP addresses in logs
- Implement proper access controls
- Follow GDPR guidelines for data retention
- Provide data export/erasure endpoints

## 🔒 Security
Enforced At: models.py, services.py, views
- MUST enforce store isolation on all queries
- MUST sanitize user input in post content
- MUST validate taxonomy and term assignments
- MUST prevent unauthorized post access across stores

## 🧪 Testing
- Unit tests MUST cover PostType, Post, Term, and Taxonomy models
- Integration tests MUST validate ViewSet permissions and store scoping
- Regression tests MUST ensure no cross-store data leakage
- Coverage MUST be >= 90%

## 🚫 Forbidden Patterns
- MUST NOT allow posts to be accessed across store boundaries
- MUST NOT bypass taxonomy validation in post creation
- MUST NOT use raw SQL in post queries
- MUST NOT expose unpublished posts to public APIs

## 🔗 Cross-References
- logs.md for post activity logging
- media.md for post media attachments
- cache.md for post content caching

## Review this final polished posts rules file carefully before applying.

<!-- ===============================================================================
 END POSTS.MD
 ================================================================================= -->


<!-- ===============================================================================
 START QUEUE.MD
 ================================================================================= -->
# Queue App Rules v1.0

## 🎯 Purpose

This document defines strict development rules for the **queue** system in CMS-Updated backend, implementing a unified task queue management system with Celery for asynchronous processing across all modules.

---

## 🏗️ Queue System Structure

### **Fixed Directory Structure**
```
apps/
├── queue/
│   ├── __init__.py
│   ├── services.py
│   ├── tasks.py
│   ├── management/
│   │   └── commands/
│   │       ├── list_tasks.py
│   │       ├── retry_failed_tasks.py
│   │       └── purge_tasks.py
│   └── tests/
│       ├── __init__.py
│       └── test_services.py
```

---

## 🧾 Authority
- Owner: Infrastructure Lead
- Enforced By: services.py, tasks.py, management commands
- Scope: Global

## 📋 Task Types

### **Task Categories**
```python
TASK_CATEGORIES = {
    'email': 'Email Sending',
    'webhook': 'Webhook Delivery',
    'notification': 'Notification Sending',
    'indexing': 'Search Indexing',
    'cache': 'Cache Management',
    'cleanup': 'Data Cleanup',
    'analytics': 'Analytics Processing',
    'export': 'Data Export',
    'import': 'Data Import',
    'custom': 'Custom Tasks',
}
```

---

## 🛠️ Services Layer

### **QueueService**
```python
# apps/queue/services.py
from celery import current_app
from celery.result import AsyncResult
import logging

logger = logging.getLogger(__name__)

class QueueService:
    """Shared queue management service"""

    @staticmethod
    def enqueue_task(task_name, args=None, kwargs=None, countdown=0, eta=None):
        """
        Enqueue a task for async execution
        """
        task = current_app.send_task(
            task_name,
            args=args or [],
            kwargs=kwargs or {},
            countdown=countdown,
            eta=eta
        )

        logger.info(f"Enqueued task: {task_name} (ID: {task.id})")
        return task

    @staticmethod
    def get_task_status(task_id):
        """
        Get task status
        """
        result = AsyncResult(task_id)

        status_map = {
            'PENDING': 'pending',
            'STARTED': 'started',
            'SUCCESS': 'success',
            'FAILURE': 'failed',
            'RETRY': 'retrying',
            'REVOKED': 'revoked'
        }

        return {
            'task_id': task_id,
            'status': status_map.get(result.status, result.status),
            'result': result.result if result.ready() else None,
            'traceback': result.traceback if result.failed() else None
        }

    @staticmethod
    def revoke_task(task_id, terminate=False):
        """
        Revoke a task
        """
        current_app.control.revoke(task_id, terminate=terminate)
        logger.info(f"Revoked task: {task_id}")
        return True

    @staticmethod
    def retry_task(task_id, countdown=60):
        """
        Retry a failed task
        """
        current_app.control.revoke(task_id, terminate=False)
        result = AsyncResult(task_id)

        if result.failed():
            # Re-enqueue the task
            task_name = result.args[0] if result.args else None
            if task_name:
                QueueService.enqueue_task(task_name, args=result.args, kwargs=result.kwargs, countdown=countdown)

        logger.info(f"Retrying task: {task_id}")
        return True

    @staticmethod
    def get_active_tasks():
        """
        Get list of active tasks
        """
        inspect = current_app.control.inspect()
        active = inspect.active()

        tasks = []
        for worker, task_list in (active or {}).items():
            for task in task_list:
                tasks.append({
                    'task_id': task['id'],
                    'name': task['name'],
                    'args': task['args'],
                    'kwargs': task['kwargs'],
                    'worker': worker
                })

        return tasks

    @staticmethod
    def get_scheduled_tasks():
        """
        Get list of scheduled tasks
        """
        inspect = current_app.control.inspect()
        scheduled = inspect.scheduled()

        tasks = []
        for worker, task_list in (scheduled or {}).items():
            for task in task_list:
                tasks.append({
                    'task_id': task['request']['id'],
                    'name': task['request']['name'],
                    'eta': task['request']['eta'],
                    'worker': worker
                })

        return tasks

    @staticmethod
    def get_worker_stats():
        """
        Get worker statistics
        """
        inspect = current_app.control.inspect()
        stats = inspect.stats()

        worker_stats = []
        for worker, stat in (stats or {}).items():
            worker_stats.append({
                'worker': worker,
                'total_tasks': stat.get('total', {}),
                'pool': stat.get('pool', {})
            })

        return worker_stats
```

---

## 🔄 Task Definition Standards

### **Task Template**
```python
# Standard task template
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def example_task(self, *args, **kwargs):
    """
    Example task with retry logic
    """
    try:
        # Task logic here
        result = perform_operation(*args, **kwargs)

        logger.info(f"Task completed successfully: {self.request.id}")
        return result

    except Exception as exc:
        logger.error(f"Task failed: {exc}")

        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

### **Task Best Practices**

1. **Always use `bind=True`** - Access to task context
2. **Set `max_retries`** - Prevent infinite retries
3. **Use exponential backoff** - Avoid overwhelming system
4. **Log all operations** - Maintain audit trail
5. **Handle exceptions** - Graceful error handling
6. **Use atomic transactions** - Prevent partial updates
7. **Validate inputs** - Ensure data integrity
8. **Document task purpose** - Clear task descriptions
9. **Set appropriate timeouts** - Prevent hanging tasks
10. **Use idempotent operations** - Safe to retry

---

## 📊 Task Monitoring

### **Task Monitoring Service**
```python
# apps/queue/services.py (continued)

class TaskMonitoringService:
    """Task monitoring service"""

    @staticmethod
    def get_task_stats(hours=24):
        """
        Get task statistics for time period
        """
        from django.utils import timezone
        from datetime import timedelta
        from .models import TaskLog

        since = timezone.now() - timedelta(hours=hours)

        logs = TaskLog.objects.filter(created_at__gte=since)

        stats = {
            'total': logs.count(),
            'success': logs.filter(status='success').count(),
            'failed': logs.filter(status='failed').count(),
            'retrying': logs.filter(status='retrying').count(),
            'revoked': logs.filter(status='revoked').count(),
            'avg_duration': logs.filter(status='success').aggregate(
                avg=models.Avg('duration_ms')
            )['avg__duration'] or 0
        }

        return stats

    @staticmethod
    def get_slow_tasks(threshold_ms=5000):
        """
        Get slow tasks
        """
        from .models import TaskLog

        return TaskLog.objects.filter(
            duration_ms__gt=threshold_ms
        ).order_by('-duration_ms')

    @staticmethod
    def get_failing_tasks(limit=50):
        """
        Get frequently failing tasks
        """
        from .models import TaskLog
        from django.db.models import Count

        return TaskLog.objects.filter(
            status='failed'
        ).values('task_name').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]

    @staticmethod
    def log_task(task_id, task_name, status, result=None, duration_ms=None, error=None):
        """
        Log task execution
        """
        from .models import TaskLog

        TaskLog.objects.create(
            task_id=task_id,
            task_name=task_name,
            status=status,
            result=result,
            duration_ms=duration_ms,
            error_message=error
        )
```

---

## 🚀 Celery Configuration

### **Celery Settings**
```python
# settings.py

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Task Settings
CELERY_TASK_ALWAYS_EAGER = False  # Set to True for testing
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True

# Task Routing
CELERY_TASK_ROUTES = {
    'apps.email.*': {'queue': 'email'},
    'apps.webhooks.*': {'queue': 'webhooks'},
    'apps.notifications.*': {'queue': 'notifications'},
    'apps.search.*': {'queue': 'search'},
    'apps.cache.*': {'queue': 'cache'},
}

# Task Timeouts
CELERY_TASK_SOFT_TIME_LIMIT = 300  # 5 minutes
CELERY_TASK_TIME_LIMIT = 360  # 6 minutes

# Task Result Expiry
CELERY_RESULT_EXPIRES = 3600  # 1 hour

# Worker Concurrency
CELERY_WORKER_CONCURRENCY = 4

# Task Prefetch
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# Task Acknowledgement
CELERY_TASK_ACKS_LATE = True
CELERY_DISABLE_RATE_LIMITS = False
```

### **Celery Beat Schedule**
```python
# settings.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Email queue processing
    'process-email-queue': {
        'task': 'apps.email.tasks.process_email_queue',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },

    # Webhook deliveries
    'deliver-webhooks': {
        'task': 'apps.webhooks.tasks.deliver_webhook',
        'schedule': crontab(minute='*/1'),  # Every minute
    },

    # Cache cleanup
    'cleanup-cache': {
        'task': 'apps.cache.tasks.clear_cache',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },

    # Search index rebuild
    'rebuild-search-index': {
        'task': 'apps.search.tasks.rebuild_index',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },

    # Notification cleanup
    'cleanup-notifications': {
        'task': 'apps.notifications.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=4, minute=0),  # Daily at 4 AM
    },

    # Log cleanup
    'cleanup-logs': {
        'task': 'apps.logs.tasks.cleanup_old_logs',
        'schedule': crontab(hour=5, minute=0),  # Daily at 5 AM
    },
}
```

---

## 🔧 Management Commands

### **List Tasks**
```bash
# List active tasks
python manage.py list_tasks --status=active

# List scheduled tasks
python manage.py list_tasks --status=scheduled

# List failed tasks
python manage.py list_tasks --status=failed
```

### **Retry Failed Tasks**
```bash
# Retry all failed tasks
python manage.py retry_failed_tasks

# Retry specific task
python manage.py retry_failed_tasks --task-id=abc123
```

### **Purge Tasks**
```bash
# Purge all tasks
python manage.py purge_tasks

# Purge tasks by queue
python manage.py purge_tasks --queue=email
```

---

## 🧪 Testing Rules

### **Required Coverage**
- **Services**: 100% code coverage
- **Tasks**: 100% code coverage

### **Test Examples**
```python
# apps/queue/tests/test_services.py
from django.test import TestCase
from ..services import QueueService

class QueueServiceTest(TestCase):
    def test_enqueue_task(self):
        """Test task enqueueing"""
        task = QueueService.enqueue_task('test_task', args=['arg1'], kwargs={'key': 'value'})

        self.assertIsNotNone(task.id)

    def test_get_task_status(self):
        """Test getting task status"""
        task = QueueService.enqueue_task('test_task', args=['arg1'])
        status = QueueService.get_task_status(task.id)

        self.assertIn('status', status)
        self.assertIn('task_id', status)

    def test_revoke_task(self):
        """Test task revocation"""
        task = QueueService.enqueue_task('test_task', args=['arg1'], countdown=60)
        result = QueueService.revoke_task(task.id)

        self.assertTrue(result)
```

---

## 🔗 Integration Examples

### **Integration with webhooks.md**
```python
# apps/webhooks/tasks.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def deliver_webhook(self, delivery_id):
    """
    Async webhook delivery task
    """
    from .models import WebhookDelivery
    from .services import WebhookService

    try:
        delivery = WebhookDelivery.objects.select_related('webhook').get(id=delivery_id)
        result = WebhookService.deliver_webhook_sync(delivery)

        # Log task completion
        from apps.queue.services import TaskMonitoringService
        TaskMonitoringService.log_task(
            task_id=self.request.id,
            task_name='deliver_webhook',
            status='success',
            result={'delivery_id': delivery_id}
        )

        return {
            'delivery_id': delivery_id,
            'status': result.status
        }

    except Exception as exc:
        logger.error(f"Webhook delivery failed: {exc}")

        # Log task failure
        from apps.queue.services import TaskMonitoringService
        TaskMonitoringService.log_task(
            task_id=self.request.id,
            task_name='deliver_webhook',
            status='failed',
            error=str(exc)
        )

        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

### **Integration with notifications.md**
```python
# apps/notifications/tasks.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_notification(self, notification_id):
    """
    Async notification sending task
    """
    from .models import Notification
    from .services import NotificationService

    try:
        notification = Notification.objects.get(id=notification_id)
        result = NotificationService.send_notification(notification)

        # Log task completion
        from apps.queue.services import TaskMonitoringService
        TaskMonitoringService.log_task(
            task_id=self.request.id,
            task_name='send_notification',
            status='success',
            result={'notification_id': notification_id}
        )

        return {
            'notification_id': notification_id,
            'status': result.status
        }

    except Exception as exc:
        logger.error(f"Notification sending failed: {exc}")

        # Log task failure
        from apps.queue.services import TaskMonitoringService
        TaskMonitoringService.log_task(
            task_id=self.request.id,
            task_name='send_notification',
            status='failed',
            error=str(exc)
        )

        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

---

## 📊 Task Logging Model

### **TaskLog Model**
```python
# apps/queue/models.py
from django.db import models
from core.models import TenantModel

class TaskLog(TenantModel):
    """
    Task execution log for monitoring
    """

    # Core fields
    task_id = models.CharField(max_length=255, db_index=True)
    task_name = models.CharField(max_length=255, db_index=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('started', 'Started'),
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('retrying', 'Retrying'),
            ('revoked', 'Revoked')
        ],
        db_index=True
    )

    # Results
    result = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    # Timing
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta(TenantModel.Meta):
        db_table = 'queue_task_log'
        indexes = [
            models.Index(fields=['store', 'status', 'created_at']),
            models.Index(fields=['task_name', 'created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.task_name} - {self.status}"
```

---

## 📚 Queue Best Practices

### **DO:**
1. **Use shared tasks** - Define tasks in tasks.py files
2. **Set appropriate timeouts** - Prevent hanging tasks
3. **Use exponential backoff** - Avoid overwhelming system
4. **Log all operations** - Maintain audit trail
5. **Monitor task queues** - Track performance
6. **Use idempotent operations** - Safe to retry
7. **Validate inputs** - Ensure data integrity
8. **Handle exceptions** - Graceful error handling
9. **Use atomic transactions** - Prevent partial updates
10. **Document task purpose** - Clear descriptions

### **DON'T:**
1. **Don't use eager mode in production** - Always async
2. **Don't create infinite loops** - Always set max_retries
3. **Don't ignore errors** - Handle all exceptions
4. **Don't block on tasks** - Always async
5. **Don't store large results** - Keep results small
6. **Don't use long-running tasks** - Break into smaller tasks
7. **Don't forget to log** - Maintain audit trail
8. **Don't retry forever** - Set reasonable limits
9. **Don't use blocking operations** - Keep tasks fast
10. **Don't assume success** - Always handle failures

---

## 🔒 Security
Enforced At: services.py, tasks.py, management commands
- MUST validate task payloads and arguments
- MUST sanitize inputs before task execution
- MUST enforce rate limits on task creation
- MUST log task execution for audit trails

## 🧪 Testing
- Unit tests MUST cover QueueService enqueue/dequeue and task validation
- Integration tests MUST validate Celery task execution and retries
- Regression tests MUST ensure no task data leakage across stores
- Coverage MUST be >= 90%

## 🚫 Forbidden Patterns
- MUST NOT use eager mode in production
- MUST NOT create infinite loops or unlimited retries
- MUST NOT block on task execution in request paths
- MUST NOT store sensitive data in task arguments

## 🔗 Cross-References
- logs.md for task execution logging
- cache.md for task result caching
- notifications.md for async notification tasks

## 📈 Monitoring

### **Metrics to Track**
- **Task Throughput**: Tasks processed per minute
- **Task Latency**: Average task duration
- **Error Rate**: Percentage of failed tasks
- **Queue Size**: Number of pending tasks
- **Worker Utilization**: CPU/memory usage

### **Alerting**
- **High Error Rate**: Alert if error rate > 10%
- **Large Queue**: Alert if queue size > 1000
- **Slow Tasks**: Alert if avg duration > 10s
- **Worker Down**: Alert if worker not responding

---

## 🎯 Implementation Checklist

- [ ] Create QueueService with standard methods
- [ ] Implement TaskMonitoringService
- [ ] Create TaskLog model
- [ ] Define task template standards
- [ ] Create Celery configuration
- [ ] Set up Celery Beat schedule
- [ ] Create management commands
- [ ] Add integration examples
- [ ] Create tests (services, tasks)
- [ ] Add monitoring and logging
- [ ] Document queue best practices
- [ ] Set up task monitoring

---

## 📖 Version History

- **v1.0** - Initial version with Celery integration

<!-- ===============================================================================
 END QUEUE.MD
 ================================================================================= -->


<!-- ===============================================================================
 START SEARCH.MD
 ================================================================================= -->
# Search App Rules v1.0

## 🎯 Purpose

This document defines strict development rules for the **search** app in CMS-Updated backend, implementing a centralized, store-scoped search system with Elasticsearch/OpenSearch integration for faceted search across content and commerce.

---

## 🏗️ Search App Structure

### **Fixed Directory Structure**
```
apps/
├── search/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── admin.py
│   ├── services.py
│   ├── tasks.py
│   ├── management/
│   │   └── commands/
│   │       ├── rebuild_index.py
│   │       └── index_content.py
│   ├── migrations/
│   ├── v2/
│   │   ├── __init__.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── tests/
│       ├── __init__.py
│       ├── test_services.py
│       └── test_views.py
```

---

## 🧾 Authority
- Owner: Search Lead
- Enforced By: models.py, services.py, tasks, views
- Scope: Store-scoped

## 📋 Core Models

### **Model Inheritance**
All search models must inherit from `TenantModel` for store scoping:

```python
from core.models import TenantModel
from django.db import models

class SearchIndex(TenantModel):
    # Store-scoped search index model
    pass
```

### **SearchIndex Model**
```python
# apps/search/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import TenantModel

User = get_user_model()

class SearchIndex(TenantModel):
    """
    Store-scoped search index configuration
    """

    # Core fields
    name = models.CharField(max_length=255)
    index_name = models.CharField(max_length=255, unique=True, db_index=True)

    # Index configuration
    content_types = models.JSONField(
        default=list,
        help_text="List of content types to index: ['Page', 'Post', 'Product']"
    )

    # Search configuration
    fields = models.JSONField(
        default=dict,
        help_text="Field mappings and search configuration"
    )

    # Facet configuration
    facets = models.JSONField(
        default=list,
        help_text="Facet configuration for filtering"
    )

    # Status
    is_active = models.BooleanField(default=True)
    last_reindexed_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = 'search_index'
        unique_together = [['store', 'name']]
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.index_name}"

    def get_index_name(self):
        """Get full index name with store prefix"""
        return f"{self.store.slug}_{self.index_name}"
```

### **SearchQuery Model**
```python
class SearchQuery(TenantModel):
    """
    Track search queries for analytics
    """

    # Core fields
    query = models.CharField(max_length=255, db_index=True)

    # Search context
    search_type = models.CharField(
        max_length=50,
        choices=[
            ('content', 'Content'),
            ('product', 'Product'),
            ('all', 'All')
        ]
    )

    # Results
    results_count = models.PositiveIntegerField(default=0)

    # User tracking
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    session_id = models.CharField(max_length=100, blank=True)

    # Filters applied
    filters = models.JSONField(default=dict)

    # Timing
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta(TenantModel.Meta):
        db_table = 'search_query'
        indexes = [
            models.Index(fields=['store', 'query']),
            models.Index(fields=['created_at']),
            models.Index(fields=['search_type']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.query} - {self.results_count} results"
```

---

## 🔌 API Endpoints

### **V2-Only Implementation**
All search endpoints must be V2-only with clean architecture:

#### SearchViewSet
```python
# apps/search/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from elasticsearch_dsl import Q

class SearchViewSet(TenantViewSet):
    """
    Search endpoints for public, customer, and dashboard
    """
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Override to return empty queryset (search uses Elasticsearch)"""
        return SearchIndex.objects.none()

    @extend_schema(
        summary="Search",
        description="Full-text search with faceting",
        responses={200: SearchResultsSerializer}
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Perform search query"""
        query = request.query_params.get('q', '')
        search_type = request.query_params.get('type', 'all')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))

        # Get filters
        filters = {
            k: v for k, v in request.query_params.items()
            if k not in ['q', 'type', 'page', 'page_size']
        }

        # Perform search
        from services.search import SearchService
        results = SearchService.search(
            store=request.store,
            query=query,
            search_type=search_type,
            filters=filters,
            page=page,
            page_size=page_size
        )

        # Track search query
        SearchService.track_search(
            store=request.store,
            query=query,
            search_type=search_type,
            results_count=results['total'],
            filters=filters,
            user=request.user if request.user.is_authenticated else None,
            duration_ms=results.get('duration_ms')
        )

        serializer = SearchResultsSerializer(results)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Get Facets",
        description="Get available facets for filtering",
        responses={200: FacetsSerializer}
    )
    @action(detail=False, methods=['get'])
    def facets(self, request):
        """Get available facets"""
        search_type = request.query_params.get('type', 'all')

        from services.search import SearchService
        facets = SearchService.get_facets(
            store=request.store,
            search_type=search_type
        )

        serializer = FacetsSerializer(facets)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Get Suggestions",
        description="Get search suggestions",
        responses={200: SuggestionsSerializer}
    )
    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """Get search suggestions"""
        query = request.query_params.get('q', '')

        from services.search import SearchService
        suggestions = SearchService.get_suggestions(
            store=request.store,
            query=query
        )

        serializer = SuggestionsSerializer(suggestions)
        return Response(serializer.data, status=status.HTTP_200_OK)
```

---

## 🛠️ Services Layer

### **Business Logic Centralization**
All search business logic must be in services.py:

#### SearchService
```python
# apps/search/services.py
from django.utils import timezone
import logging
import time

logger = logging.getLogger(__name__)

class SearchService:
    """Shared search management service"""

    @staticmethod
    def search(store, query, search_type='all', filters=None, page=1, page_size=20):
        """
        Perform search query with faceting
        """
        from elasticsearch_dsl import Search, A

        start_time = time.time()

        # Get search index
        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()

        if not index:
            return {
                'total': 0,
                'results': [],
                'facets': {},
                'page': page,
                'page_size': page_size
            }

        # Build Elasticsearch query
        s = Search(index=index.get_index_name())

        # Add query
        if query:
            s = s.query('multi_match', query=query, fields=['title^2', 'content', 'description'])

        # Add filters
        if filters:
            for key, value in filters.items():
                if value:
                    s = s.filter('term', **{key: value})

        # Add store filter
        s = s.filter('term', store_id=str(store.id))

        # Add aggregations for facets
        for facet in index.facets:
            s.aggs.bucket(facet['field'], 'terms', field=facet['field'], size=10)

        # Pagination
        start = (page - 1) * page_size
        s = s[start:start + page_size]

        # Execute search
        response = s.execute()

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Build results
        results = []
        for hit in response.hits:
            results.append({
                'id': hit.meta.id,
                'type': hit.get('type'),
                'title': hit.get('title'),
                'description': hit.get('description'),
                'url': hit.get('url'),
                'score': hit.meta.score
            })

        # Build facets
        facets = {}
        for facet in index.facets:
            field = facet['field']
            if field in response.aggregations:
                buckets = response.aggregations[field].buckets
                facets[field] = [
                    {'value': bucket.key, 'count': bucket.doc_count}
                    for bucket in buckets
                ]

        return {
            'total': response.hits.total.value,
            'results': results,
            'facets': facets,
            'page': page,
            'page_size': page_size,
            'duration_ms': duration_ms
        }

    @staticmethod
    def get_facets(store, search_type='all'):
        """Get available facets"""
        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()

        if not index:
            return []

        return index.facets

    @staticmethod
    def get_suggestions(store, query):
        """Get search suggestions"""
        from elasticsearch_dsl import Search

        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()

        if not index:
            return []

        # Build suggestion query
        s = Search(index=index.get_index_name())
        s = s.suggest(
            'title_suggest',
            query,
            completion={
                'field': 'title_suggest',
                'size': 10
            }
        )

        response = s.execute()

        suggestions = []
        if response.suggest.title_suggest:
            for suggestion in response.suggest.title_suggest[0].options:
                suggestions.append({
                    'text': suggestion.text,
                    'score': suggestion.score
                })

        return suggestions

    @staticmethod
    def index_document(store, document_type, document_id, data):
        """Index a document"""
        from elasticsearch import Elasticsearch

        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()

        if not index:
            return False

        # Add store ID to document
        data['store_id'] = str(store.id)
        data['type'] = document_type

        # Index document
        es = Elasticsearch()
        es.index(
            index=index.get_index_name(),
            id=document_id,
            body=data
        )

        logger.info(f"Indexed {document_type} #{document_id}")
        return True

    @staticmethod
    def delete_document(store, document_id):
        """Delete a document from index"""
        from elasticsearch import Elasticsearch

        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()

        if not index:
            return False

        # Delete document
        es = Elasticsearch()
        es.delete(
            index=index.get_index_name(),
            id=document_id
        )

        logger.info(f"Deleted document #{document_id}")
        return True

    @staticmethod
    def rebuild_index(store):
        """Rebuild entire search index"""
        from elasticsearch import Elasticsearch

        index = SearchIndex.objects.filter(
            store=store,
            is_active=True
        ).first()

        if not index:
            return False

        # Delete and recreate index
        es = Elasticsearch()
        index_name = index.get_index_name()

        # Delete existing index
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)

        # Create index with mappings
        mappings = {
            'properties': {
                'title': {'type': 'text', 'fields': {'suggest': {'type': 'completion'}}},
                'content': {'type': 'text'},
                'description': {'type': 'text'},
                'url': {'type': 'keyword'},
                'type': {'type': 'keyword'},
                'store_id': {'type': 'keyword'},
                'created_at': {'type': 'date'}
            }
        }

        es.indices.create(index=index_name, body={'mappings': mappings})

        # Reindex all content
        for content_type in index.content_types:
            SearchService._index_content_type(store, content_type)

        # Update last reindexed timestamp
        index.last_reindexed_at = timezone.now()
        index.save(update_fields=['last_reindexed_at'])

        logger.info(f"Rebuilt search index for store {store.slug}")
        return True

    @staticmethod
    def _index_content_type(store, content_type):
        """Index all documents of a content type"""
        # Get model based on content type
        if content_type == 'Page':
            from apps.pages.models import Page
            queryset = Page.objects.filter(store=store, status='published')
        elif content_type == 'Post':
            from apps.posts.models import Post
            queryset = Post.objects.filter(store=store, status='published')
        elif content_type == 'Product':
            from apps.ecommerce.models import Product
            queryset = Product.objects.filter(store=store, is_active=True)
        else:
            return

        # Index each document
        for item in queryset:
            data = {
                'title': item.title,
                'content': getattr(item, 'content', ''),
                'description': getattr(item, 'description', ''),
                'url': item.get_absolute_url(),
                'created_at': item.created_at.isoformat()
            }

            SearchService.index_document(
                store=store,
                document_type=content_type,
                document_id=str(item.id),
                data=data
            )

    @staticmethod
    def track_search(store, query, search_type, results_count, filters=None, user=None, duration_ms=None):
        """Track search query for analytics"""
        SearchQuery.objects.create(
            store=store,
            query=query,
            search_type=search_type,
            results_count=results_count,
            filters=filters or {},
            user=user,
            duration_ms=duration_ms
        )
```

---

## 🔄 Celery Tasks

### **Async Indexing**
```python
# apps/search/tasks.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def index_document(self, store_id, document_type, document_id, data):
    """
    Async document indexing
    """
    from .models import SearchIndex
    from .services import SearchService

    try:
        store = Store.objects.get(id=store_id)
        result = SearchService.index_document(
            store=store,
            document_type=document_type,
            document_id=document_id,
            data=data
        )

        return {
            'document_id': document_id,
            'indexed': result
        }

    except Store.DoesNotExist:
        logger.error(f"Store #{store_id} not found")
        raise

    except Exception as exc:
        logger.error(f"Document indexing failed: {exc}")
        raise self.retry(exc=exc, countdown=60)

@shared_task
def rebuild_index(store_id):
    """
    Async index rebuild
    """
    from .models import SearchIndex
    from .services import SearchService

    try:
        store = Store.objects.get(id=store_id)
        result = SearchService.rebuild_index(store)

        return {
            'store_id': store_id,
            'rebuilt': result
        }

    except Store.DoesNotExist:
        logger.error(f"Store #{store_id} not found")
        return {'store_id': store_id, 'rebuilt': False}
```

---

## 🔒 Security Rules

### **Search Security**
- **Store Isolation**: All searches must be store-scoped
- **Query Validation**: Validate all search queries
- **Rate Limiting**: Implement rate limiting on search endpoints
- **Result Filtering**: Filter results based on permissions
- **No Sensitive Data**: Never index sensitive information
- **Access Control**: Respect user permissions in results
- **SQL Injection Prevention**: Use parameterized queries
- **XSS Protection**: Sanitize search results

---

## 📊 Performance Rules

### **Search Optimization**
- **Async Indexing**: All indexing must be asynchronous
- **Batch Operations**: Use bulk operations for indexing
- **Query Optimization**: Use efficient Elasticsearch queries
- **Caching**: Cache search results where appropriate
- **Index Optimization**: Optimize Elasticsearch indexes

### **Database Optimization**
- **Indexes**: Add indexes on frequently queried fields
- **Query Optimization**: Use `select_related` for lookups
- **Bulk Operations**: Use bulk operations for indexing
- **Partitioning**: Consider partitioning large search tables

---

## 🧪 Testing Rules

### **Required Coverage**
- **Services**: 100% code coverage
- **Views**: 90% code coverage
- **Integration**: Critical path testing

### **Test Examples**
```python
# apps/search/tests/test_services.py
from django.test import TestCase
from ..services import SearchService

class SearchServiceTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', slug='test-store')
        self.index = SearchIndex.objects.create(
            store=self.store,
            name='Test Index',
            index_name='test_index',
            content_types=['Page'],
            fields={'title': 'text', 'content': 'text'},
            facets=[{'field': 'type', 'label': 'Type'}]
        )

    def test_search(self):
        """Test search functionality"""
        results = SearchService.search(
            store=self.store,
            query='test',
            search_type='content'
        )

        self.assertIn('results', results)
        self.assertIn('facets', results)

    def test_index_document(self):
        """Test document indexing"""
        data = {
            'title': 'Test Page',
            'content': 'Test content',
            'url': '/test-page'
        }

        result = SearchService.index_document(
            store=self.store,
            document_type='Page',
            document_id='1',
            data=data
        )

        self.assertTrue(result)
```

---

## 🔗 Integration Rules

### **Required Integrations**
- **stores.md**: Store scoping
- **logs.md**: Activity logging
- **core.md**: TenantModel and TenantViewSet

### **Integration Examples**
```python
# Integration with pages.md for page indexing
from signals import page_published

@receiver(page_published)
def index_page(sender, instance, **kwargs):
    """Index published page"""
    data = {
        'title': instance.title,
        'content': instance.content,
        'description': instance.description,
        'url': instance.get_absolute_url(),
        'created_at': instance.created_at.isoformat()
    }

    from services.search import SearchService
    SearchService.index_document(
        store=instance.store,
        document_type='Page',
        document_id=str(instance.id),
        data=data
    )

# Integration with ecommerce.md for product indexing
from signals import product_updated

@receiver(product_updated)
def index_product(sender, instance, **kwargs):
    """Index product"""
    data = {
        'title': instance.title,
        'content': instance.description,
        'description': instance.short_description,
        'url': instance.get_absolute_url(),
        'created_at': instance.created_at.isoformat()
    }

    from services.search import SearchService
    SearchService.index_document(
        store=instance.store,
        document_type='Product',
        document_id=str(instance.id),
        data=data
    )
```

---

## 📈 Search Configuration

### **Index Mappings**
```python
# Example Elasticsearch index mappings
MAPPINGS = {
    'properties': {
        'title': {
            'type': 'text',
            'fields': {
                'suggest': {'type': 'completion'}
            }
        },
        'content': {'type': 'text'},
        'description': {'type': 'text'},
        'url': {'type': 'keyword'},
        'type': {'type': 'keyword'},
        'store_id': {'type': 'keyword'},
        'created_at': {'type': 'date'}
    }
}
```

### **Facet Configuration**
```python
# Example facet configuration
FACETS = [
    {
        'field': 'type',
        'label': 'Type',
        'type': 'terms'
    },
    {
        'field': 'category_id',
        'label': 'Category',
        'type': 'terms'
    },
    {
        'field': 'price',
        'label': 'Price Range',
        'type': 'range',
        'ranges': [
            {'to': 50, 'label': 'Under $50'},
            {'from': 50, 'to': 100, 'label': '$50 - $100'},
            {'from': 100, 'label': '$100+'}
        ]
    }
]
```

---

## 🔒 Security
Enforced At: models.py, services.py, tasks, views
- MUST validate all search queries to prevent injection
- MUST enforce store isolation on all search indexes
- MUST sanitize user input before indexing
- MUST rate limit search endpoints

## 🧪 Testing
- Unit tests MUST cover SearchIndex creation and query validation
- Integration tests MUST validate Elasticsearch integration and faceting
- Regression tests MUST ensure no cross-store search leakage
- Coverage MUST be >= 90%

## 🚫 Forbidden Patterns
- MUST NOT allow raw Elasticsearch queries from user input
- MUST NOT bypass store filtering in search queries
- MUST NOT index sensitive data without sanitization
- MUST NOT expose search results across tenant boundaries

## 🔗 Cross-References
- logs.md for search query logging
- cache.md for search result caching
- queue.md for async indexing tasks

## 🚀 Deployment Notes

### **Required Dependencies**
```python
# requirements.txt
elasticsearch>=8.0.0
elasticsearch-dsl>=8.0.0
celery>=5.3.0
```

### **Elasticsearch Configuration**
```python
# settings.py
ELASTICSEARCH_HOSTS = ['http://localhost:9200']
ELASTICSEARCH_TIMEOUT = 30
```

### **Monitoring**
- Monitor search query performance
- Track search query analytics
- Alert on high query times
- Monitor index sizes

---

## 📚 Best Practices

1. **Always use async indexing** - Never block on indexing
2. **Validate all queries** - Prevent injection attacks
3. **Respect store isolation** - Never cross store boundaries
4. **Log search queries** - Maintain analytics
5. **Rate limit endpoints** - Prevent abuse
6. **Optimize indexes** - Regular index optimization
7. **Monitor performance** - Track query times
8. **Use suggestions** - Improve user experience
9. **Implement faceting** - Enable advanced filtering
10. **Test search queries** - Ensure relevance

---

## 🔧 Management Commands

### **Rebuild Index**
```bash
python manage.py rebuild_index --store=test-store
```

### **Index Content**
```bash
python manage.py index_content --type=Page
```

---

## 📝 API Documentation

### **Base URL**
```
/v2/api/search/
```

### **Endpoints**

#### Search
- `GET /v2/api/search/search/` - Perform search
- `GET /v2/api/search/facets/` - Get available facets
- `GET /v2/api/search/suggestions/` - Get search suggestions

### **Query Parameters**

#### Search
- `q` - Search query
- `type` - Search type (content, product, all)
- `page` - Page number (default: 1)
- `page_size` - Results per page (default: 20)
- `*` - Additional filters

#### Facets
- `type` - Facet type (content, product, all)

#### Suggestions
- `q` - Search query for suggestions

---

## 🎯 Implementation Checklist

- [ ] Create SearchIndex, SearchQuery models
- [ ] Implement SearchService
- [ ] Create API endpoints (SearchViewSet)
- [ ] Implement Elasticsearch integration
- [ ] Add faceting support
- [ ] Implement search suggestions
- [ ] Create Celery tasks for async indexing
- [ ] Add admin interface
- [ ] Create tests (services, views)
- [ ] Add monitoring and logging
- [ ] Implement index management
- [ ] Create management commands
- [ ] Add integration examples
- [ ] Document search configuration

---

## 📖 Version History

- **v1.0** - Initial version with Elasticsearch integration

<!-- ===============================================================================
 END SEARCH.MD
 ================================================================================= -->


<!-- ===============================================================================
 START SMTP.MD
 ================================================================================= -->
# SMTP Module Rules v1.0

## 1. Directory Structure
```
apps/backend/modules/smtp/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── migrations/
├── tasks.py
└── v1/
    ├── __init__.py
    ├── forms/
    ├── services.py
    ├── urls.py
    └── views/
        ├── __init__.py
        ├── configs.py
        ├── emails.py
        └── templates.py
```

## 2. Core Models

### 2.1 SmtpConfiguration
```python
class SmtpConfiguration(models.Model):
    PROVIDER_CHOICES = [
        ('gmail', 'Gmail'),
        ('outlook', 'Outlook'),
        ('sendgrid', 'SendGrid'),
        ('mailgun', 'Mailgun'),
        ('amazon_ses', 'Amazon SES'),
        ('custom', 'Custom SMTP'),
    ]

    # ... (keep existing fields)

    def save(self, *args, **kwargs):
        # Log configuration changes
        from apps.logs.services import log_event_async

        is_new = self._state.adding
        super().save(*args, **kwargs)

        log_event_async.delay(
            event_type='SMTP_CONFIG_SAVED' if not is_new else 'SMTP_CONFIG_CREATED',
            message=f"SMTP Config {'created' if is_new else 'updated'}: {self.name}",
            store=self.store,
            metadata={
                'config_id': str(self.id),
                'provider': self.provider,
                'is_default': self.is_default,
                'is_verified': self.is_verified
            }
        )
```

## 3. Services

### 3.1 EmailService with Logging
```python
# v1/services.py
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail as django_send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from apps.logs.services import log_event_async

class EmailService:
    @classmethod
    def send_email(
        cls,
        to_email: str,
        subject: str,
        html_content: str = "",
        text_content: str = "",
        from_email: str = None,
        smtp_config_id: str = None,
        store=None,
        user=None,
        template_id: str = None,
        context: dict = None
    ) -> dict:
        """
        Send email using specified SMTP configuration with full logging
        """
        log_data = {
            'to_email': to_email,
            'subject': subject,
            'template_id': str(template_id) if template_id else None,
            'smtp_config_id': str(smtp_config_id) if smtp_config_id else None,
            'store_id': str(store.id) if store else None,
            'user_id': str(user.id) if user else None
        }

        try:
            # Get SMTP config (implementation omitted for brevity)
            smtp_config = cls._get_smtp_config(smtp_config_id, store)

            # Log email sending attempt
            log_event_async.delay(
                event_type='EMAIL_SEND_ATTEMPT',
                message=f"Sending email to {to_email}",
                store=store,
                user=user,
                metadata=log_data
            )

            # Send email (implementation details)
            result = django_send_mail(
                subject=subject,
                message=text_content,
                from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                html_message=html_content,
                fail_silently=False,
                auth_user=smtp_config.username,
                auth_password=smtp_config.get_decrypted_password(),
                connection=smtp_config.get_connection()
            )

            # Log success
            log_event_async.delay(
                event_type='EMAIL_SEND_SUCCESS',
                message=f"Email sent to {to_email}",
                store=store,
                user=user,
                metadata={
                    **log_data,
                    'message_id': result.message_id if hasattr(result, 'message_id') else None
                }
            )

            return {'success': True, 'message_id': getattr(result, 'message_id', None)}

        except Exception as e:
            # Log failure
            log_event_async.delay(
                event_type='EMAIL_SEND_FAILED',
                message=f"Failed to send email to {to_email}: {str(e)}",
                level='ERROR',
                store=store,
                user=user,
                metadata={
                    **log_data,
                    'error': str(e),
                    'error_type': e.__class__.__name__
                }
            )
            raise

    @staticmethod
    @shared_task(bind=True, max_retries=3)
    def send_email_async(self, email_data):
        """Celery task for async email sending"""
        try:
            return EmailService.send_email(**email_data)
        except Exception as exc:
            self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

## 4. Admin & Dashboard Views

### 4.1 admin.py
```python
from django.contrib import admin
from django.utils.html import format_html
from .models import SmtpConfiguration, EmailTemplate, EmailLog

@admin.register(SmtpConfiguration)
class SmtpConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'host', 'port', 'is_default', 'is_verified', 'store')
    list_filter = ('provider', 'is_default', 'is_verified', 'store')
    search_fields = ('name', 'host', 'username')
    readonly_fields = ('last_tested', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'provider', 'store', 'is_default')
        }),
        ('SMTP Settings', {
            'fields': ('host', 'port', 'username', 'password', 'use_tls', 'use_ssl')
        }),
        ('Status', {
            'fields': ('is_verified', 'last_tested')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        # Encrypt password before saving
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'subject', 'is_active', 'store')
    list_filter = ('template_type', 'is_active', 'store')
    search_fields = ('name', 'subject', 'html_content')
    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        # Log template changes
        from apps.logs.services import log_event_async
        action = 'created' if not change else 'updated'
        log_event_async.delay(
            event_type='EMAIL_TEMPLATE_SAVED',
            message=f"Email template {obj.name} {action}",
            store=obj.store,
            user=request.user,
            metadata={
                'template_id': str(obj.id),
                'template_type': obj.template_type,
                'changes': form.changed_data if change else None
            }
        )
        super().save_model(request, obj, form, change)

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('to_email', 'subject', 'status', 'sent_at', 'store')
    list_filter = ('status', 'sent_at', 'store')
    search_fields = ('to_email', 'subject', 'message_id')
    readonly_fields = ('sent_at', 'delivered_at', 'opened_at', 'created_at')
    date_hierarchy = 'sent_at'
```

### 4.2 Dashboard API Views
```python
# v1/views/configs.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ...models import SmtpConfiguration
from .serializers import SmtpConfigSerializer
from ...services import SmtpService

class SmtpConfigViewSet(viewsets.ModelViewSet):
    serializer_class = SmtpConfigSerializer
    permission_classes = [IsAuthenticated, IsStoreAdmin]

    def get_queryset(self):
        return SmtpConfiguration.objects.filter(store=self.request.store)

    def perform_create(self, serializer):
        serializer.save(store=self.request.store)

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test SMTP connection"""
        config = self.get_object()
        try:
            is_valid = SmtpService.test_connection(config)
            return Response({
                'success': is_valid,
                'message': 'Connection successful' if is_valid else 'Connection failed'
            })
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
```

## 5. Migration & Legacy Support

### 5.1 Management Command: migrate_smtp.py
```python
# management/commands/migrate_smtp.py
from django.core.management.base import BaseCommand
from django.db import transaction
from legacy_app.models import LegacySmtpConfig
from ...models import SmtpConfiguration

class Command(BaseCommand):
    help = 'Migrate SMTP configurations from legacy system'

    def handle(self, *args, **options):
        count = 0

        for legacy in LegacySmtpConfig.objects.all():
            try:
                with transaction.atomic():
                    config = SmtpConfiguration.objects.create(
                        name=legacy.config_name,
                        provider=self._map_provider(legacy.provider_type),
                        host=legacy.smtp_host,
                        port=legacy.smtp_port or 587,
                        username=legacy.username,
                        password=legacy.encrypted_password,  # Assumes decryption handled
                        use_tls=legacy.use_tls,
                        use_ssl=legacy.use_ssl,
                        store_id=legacy.store_id,
                        is_default=legacy.is_primary,
                        is_verified=legacy.is_verified
                    )
                    count += 1
                    self.stdout.write(f"Migrated SMTP config: {config.name}")

            except Exception as e:
                self.stderr.write(f"Error migrating {legacy.config_name}: {str(e)}")

        self.stdout.write(self.style.SUCCESS(f'Successfully migrated {count} SMTP configurations'))

    def _map_provider(self, legacy_provider):
        """Map legacy provider names to new ones"""
        provider_map = {
            'google': 'gmail',
            'office365': 'outlook',
            'sendgrid': 'sendgrid',
            'custom': 'custom'
        }
        return provider_map.get(legacy_provider.lower(), 'custom')
```

## 6. Security Implementation

### 6.1 Password Encryption
```python
# models.py
from fernet_fields import EncryptedCharField

class SmtpConfiguration(models.Model):
    # ... other fields ...
    password = EncryptedCharField(max_length=255)

    def get_decrypted_password(self):
        """Get decrypted password for SMTP auth"""
        return self.password
```

### 6.2 Rate Limiting
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'emails': '100/hour',  # Per store
        'smtp_test': '10/hour',  # SMTP connection tests
    }
}

# views/configs.py
from rest_framework.throttling import UserRateThrottle

class EmailRateThrottle(UserRateThrottle):
    scope = 'emails'

    def get_cache_key(self, request, view):
        # Rate limit by store
        store_id = request.store.id if hasattr(request, 'store') else 'anon'
        return f'throttle_emails_{store_id}_{self.get_ident(request)}'
```

## 7. Testing Examples

### 7.1 Test Email Sending
```python
# tests/test_emails.py
import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from ..services import EmailService

class TestEmailService(TestCase):
    @patch('django.core.mail.send_mail')
    def test_send_email_success(self, mock_send):
        # Setup
        mock_send.return_value = 1

        # Test
        result = EmailService.send_email(
            to_email='test@example.com',
            subject='Test',
            html_content='<p>Test</p>',
            text_content='Test'
        )

        # Assert
        self.assertTrue(result['success'])
        mock_send.assert_called_once()

    @patch('django.core.mail.send_mail')
    def test_send_email_failure(self, mock_send):
        # Setup
        mock_send.side_effect = Exception('SMTP Error')

        # Test & Assert
        with self.assertRaises(Exception):
            EmailService.send_email(
                to_email='test@example.com',
                subject='Test',
                html_content='<p>Test</p>'
            )
```

### 7.2 Test SMTP Configuration
```python
# tests/test_smtp_config.py
from django.test import TestCase
from ..models import SmtpConfiguration

class TestSmtpConfiguration(TestCase):
    def test_password_encryption(self):
        # Setup
        config = SmtpConfiguration.objects.create(
            name='Test Config',
            host='smtp.example.com',
            username='user',
            password='secret',
            use_tls=True
        )

        # Test
        saved_config = SmtpConfiguration.objects.get(pk=config.pk)

        # Assert
        self.assertNotEqual(saved_config.password, 'secret')  # Should be encrypted
        self.assertEqual(saved_config.get_decrypted_password(), 'secret')
```

## 8. Celery Tasks

### 8.1 tasks.py
```python
from celery import shared_task
from django.conf import settings
from .models import EmailQueue
from .services import EmailService
from apps.logs.services import log_event_async

@shared_task(bind=True, max_retries=3)
def process_email_queue(self):
    """Process queued emails"""
    batch_size = getattr(settings, 'EMAIL_BATCH_SIZE', 50)

    # Get pending emails, ordered by priority and creation time
    queued_emails = EmailQueue.objects.filter(
        is_processed=False,
        scheduled_at__lte=timezone.now()
    ).order_by('priority', 'created_at')[:batch_size]

    for email in queued_emails:
        try:
            # Add tracking if enabled
            if email.is_tracked and email.html_content:
                email.html_content = EmailService.add_tracking(email, email.html_content)

            # Send email
            result = EmailService.send_email_async.delay({
                'to_email': email.to_email,
                'subject': email.subject,
                'html_content': email.html_content,
                'text_content': email.text_content,
                'smtp_config_id': str(email.smtp_config_id),
                'store_id': str(email.store_id),
                'template_id': str(email.template_id) if email.template_id else None,
                'track_opens': email.is_tracked,
                'track_clicks': email.is_tracked,
                'tracking_id': str(email.tracking_id) if email.is_tracked else None
            })

            # Mark as processed
            email.is_processed = True
            email.processed_at = timezone.now()
            email.status = 'processing'
            email.save()

            # Log sent event
            email.add_tracking_event('sent', {
                'queue_id': str(email.id),
                'scheduled_at': str(email.scheduled_at)
            })

        except Exception as e:
            # Handle retries
            email.retry_count += 1
            if email.retry_count >= email.max_retries:
                email.is_processed = True
                email.status = 'failed'
                email.error_message = str(e)

                # Log failure
                email.add_tracking_event('failed', {
                    'error': str(e),
                    'retry_count': email.retry_count,
                    'max_retries': email.max_retries
                })

            email.save()

            # Log error
            log_event_async.delay(
                event_type='EMAIL_QUEUE_ERROR',
                message=f'Failed to process queued email: {str(e)}',
                store=email.store,
                metadata={
                    'email_id': str(email.id),
                    'to_email': email.to_email,
                    'retry_count': email.retry_count,
                    'error': str(e)
                },
                level='ERROR'
            )

            # Retry with exponential backoff
            raise self.retry(exc=e, countdown=60 * (2 ** email.retry_count))
```

## 9. Email Tracking & Analytics

### 9.1 Tracking Pixel Implementation
```python
# v1/views/tracking.py
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseNotFound
from django.utils import timezone
import base64
from ...models import EmailLog, EmailTracking

@csrf_exempt
@require_http_methods(['GET'])
def track_email_open(request, tracking_id):
    """
    Endpoint for tracking email opens via 1x1 pixel
    """
    try:
        email_log = EmailLog.objects.get(tracking_id=tracking_id)

        # Add tracking event
        email_log.add_tracking_event(
            event_type='opened',
            event_data={
                'ip': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT'),
                'referer': request.META.get('HTTP_REFERER')
            },
            request=request
        )

        # Return transparent 1x1 GIF
        pixel = base64.b64decode('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7')
        response = HttpResponse(pixel, content_type='image/gif')

        # Cache control headers
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

        return response

    except EmailLog.DoesNotExist:
        return HttpResponseNotFound()
```

### 9.2 Click Tracking
```python
# v1/services.py
import re
import urllib.parse
from bs4 import BeautifulSoup

class EmailService:
    # ... existing methods ...

    URL_PATTERN = re.compile(
        r'https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )

    @classmethod
    def add_click_tracking(cls, email_log, content, is_html=True):
        """
        Convert all links in the email to tracked links
        Supports both HTML and plain text emails
        """
        if not email_log.is_tracked or not content:
            return content

        if is_html:
            return cls._track_html_links(email_log, content)
        return cls._track_text_links(email_log, content)

    @classmethod
    def _track_html_links(cls, email_log, html_content):
        """Track links in HTML emails"""
        soup = BeautifulSoup(html_content, 'html.parser')

        for link in soup.find_all('a', href=True):
            original_url = link['href']
            if not original_url or not original_url.startswith(('http://', 'https://')):
                continue

            # Create tracking URL
            tracking_url = cls._create_tracking_url(email_log, original_url)

            # Update link
            link['href'] = tracking_url

            # Add tracking class and style (if not already present)
            if 'tracked-link' not in link.get('class', []):
                link['class'] = link.get('class', []) + ['tracked-link']

            # Ensure link is visible in email clients
            link_style = link.get('style', '')
            if 'color:' not in link_style:
                link_style = (link_style + ';color: #2563eb;').strip(';')
                link['style'] = link_style

        return str(soup)

    @classmethod
    def _track_text_links(cls, email_log, text_content):
        """Track links in plain text emails"""
        def replace_match(match):
            original_url = match.group(0)
            tracking_url = cls._create_tracking_url(email_log, original_url)
            return f"{original_url} [Tracked: {tracking_url}]"

        return cls.URL_PATTERN.sub(replace_match, text_content)

    @classmethod
    def _create_tracking_url(cls, email_log, original_url):
        """Create a tracking URL for click tracking"""
        from django.urls import reverse
        import hashlib

        # Generate URL-safe hash of the original URL
        url_hash = hashlib.md5(original_url.encode()).hexdigest()[:8]

        # Create tracking URL
        tracking_path = reverse('smtp:track-click', kwargs={
            'tracking_id': str(email_log.tracking_id),
            'url_hash': url_hash
        })

        # Encode original URL as query parameter
        encoded_url = urllib.parse.quote(original_url)
        return f"{settings.SITE_URL}{tracking_path}?url={encoded_url}"
```

### 9.3 Webhook Handler with Security

#### 9.3.1 Security Considerations
- **Webhook Verification**: All webhook requests must be verified using provider signatures
- **Rate Limiting**: Implement rate limiting to prevent abuse
- **IP Whitelisting**: Optionally restrict incoming webhooks to known provider IPs
- **Request Timeout**: Verify webhook timestamps to prevent replay attacks

#### 9.3.2 Implementation
```python
# v1/views/webhooks.py
import hmac
import hashlib
import json
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from ...models import EmailLog, EmailTracking

logger = logging.getLogger(__name__)

# Webhook configuration (move to settings.py in production)
WEBHOOK_CONFIG = {
    'sendgrid': {
        'signing_key': settings.SENDGRID_WEBHOOK_SIGNING_KEY,
        'signature_header': 'X-Twilio-Email-Event-Webhook-Signature',
        'timestamp_header': 'X-Twilio-Email-Event-Webhook-Timestamp',
        'max_age_seconds': 300,  # 5 minutes
    },
    'mailgun': {
        'signing_key': settings.MAILGUN_WEBHOOK_SIGNING_KEY,
        'signature_param': 'signature',
        'timestamp_param': 'timestamp',
        'token_param': 'token',
    }
}

@method_decorator(csrf_exempt, name='dispatch')
class EmailWebhookView(APIView):
    permission_classes = [AllowAny]

    def verify_webhook_signature(self, request, provider):
        """Verify webhook signature using provider's signing key"""
        config = WEBHOOK_CONFIG.get(provider, {})

        if provider == 'sendgrid':
            # Verify SendGrid signature
            signature = request.headers.get(config['signature_header'])
            timestamp = request.headers.get(config['timestamp_header'])

            if not all([signature, timestamp, config['signing_key']]):
                logger.warning('Missing required signature headers or signing key')
                return False

            # Verify timestamp (prevent replay attacks)
            try:
                event_time = datetime.fromtimestamp(int(timestamp))
                if (datetime.utcnow() - event_time) > timedelta(seconds=config['max_age_seconds']):
                    logger.warning('Webhook timestamp too old')
                    return False
            except (ValueError, TypeError):
                logger.warning('Invalid timestamp in webhook')
                return False

            # Verify signature
            payload = f"{timestamp}{request.body.decode('utf-8')}"
            expected_signature = hmac.new(
                key=config['signing_key'].encode('utf-8'),
                msg=payload.encode('utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)

        elif provider == 'mailgun':
            # Similar verification for Mailgun
            data = request.data
            signature = data.get(config['signature_param'])
            timestamp = data.get(config['timestamp_param'])
            token = data.get(config['token_param'])

            if not all([signature, timestamp, token, config['signing_key']]):
                return False

            # Verify timestamp (Mailgun uses seconds since epoch)
            try:
                if (time.time() - int(timestamp)) > config.get('max_age_seconds', 300):
                    return False
            except (ValueError, TypeError):
                return False

            # Verify signature
            signing_data = f"{timestamp}{token}"
            expected_signature = hmac.new(
                key=config['signing_key'].encode('utf-8'),
                msg=signing_data.encode('utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)

        return False  # Default to deny for unknown providers

    def post(self, request, provider=None, *args, **kwargs):
        """
        Handle email webhooks from various providers with signature verification
        """
        try:
            # Get provider handler
            provider = provider or request.GET.get('provider', 'sendgrid')

            # Verify webhook signature
            if not self.verify_webhook_signature(request, provider):
                logger.warning(f'Invalid webhook signature from {provider}')
                return Response(
                    {'error': 'Invalid signature'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Get handler for this provider
            handler = getattr(self, f'handle_{provider}', None)
            if not handler:
                return Response(
                    {'error': 'Unsupported email provider'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Process events
            events = handler(request.data)
            return Response({
                'status': 'success',
                'events_processed': len(events)
            })

        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def handle_sendgrid(self, data):
        """Process SendGrid webhook events"""
        events = []

        # Handle both array and single event
        event_list = data if isinstance(data, list) else [data]

        for event in event_list:
            try:
                event_type = event.get('event')
                tracking_id = event.get('tracking_id') or event.get('email_id')

                if not tracking_id:
                    continue

                # Map SendGrid event types to our system
                event_map = {
                    'processed': 'sent',
                    'delivered': 'delivered',
                    'open': 'opened',
                    'click': 'clicked',
                    'bounce': 'bounced',
                    'dropped': 'dropped',
                    'spamreport': 'spam',
                    'unsubscribe': 'unsubscribed'
                }

                mapped_type = event_map.get(event_type)
                if not mapped_type:
                    continue

                # Find and update email log
                email_log = EmailLog.objects.get(tracking_id=tracking_id)
                email_log.add_tracking_event(
                    event_type=mapped_type,
                    event_data=event
                )

                # Update email status if needed
                if mapped_type in ['delivered', 'bounced', 'dropped']:
                    email_log.status = mapped_type
                    email_log.save(update_fields=['status', 'updated_at'])

                events.append(mapped_type)

            except EmailLog.DoesNotExist:
                logger.warning(f"Email log not found for tracking_id: {tracking_id}")
            except Exception as e:
                logger.error(f"Error processing {event_type} event: {str(e)}")

        return events
```

### 9.4 Privacy & Compliance

#### 9.4.1 GDPR & Privacy Considerations

1. **IP Anonymization**
   ```python
   def anonymize_ip(ip_address):
       """Anonymize IP address by zeroing the last octet"""
       if not ip_address or ip_address == '127.0.0.1':
           return ip_address

       # Handle IPv4
       if '.' in ip_address:
           parts = ip_address.split('.')
           if len(parts) == 4:
               return f"{'.'.join(parts[:3])}.0"

       # Handle IPv6 (simplified)
       if ':' in ip_address:
           return ':'.join(ip_address.split(':')[:4] + ['0000'] * 4)

       return ip_address
   ```

2. **Data Retention**
   - Store raw IPs for security logs (14 days)
   - Anonymize IPs in tracking events after 30 days
   - Provide data export/deletion endpoints for compliance

3. **User Consent**
   - Add tracking preference in user/account settings
   - Include tracking info in email footers
   - Support one-click unsubscribe

### 9.5 Dashboard UI Implementation

#### 9.5.1 Frontend Components

1. **Email Analytics Dashboard**
   - Real-time delivery metrics
   - Interactive charts for open/click rates
   - Bounce and complaint tracking
   - Device/geography breakdowns

2. **Example Chart.js Implementation**
   ```html
   <div class="chart-container">
     <canvas id="emailMetricsChart"></canvas>
   </div>

   <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
   <script>
   // Fetch data from backend API
   fetch('/api/v1/analytics/emails/?days=30')
     .then(response => response.json())
     .then(data => {
       const ctx = document.getElementById('emailMetricsChart').getContext('2d');
       new Chart(ctx, {
         type: 'line',
         data: {
           labels: data.time_series.map(d => d.date),
           datasets: [{
             label: 'Open Rate %',
             data: data.time_series.map(d => d.open_rate),
             borderColor: 'rgb(75, 192, 192)',
             tension: 0.1
           }, {
             label: 'Click Rate %',
             data: data.time_series.map(d => d.click_through_rate),
             borderColor: 'rgb(54, 162, 235)',
             tension: 0.1
           }]
         },
         options: {
           responsive: true,
           plugins: {
             title: { display: true, text: 'Email Engagement (30 Days)' },
             tooltip: { mode: 'index', intersect: false },
             legend: { position: 'bottom' }
           },
           scales: {
             y: {
               min: 0,
               max: 100,
               ticks: { callback: value => `${value}%` }
             }
           }
         }
       });
     });
   </script>
   ```

3. **Responsive Design**
   - Mobile-first approach
   - Collapsible sections for smaller screens
   - Exportable reports (CSV/PDF)

### 9.6 Monitoring & Alerts

#### 9.4.1 Alert Conditions
```python
# monitoring/checks/email_health.py
def check_email_health():
    """Check for email delivery issues"""
    from datetime import timedelta
    from django.utils import timezone
    from ...models import EmailLog

    # Check for emails stuck in sending state
    threshold = timezone.now() - timedelta(hours=1)
    stuck_emails = EmailLog.objects.filter(
        status='sending',
        created_at__lt=threshold,
        is_processed=False
    )

    if stuck_emails.exists():
        send_alert(
            'high',
            f'{stuck_emails.count()} emails stuck in sending state',
            'Check Celery workers and SMTP configuration'
        )

    # Check for high bounce rate
    bounce_threshold = 5  # 5% bounce rate
    last_hour = timezone.now() - timedelta(hours=1)

    sent_count = EmailLog.objects.filter(created_at__gte=last_hour).count()
    bounced_count = EmailLog.objects.filter(
        created_at__gte=last_hour,
        status='bounced'
    ).count()

    if sent_count > 0:
        bounce_rate = (bounced_count / sent_count) * 100
        if bounce_rate > bounce_threshold:
            send_alert(
                'critical',
                f'High bounce rate: {bounce_rate:.1f}% in the last hour',
                'Check SMTP configuration and recipient email addresses'
            )
```

#### 9.4.2 Dashboard Metrics
```python
# v1/views/analytics.py
class EmailAnalyticsView(APIView):
    """API for email analytics and reporting"""

    def get(self, request, *args, **kwargs):
        store = getattr(request, 'store', None)
        days = int(request.query_params.get('days', 30))

        # Date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Base queryset
        logs = EmailLog.objects.filter(
            created_at__range=(start_date, end_date)
        )

        if store:
            logs = logs.filter(store=store)

        # Calculate metrics
        metrics = {
            'sent': logs.count(),
            'delivered': logs.filter(status='delivered').count(),
            'opened': logs.filter(tracking_events__event_type='opened')
                       .distinct().count(),
            'clicked': logs.filter(tracking_events__event_type='clicked')
                         .distinct().count(),
            'bounced': logs.filter(status='bounced').count(),
            'unsubscribed': logs.filter(tracking_events__event_type='unsubscribed')
                             .distinct().count(),
        }

        # Calculate rates
        metrics.update({
            'delivery_rate': self._safe_divide(metrics['delivered'], metrics['sent']) * 100,
            'open_rate': self._safe_divide(metrics['opened'], metrics['delivered']) * 100,
            'click_through_rate': self._safe_divide(metrics['clicked'], metrics['opened']) * 100,
            'bounce_rate': self._safe_divide(metrics['bounced'], metrics['sent']) * 100,
            'unsubscribe_rate': self._safe_divide(metrics['unsubscribed'], metrics['delivered']) * 100,
        })

        # Time series data
        time_series = self._get_time_series_data(logs, start_date, end_date)

        return Response({
            'metrics': metrics,
            'time_series': time_series,
            'period': {
                'start': start_date,
                'end': end_date
            }
        })

    def _safe_divide(self, numerator, denominator):
        """Safely divide two numbers, return 0 if denominator is 0"""
        return numerator / denominator if denominator else 0

    def _get_time_series_data(self, queryset, start_date, end_date):
        """Generate time series data for the given date range"""
        from django.db.models import Count, Q
        from django.db.models.functions import TruncDate

        # Group by date
        date_series = queryset.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            sent=Count('id'),
            delivered=Count('id', filter=Q(status='delivered')),
            opened=Count('tracking_events',
                       filter=Q(tracking_events__event_type='opened'),
                       distinct=True),
            clicked=Count('tracking_events',
                        filter=Q(tracking_events__event_type='clicked'),
                        distinct=True),
            bounced=Count('id', filter=Q(status='bounced')),
            unsubscribed=Count('tracking_events',
                             filter=Q(tracking_events__event_type='unsubscribed'),
                             distinct=True)
        ).order_by('date')

        # Convert to dict for easier lookup
        date_map = {item['date']: item for item in date_series}

        # Generate full date range
        result = []
        current_date = start_date.date()
        end_date = end_date.date()

        while current_date <= end_date:
            data = date_map.get(current_date, {
                'date': current_date,
                'sent': 0,
                'delivered': 0,
                'opened': 0,
                'clicked': 0,
                'bounced': 0,
                'unsubscribed': 0
            })

            # Calculate rates
            data.update({
                'delivery_rate': self._safe_divide(data['delivered'], data['sent']) * 100,
                'open_rate': self._safe_divide(data['opened'], data['delivered']) * 100,
                'click_through_rate': self._safe_divide(data['clicked'], data['opened']) * 100,
                'bounce_rate': self._safe_divide(data['bounced'], data['sent']) * 100,
                'unsubscribe_rate': self._safe_divide(data['unsubscribed'], data['delivered']) * 100,
            })

            result.append(data)
            current_date += timedelta(days=1)

        return result

### 9.1 Important Metrics
- Email delivery success/failure rates
- Average send time
- Queue size and processing time
- SMTP provider performance

### 9.2 Example Alerts
```python
# monitoring/checks/email_health.py
def check_email_queues():
    """Check for stuck email queues"""
    from datetime import timedelta
    from django.utils import timezone
    from ..models import EmailQueue

    # Check for emails stuck in queue for too long
    threshold = timezone.now() - timedelta(hours=1)
    stuck_emails = EmailQueue.objects.filter(
        is_processed=False,
        created_at__lt=threshold
    ).count()

    if stuck_emails > 10:
        send_alert(
            'high',
            f'{stuck_emails} emails stuck in queue',
            'Check Celery workers and SMTP configuration'
        )
```

## Review this final polished SMTP rules file carefully before applying.

<!-- ===============================================================================
 END SMTP.MD
 ================================================================================= -->


<!-- ===============================================================================
 START STORE-BOOTSTRAP.MD
 ================================================================================= -->
# Store Bootstrap Lifecycle Rules v1.0

## 🎯 Purpose

This document defines the complete store bootstrap lifecycle for CMS-Updated backend, ensuring all stores are properly initialized with required content types, roles, settings, and permissions upon creation.

## 📚 Related Documents
- [Core Architecture](../core.md)
- [Store Management](../stores.md)
- [Authentication & Permissions](../authentication.md)

---

## 🏗️ Store Bootstrap Overview

### **Bootstrap Phases**
When a new store is created, the following phases **must** be executed in order:

1. **Phase 1: Core Store Creation** - Basic store record
2. **Phase 2: Content Type Initialization** - Required post types
3. **Phase 3: Role and Permission Setup** - Default roles and permissions
4. **Phase 4: Default Configuration** - Store settings and preferences
5. **Phase 5: Theme Initialization** - Default theme setup
6. **Phase 6: Search Index Creation** - Search infrastructure
7. **Phase 7: Cache Warming** - Initial cache population
8. **Phase 8: Notification Setup** - Default notification preferences

## � Authentication & Permissions
- **Required Permission**: `stores.add_store` to create a new store
- **Bootstrap Execution**: Runs with the permissions of the user who created the store

---

## 📋 Phase 1: Core Store Creation

### **Bootstrap Fields to Add to Store Model**
Add these fields to your existing `Store` model in `apps/stores/models.py`:

```python
# Bootstrap tracking fields
bootstrap_completed = models.BooleanField(
    default=False,
    help_text="Indicates if bootstrap process has completed successfully"
)
bootstrap_phase = models.CharField(
    max_length=50,
    blank=True,
    help_text="Current phase of the bootstrap process"
)
bootstrap_error = models.TextField(
    blank=True,
    help_text="Any errors that occurred during bootstrap"
)
```

### **Bootstrap Lifecycle Hook**
Add this to your `Store` model's `save()` method:

```python
def save(self, *args, **kwargs):
    is_new = self.pk is None
    super().save(*args, **kwargs)

    if is_new:
        # Import here to avoid circular imports
        from .services import StoreBootstrapService
        StoreBootstrapService.bootstrap_store(self)
```

### **Store Model Integration**
Your existing `Store` model should already have these core fields:
- `name`
- `slug` (unique)
- `status` (with appropriate choices)
- `owner` (ForeignKey to User)
- `created_at`
- `updated_at`
```

---

## 🛠️ Phase 2: Content Type Initialization

### **Required Post Types**
All stores **must** have the following non-deletable post types:

1. **Page** - Static pages (About, Contact, etc.)
2. **Blog** - Blog posts
3. **Product** - Product catalog (if ecommerce enabled)

### **Bootstrap Implementation**
```python
# apps/stores/services.py
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class StoreBootstrapService:
    """Store bootstrap service"""

    @staticmethod
    @transaction.atomic
    def bootstrap_store(store):
        """
        Bootstrap a new store with all required components
        """
        try:
            logger.info(f"Starting bootstrap for store: {store.slug}")

            # Phase 1: Core store creation (already done)
            StoreBootstrapService._phase1_complete(store)

            # Phase 2: Content type initialization

            # Mark as complete
            store.bootstrap_completed = True
            store.bootstrap_phase = 'completed'
            store.save(update_fields=['bootstrap_completed', 'bootstrap_phase'])

        except Exception as e:
            store.bootstrap_error = str(e)
            store.save(update_fields=['bootstrap_error'])
            logger.error(f"Bootstrap failed for store {store.slug}: {e}")
            raise

    @staticmethod
    def _bootstrap_phase_2(store, actor):
        """
        Initialize content types and default pages

        Args:
            store: The Store instance
            actor: The User who initiated the bootstrap
        """
        logger.info(f"Starting phase 2 for store: {store.slug}")

        # Create required post types
        post_types = [
            {
                'name': 'Page',
                'slug': 'page',
                'description': 'Static pages for the store',
                'is_system': True,
                'is_deletable': False
            },
            {
                'name': 'Blog',
                'slug': 'blog',
                'description': 'Blog posts for the store',
                'is_system': True,
                'is_deletable': False
            },
            {
                'name': 'Product',
                'slug': 'product',
                'description': 'Product catalog',
                'is_system': True,
                'is_deletable': False
            }
        ]

        for post_type_data in post_types:
            PostType.objects.get_or_create(
                store=store,
                slug=post_type_data['slug'],
                defaults={
                    'name': post_type_data['name'],
                    'description': post_type_data['description'],
                    'is_system': post_type_data['is_system'],
                    'is_deletable': post_type_data['is_deletable'],
                    'created_by': actor  # Use the actor as creator
                }
            )

        # Create default pages
        StoreBootstrapService._create_default_pages(store)

        store.bootstrap_phase = 'phase2_complete'
        store.save(update_fields=['bootstrap_phase'])
        logger.info(f"Phase 2 complete for store: {store.slug}")

    @staticmethod
    def _bootstrap_phase_3(store, actor):
        """
        Initialize roles and permissions

        Args:
            store: The Store instance
            actor: The User who will be assigned as store owner
        """
        logger.info(f"Starting phase 3 for store: {store.slug}")

        # Create default roles
        roles = [
            {
                'name': 'Owner',
                'slug': 'owner',
                'description': 'Full access to all store features',
                'is_system': True,
                'permissions': ['*']
            },
            {
                'name': 'Admin',
                'slug': 'admin',
                'description': 'Administrative access to store',
                'is_system': True,
                'permissions': ['content.*', 'ecommerce.*', 'settings.*']
            },
            {
                'name': 'Manager',
                'slug': 'manager',
                'description': 'Manager access to store',
                'is_system': True,
                'permissions': ['content.read', 'content.write', 'ecommerce.read', 'ecommerce.write']
            },
            {
                'name': 'Staff',
                'slug': 'staff',
                'description': 'Staff access to store',
                'is_system': True,
                'permissions': ['content.read', 'ecommerce.read']
            },
            {
                'name': 'Viewer',
                'slug': 'viewer',
                'description': 'Read-only access to store',
                'is_system': True,
                'permissions': ['content.read']
            }
        ]

        owner_role = None

        for role_data in roles:
            role, created = Role.objects.get_or_create(
                store=store,
                slug=role_data['slug'],
                defaults={
                    'name': role_data['name'],
                    'description': role_data['description'],
                    'is_system': role_data['is_system'],
                    'created_by': actor  # Track who created the role
                }
            )

            if created and role_data.get('permissions'):
                role.permissions.set(role_data['permissions'])

            if role.slug == 'owner':
                owner_role = role

        # Assign owner role to the actor
        if owner_role:
            StoreMember.objects.get_or_create(
                store=store,
                user=actor,
                defaults={
                    'role': owner_role,
                    'is_active': True
                }
            )
        StoreMember.objects.get_or_create(
            store=store,
            user=store.owner,
            defaults={'role': owner_role}
        )

        store.bootstrap_phase = 'phase3_complete'
        store.save(update_fields=['bootstrap_phase'])
        logger.info(f"Phase 3 complete for store: {store.slug}")

    @staticmethod
    def _create_role_permissions(store, role):
        """Create permissions for a role"""
        from apps.accounts.models import Permission

        # Define permission sets based on role
        permission_sets = {
            'owner': ['*'],  # All permissions
            'admin': ['content.*', 'ecommerce.*', 'settings.*'],
            'manager': ['content.read', 'content.write', 'ecommerce.read', 'ecommerce.write'],
            'staff': ['content.read', 'ecommerce.read'],
            'viewer': ['content.read']
        }

        permissions = permission_sets.get(role.slug, [])

        for perm in permissions:
            Permission.objects.get_or_create(
                store=store,
                code=perm,
                defaults={'description': f'{perm} permission'}
            )

            role.permissions.add(Permission.objects.get(store=store, code=perm))

    @staticmethod
    def _phase4_configuration(store):
        """Phase 4: Default configuration"""
        from apps.metafields.services import MetaFieldService

        # Set default store configuration
        default_config = {
            'currency': 'USD',
            'timezone': 'UTC',
            'language': 'en_US',
            'date_format': 'MM/DD/YYYY',
            'time_format': 'HH:mm',
            'tax_rate': '0.00',
            'shipping_free_threshold': '0'
        }

        for key, value in default_config.items():
            MetaFieldService.set_metafield_value(
                store,
                key,
                value,
                namespace='config'
            )

        store.bootstrap_phase = 'phase4_complete'
        store.save(update_fields=['bootstrap_phase'])
        logger.info(f"Phase 4 complete for store: {store.slug}")

    @staticmethod
    def _phase5_theme(store):
        """Phase 5: Theme initialization"""
        from apps.themes.models import Theme, ColorScheme, Typography

        # Create default theme
        theme, created = Theme.objects.get_or_create(
            store=store,
            name='Default Theme',
            defaults={'is_active': True}
        )

        if created:
            # Create default color scheme
            ColorScheme.objects.create(
                store=store,
                theme=theme,
                name='Light',
                colors={
                    'primary': '#0066cc',
                    'secondary': '#666666',
                    'background': '#ffffff',
                    'text': '#333333',
                    'accent': '#ff6600'
                },
                is_default=True
            )

            # Create default typography
            Typography.objects.create(
                store=store,
                theme=theme,
                base_font_size=16,
                font_smoothing=True,
                font_families={
                    'primary': 'Arial, sans-serif',
                    'heading': 'Georgia, serif'
                }
            )

        store.bootstrap_phase = 'phase5_complete'
        store.save(update_fields=['bootstrap_phase'])
        logger.info(f"Phase 5 complete for store: {store.slug}")

    @staticmethod
    def _phase6_search_index(store):
        """Phase 6: Search index creation"""
        from apps.search.models import SearchIndex

        # Create search index for store
        SearchIndex.objects.get_or_create(
            store=store,
            name='Default Search Index',
            defaults={
                'index_name': f'{store.slug}_search',
                'content_types': ['Page', 'Post', 'Product'],
                'fields': {
                    'title': 'text',
                    'content': 'text',
                    'description': 'text'
                },
                'facets': [
                    {'field': 'type', 'label': 'Type'},
                    {'field': 'category_id', 'label': 'Category'}
                ],
                'is_active': True
            }
        )

        # Warm search index
        from apps.search.services import SearchService
        SearchService.rebuild_index(store)

        store.bootstrap_phase = 'phase6_complete'
        store.save(update_fields=['bootstrap_phase'])
        logger.info(f"Phase 6 complete for store: {store.slug}")

    @staticmethod
    def _phase7_cache_warming(store):
        """Phase 7: Cache warming"""
        from apps.cache.services import CacheWarmupService

        # Warm cache for store
        CacheWarmupService.warm_store_cache(store)

        store.bootstrap_phase = 'phase7_complete'
        store.save(update_fields=['bootstrap_phase'])
        logger.info(f"Phase 7 complete for store: {store.slug}")

    @staticmethod
    def _phase8_notifications(store):
        """Phase 8: Notification setup"""
        from apps.notifications.models import NotificationPreference, NotificationTemplate

        # Create default notification templates
        templates = [
            {
                'notification_type': 'order.created',
                'title_template': 'Order Created',
                'message_template': 'Your order {{order_number}} has been created',
                'email_subject_template': 'Order Confirmation - {{order_number}}',
                'email_body_template': 'Thank you for your order!'
            },
            {
                'notification_type': 'user.registered',
                'title_template': 'Welcome to {{store_name}}',
                'message_template': 'Welcome to our store!',
                'email_subject_template': 'Welcome to {{store_name}}',
                'email_body_template': 'Thank you for registering!'
            }
        ]

        for template_data in templates:
            NotificationTemplate.objects.get_or_create(
                store=store,
                notification_type=template_data['notification_type'],
                defaults=template_data
            )

        # Create default notification preferences for owner
        notification_types = [
            'order.created', 'order.shipped', 'order.delivered',
            'user.registered', 'form.submitted', 'system.alert'
        ]

        for notification_type in notification_types:
            NotificationPreference.objects.get_or_create(
                store=store,
                user=store.owner,
                notification_type=notification_type,
                defaults={
                    'channel_preferences': {'email': True, 'in_app': True},
                    'digest_enabled': False
                }
            )

        store.bootstrap_phase = 'phase8_complete'
        store.save(update_fields=['bootstrap_phase'])
        logger.info(f"Phase 8 complete for store: {store.slug}")
```

---

## 🔄 Bootstrap Retries

### **Retry Logic**
If bootstrap fails at any phase, the system should:

1. **Log the error** - Store error in `bootstrap_error` field
2. **Mark phase** - Set `bootstrap_phase` to the failed phase
3. **Allow retry** - Provide mechanism to retry bootstrap

### **Retry Implementation**
```python
# apps/stores/services.py (continued)

@staticmethod
def retry_bootstrap(store):
    """
    Retry bootstrap for a store
    """
    if store.bootstrap_completed:
        logger.warning(f"Store {store.slug} already bootstrapped")
        return False

    # Clear error
    store.bootstrap_error = ''
    store.save(update_fields=['bootstrap_error'])

    # Retry bootstrap
    StoreBootstrapService.bootstrap_store(store)

    return True
```

---

## 🔧 Management Commands

### **Bootstrap Store**
```bash
# Bootstrap a specific store
python manage.py bootstrap_store --slug=my-store

# Bootstrap all stores
python manage.py bootstrap_store --all

# Retry failed bootstrap
python manage.py bootstrap_store --retry
```

### **Bootstrap Status**
```bash
# Check bootstrap status
python manage.py bootstrap_status --slug=my-store

# List stores with failed bootstrap
python manage.py bootstrap_status --failed
```

---

## 🧪 Testing Rules

### **Required Coverage**
- **Bootstrap Service**: 100% code coverage
- **Integration**: Critical path testing
- **Error Handling**: Test failure scenarios

### **Test Examples**
```python
# apps/stores/tests/test_bootstrap.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from ..services import StoreBootstrapService
from ..models import Store

User = get_user_model()

class StoreBootstrapTest(TestCase):
    """
    Test the store bootstrap process

    Note: We create a test user here because tests run in isolation.
    In production, the user would come from the request.
    """
    def setUp(self):
        # Create a test user to simulate the actor
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password'
        )

        # Create a store owned by the test user
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store',
            owner=self.user
        )

    def test_complete_bootstrap_flow(self):
        """Test the complete bootstrap flow"""
        # Execute bootstrap
        StoreBootstrapService.bootstrap_store(store=self.store, actor=self.user)

        # Refresh store from DB
        self.store.refresh_from_db()

        # Verify bootstrap completed
        self.assertTrue(self.store.bootstrap_completed)
        self.assertEqual(self.store.bootstrap_phase, 'completed')

        # Verify post types were created
        from apps.posts.models import PostType
        self.assertTrue(PostType.objects.filter(store=self.store).exists())

        # Verify roles were created
        from apps.accounts.models import Role
        self.assertTrue(Role.objects.filter(store=self.store).exists())

        # Verify owner role was assigned to the actor
        from apps.accounts.models import StoreMember
        member = StoreMember.objects.get(store=self.store, user=self.user)
        self.assertEqual(member.role.slug, 'owner')

    def test_bootstrap_with_existing_owner(self):
        """Test bootstrap when owner already exists"""
        # First bootstrap
        StoreBootstrapService.bootstrap_store(store=self.store, actor=self.user)

        # Should not create duplicate owner
        from apps.accounts.models import StoreMember
        owners = StoreMember.objects.filter(
            store=self.store,
            role__slug='owner'
        )
        self.assertEqual(owners.count(), 1)

    def test_bootstrap_error_handling(self):
        """Test error handling during bootstrap"""
        # Force an error by making store name invalid
        self.store.name = ''
        self.store.save(update_fields=['name'])

        with self.assertRaises(ValueError):
            StoreBootstrapService.bootstrap_store(store=self.store, actor=self.user)

        # Verify error state was recorded
        self.store.refresh_from_db()
        self.assertIsNotNone(self.store.bootstrap_error)
        self.assertFalse(self.store.bootstrap_completed)

        # Retry bootstrap
        result = StoreBootstrapService.retry_bootstrap(store)

        self.assertTrue(result)
        self.assertTrue(store.bootstrap_completed)
```

---

## 📚 Bootstrap Best Practices

### **DO:**
1. **Use atomic transactions** - All-or-nothing bootstrap
2. **Log each phase** - Maintain audit trail
3. **Handle failures gracefully** - Allow retry mechanism
4. **Validate bootstrap completion** - Ensure all phases complete
5. **Create non-deletable items** - Protect system content
6. **Use sensible defaults** - Provide good out-of-box experience
7. **Warm cache on bootstrap** - Improve initial performance
8. **Set up notifications** - Enable communication
9. **Create search indexes** - Enable search functionality
10. **Test bootstrap thoroughly** - Ensure reliability

### **DON'T:**
1. **Don't skip phases** - Execute all phases in order
2. **Don't ignore errors** - Handle all exceptions
3. **Don't allow partial bootstrap** - Complete or fail
4. **Don't create deletable system items** - Protect core content
5. **Don't forget to warm cache** - Improve performance
6. **Don't skip notifications** - Enable communication
7. **Don't assume success** - Verify each phase
8. **Don't use blocking operations** - Keep bootstrap fast
9. **Don't create circular dependencies** - Keep phases independent
10. **Don't forget to test** - Ensure reliability

---

## 📊 Bootstrap Monitoring

### **Metrics to Track**
- **Bootstrap Success Rate**: Percentage of successful bootstraps
- **Bootstrap Duration**: Average time to complete bootstrap
- **Failed Bootstraps**: Number of failed bootstraps
- **Phase Failures**: Which phases fail most often

### **Alerting**
- **Bootstrap Failures**: Alert on bootstrap failures
- **Long Bootstrap Times**: Alert if bootstrap > 5 minutes
- **Failed Phase Alerts**: Alert on specific phase failures

---

## 🎯 Implementation Checklist

- [ ] Create Store model with bootstrap fields
- [ ] Implement StoreBootstrapService
- [ ] Define all 8 bootstrap phases
- [ ] Create default post types (Page, Blog, Product)
- [ ] Create default pages (Home, About, Contact)
- [ ] Create default roles (Owner, Admin, Manager, Staff, Viewer)
- [ ] Create default permissions
- [ ] Set default store configuration
- [ ] Create default theme
- [ ] Set up search index
- [ ] Warm cache
- [ ] Set up notifications
- [ ] Implement retry logic
- [ ] Create management commands
- [ ] Add monitoring and logging
- [ ] Create tests (bootstrap service, integration)

---

## 📖 Version History

- **v1.0** - Initial version with complete bootstrap lifecycle

<!-- ===============================================================================
 END STORE-BOOTSTRAP.MD
 ================================================================================= -->


<!-- ===============================================================================
 START STORES.MD
 ================================================================================= -->
# Stores App Rules - DFCMS Compatible

Follow core.md and accounts.md strictly.
All models must use explicit store ForeignKey. Owner references accounts.models.User.
Use standard ViewSet with store filtering.

## 1. Directory Structure (V2-Only Clean Implementation)
```
apps/
├── stores/
│   ├── v2/                    # Version 2 (Current Only)
│   │   ├── __init__.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── services.py
│   │   └── tests.py
│   ├── models/                 # Shared models across versions
│   │   ├── __init__.py
│   │   ├── store.py
│   │   ├── settings.py
│   │   └── theme.py
│   ├── admin.py
│   ├── apps.py
│   ├── middleware.py
│   ├── signals.py
│   ├── tasks.py
│   ├── management/
│   │   └── commands/
│   │       └── migrate_stores.py
│   ├── migrations/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_views.py
│   └── api.md                  # API documentation (REQUIRED)
```

## 2. Core Models

### 2.1 Store Model
```python
# apps/stores/models/store.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import secrets

User = get_user_model()

class Store(models.Model):
    """Store model following DFCMS patterns with explicit store scoping"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]

    TYPE_CHOICES = [
        ('ecommerce', 'E-commerce'),
        ('blog', 'Blog'),
        ('portfolio', 'Portfolio'),
        ('corporate', 'Corporate'),
        ('other', 'Other'),
    ]

    # Core fields (from DFCMS)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    # Ownership (DFCMS compatibility)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_stores'
    )

    # Access & Security (from DFCMS)
    access_code = models.CharField(max_length=6, unique=True, editable=False)
    verification_token = models.CharField(max_length=255, unique=True, blank=True, null=True)

    # Status & Type
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    store_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='ecommerce')

    # Enhanced Features
    domain = models.URLField(blank=True, null=True, unique=True)
    logo = models.ImageField(upload_to='stores/logos/', blank=True, null=True)
    favicon = models.ImageField(upload_to='stores/favicons/', blank=True, null=True)

    # Dynamic Settings (JSON field for configs)
    settings = models.JSONField(default=dict, blank=True)

    # SEO Fields
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)

    # Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True)
    facebook_pixel_id = models.CharField(max_length=50, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_accessed = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'stores_store'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['owner']),
            models.Index(fields=['domain']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.name)

        # Generate access code and verification token for new stores
        if not self.pk:
            self.access_code = self._generate_access_code()
            self.verification_token = secrets.token_urlsafe(32)

        super().save(*args, **kwargs)

    def _generate_access_code(self):
        """Generate unique 6-digit access code"""
        while True:
            code = ''.join(secrets.choice('0123456789') for _ in range(6))
            if not Store.objects.filter(access_code=code).exists():
                return code
```

### 2.2 StoreSettings Model
```python
class StoreSettings(models.Model):
    """Store-specific settings with explicit store relationship"""

    store = models.OneToOneField(
        'Store',
        on_delete=models.CASCADE,
        related_name='store_settings'
    )

    # General Settings
    site_name = models.CharField(max_length=255, default='My Store')
    site_description = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    # Currency & Locale
    currency = models.CharField(max_length=3, default='USD')
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')

    # E-commerce Settings
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    shipping_enabled = models.BooleanField(default=True)
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Media References
    logo = models.ForeignKey(
        'media.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='store_logos',
        help_text="Store logo image"
    )
    favicon = models.ForeignKey(
        'media.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='store_favicons',
        help_text="Store favicon image"
    )

    # Advanced Settings (JSON for flexibility)
    custom_settings = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stores_settings'

    def __str__(self):
        return f"{self.store.name} Settings"
```

## 3. Service Layer

### 3.1 Store Service
```python
# apps/stores/services.py
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.stores.models import Store, StoreSettings
from apps.logs.tasks import log_event_async

class StoreService:
    """Store business logic following DFCMS patterns"""

    @staticmethod
    @transaction.atomic
    def create_store(owner, store_data):
        """Create new store with settings and theme"""
        try:
            # Create store
            store = Store.objects.create(
                owner=owner,
                name=store_data['name'],
                slug=store_data.get('slug', ''),
                description=store_data.get('description', ''),
                store_type=store_data.get('store_type', 'ecommerce')
            )

            # Create default settings
            StoreSettings.objects.create(
                store=store,
                site_name=store.name,
                contact_email=owner.email
            )

            # Log store creation
            log_event_async.delay({
                'event_type': 'CONTENT_CREATE',
                'message': f"Store created: {store.name}",
                'user': owner,
                'store': store,
                'entity_type': 'Store',
                'entity_id': store.id,
                'metadata': {'store_data': store_data}
            })

            return store

        except Exception as e:
            log_event_async.delay({
                'event_type': 'SYSTEM_ERROR',
                'message': f"Failed to create store: {str(e)}",
                'user': owner,
                'level': 'ERROR',
                'metadata': {'error': str(e), 'store_data': store_data}
            })
            raise

    @staticmethod
    def update_store(store, update_data, user=None):
        """Update store with logging"""
        try:
            old_data = {
                'name': store.name,
                'status': store.status,
                'description': store.description
            }

            for field, value in update_data.items():
                if hasattr(store, field):
                    setattr(store, field, value)

            store.save()

            # Log update
            log_event_async.delay({
                'event_type': 'CONTENT_UPDATE',
                'message': f"Store updated: {store.name}",
                'user': user,
                'store': store,
                'entity_type': 'Store',
                'entity_id': store.id,
                'metadata': {
                    'old_data': old_data,
                    'new_data': update_data
                }
            })

            return store

        except Exception as e:
            log_event_async.delay({
                'event_type': 'SYSTEM_ERROR',
                'message': f"Failed to update store: {str(e)}",
                'user': user,
                'store': store,
                'level': 'ERROR',
                'metadata': {'error': str(e), 'update_data': update_data}
            })
            raise

    @staticmethod
    def verify_store(store, token):
        """Verify store email"""
        if store.verification_token == token:
            store.status = 'active'
            store.verification_token = None
            store.save()

            log_event_async.delay({
                'event_type': 'CONTENT_UPDATE',
                'message': f"Store verified: {store.name}",
                'store': store,
                'entity_type': 'Store',
                'entity_id': store.id,
                'metadata': {'verification': True}
            })

            return True
        return False

    @staticmethod
    def get_store_analytics(store, days=30):
        """Get store analytics data from logs"""
        from datetime import timedelta
        from django.utils import timezone
        from apps.logs.models import LogEntry

        since = timezone.now() - timedelta(days=days)

        # Get analytics from logs app
        page_views = LogEntry.objects.filter(
            store=store,
            event_type='PAGE_VIEW',
            created_at__gte=since
        ).count()

        unique_visitors = LogEntry.objects.filter(
            store=store,
            event_type='PAGE_VIEW',
            created_at__gte=since
        ).values('session_id').distinct().count()

        security_events = LogEntry.objects.filter(
            store=store,
            is_suspicious=True,
            created_at__gte=since
        ).count()

        return {
            'page_views': page_views,
            'unique_visitors': unique_visitors,
            'security_events': security_events,
            'period_days': days,
        }
```

## 4. API Views (V2 Only)

### 4.1 Public Store Views
```python
# apps/stores/v2/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from core.viewsets import BaseViewSet
from ..serializers import StorePublicSerializer
from ..services import StoreService

class StorePublicViewSet(BaseViewSet):
    """Public store API - no authentication required"""

    permission_classes = [AllowAny]
    queryset = Store.objects.filter(status='active')
    serializer_class = StorePublicSerializer

    def get_queryset(self):
        """Filter by domain or subdomain"""
        queryset = super().get_queryset()

        # Filter by domain if provided
        domain = self.request.GET.get('domain')
        if domain:
            queryset = queryset.filter(domain=domain)

        return queryset

    @extend_schema(
        summary="Get store by slug",
        description="Get public store details by slug",
        tags=["Stores Public"]
    )
    def retrieve(self, request, *args, **kwargs):
        """Get store details"""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="List active stores",
        description="List all active stores",
        tags=["Stores Public"]
    )
    def list(self, request, *args, **kwargs):
        """List stores"""
        return super().list(request, *args, **kwargs)
```

### 4.2 Dashboard Store Views
```python
# apps/stores/v2/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from core.viewsets import StoreScopedViewSet
from core.permissions import IsStoreOwner
from ..serializers import StoreSerializer, StoreCreateSerializer
from ..services import StoreService

class StoreViewSet(StoreScopedViewSet):
    """Store management API for dashboard"""

    permission_classes = [IsAuthenticated, IsStoreOwner]
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    def get_queryset(self):
        """Filter by current user's stores"""
        return super().get_queryset().filter(owner=self.request.user)

    @extend_schema(
        summary="Create store",
        description="Create new store",
        request=StoreCreateSerializer,
        responses={201: StoreSerializer},
        tags=["Stores Dashboard"]
    )
    def create(self, request, *args, **kwargs):
        """Create new store"""
        serializer = StoreCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        store = StoreService.create_store(
            owner=request.user,
            store_data=serializer.validated_data
        )

        return Response(
            StoreSerializer(store).data,
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        summary="Update store",
        description="Update store details",
        tags=["Stores Dashboard"]
    )
    def update(self, request, *args, **kwargs):
        """Update store"""
        store = self.get_object()
        updated_store = StoreService.update_store(
            store=store,
            update_data=request.data,
            user=request.user
        )

        return Response(StoreSerializer(updated_store).data)

    @extend_schema(
        summary="Store analytics",
        description="Get store analytics data",
        tags=["Stores Dashboard"]
    )
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get store analytics"""
        store = self.get_object()
        days = int(request.GET.get('days', 30))

        analytics = StoreService.get_store_analytics(store, days)
        return Response(analytics)
```

## 5. Serializers

### 5.1 Store Serializers
```python
# apps/stores/v2/serializers.py
from rest_framework import serializers
from core.serializers import BaseSerializer
from apps.stores.models import Store, StoreSettings, StoreTheme

class StorePublicSerializer(BaseSerializer):
    """Public store information"""

    class Meta:
        model = Store
        fields = [
            'id', 'name', 'slug', 'description', 'logo',
            'domain', 'meta_title', 'meta_description',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class StoreSerializer(BaseSerializer):
    """Full store information for owners"""
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    store_type_display = serializers.CharField(source='get_store_type_display', read_only=True)

    class Meta:
        model = Store
        fields = '__all__'
        read_only_fields = ['id', 'owner', 'access_code', 'created_at']

class StoreCreateSerializer(BaseSerializer):
    """Store creation serializer"""

    class Meta:
        model = Store
        fields = ['name', 'slug', 'description', 'store_type']

    def validate_slug(self, value):
        """Validate slug uniqueness"""
        if Store.objects.filter(slug=value).exists():
            raise serializers.ValidationError("Store with this slug already exists.")
        return value

class StoreSettingsSerializer(BaseSerializer):
    """Store settings serializer"""

    class Meta:
        model = StoreSettings
        fields = '__all__'

class StoreThemeSerializer(BaseSerializer):
    """Store theme serializer"""

    class Meta:
        model = StoreTheme
        fields = '__all__'
```

## 6. Migration & Legacy Rules

### 6.1 Migration Command
```python
# apps/stores/management/commands/migrate_stores.py
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.stores.models import Store

class Command(BaseCommand):
    help = 'Migrate old stores from DFCMS structure'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be migrated')
        parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for migration')

    def handle(self, *args, **options):
        from apps.activity_logs.models import ActivityLog  # Old DFCMS

        # Migrate stores logic here
        self.stdout.write(self.style.SUCCESS("Store migration completed"))
```

## 7. Signals for Logging

```python
# apps/stores/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Store, StoreSettings, StoreTheme
from apps.logs.tasks import log_event_async

@receiver(post_save, sender=Store)
def log_store_change(sender, instance, created, **kwargs):
    """Log store changes"""
    if created:
        event_type = 'CONTENT_CREATE'
        message = f"Store created: {instance.name}"
    else:
        event_type = 'CONTENT_UPDATE'
        message = f"Store updated: {instance.name}"

    log_event_async.delay({
        'event_type': event_type,
        'message': message,
        'store': instance,
        'entity_type': 'Store',
        'entity_id': instance.id,
        'metadata': {'created': created}
    })

@receiver(post_delete, sender=Store)
def log_store_deletion(sender, instance, **kwargs):
    """Log store deletion"""
    log_event_async.delay({
        'event_type': 'CONTENT_DELETE',
        'message': f"Store deleted: {instance.name}",
        'entity_type': 'Store',
        'entity_id': instance.id,
        'metadata': {'store_name': instance.name}
    })
```

## 8. What AI Can Do

### ✅ **Allowed Actions**
1. **Create Store Models**: Following exact model patterns with explicit store FK
2. **Implement Services**: Business logic in services.py with logging integration
3. **Create ViewSets**: V2-only ViewSets with StoreScopedViewSet base
4. **Add Serializers**: Both public and internal serializers with validation
5. **Configure URLs**: V2 URL patterns with nested routes
6. **Write Tests**: Model, service, and API tests with proper coverage
7. **Add Admin**: Django admin configuration for store management
8. **Implement Signals**: Auto-logging integration with logs app

### 🚫 **Forbidden Actions**
1. **No V1 References**: Only V2 implementation allowed
2. **No Business Logic in Views**: All logic must be in services
3. **No Hardcoded Values**: Use settings or configuration
4. **No Direct Database Queries**: Use service layer
5. **No Missing Store FK**: All models must have store relationship
6. **No Missing Logging**: All actions must be logged
7. **No TenantModel**: Use explicit store FK relationships
8. **No Nested Subfolders**: Models stay in apps/stores/models/
9. **No Missing API Documentation**: api.md file is REQUIRED
10. **No Missing Tests**: Minimum 80% coverage required

---

**Review suggested changes carefully before applying.**

<!-- ===============================================================================
 END STORES.MD
 ================================================================================= -->


<!-- ===============================================================================
 START THEMES.MD
 ================================================================================= -->
# Themes App Rules v1.0

## 🎯 Purpose

This document defines the development rules for the **themes** app in CMS-Updated backend, providing a simplified yet powerful theming system that supports multiple color schemes, typography settings, and custom styles while maintaining a clean architecture.

---

## 🏗️ Themes App Structure

### **Fixed Directory Structure**
```
apps/
└── themes/
    ├── v2/                     # Version 2 (Current Only)
    │   ├── serializers/       # API serializers
    │   ├── services/          # Business logic
    │   ├── templates/         # Default theme templates
    │   ├── templatetags/      # Template tags and filters
    │   ├── tests/             # Unit and integration tests
    │   ├── urls.py           # URL routing
    │   └── views/            # API views
    ├── models/                # Database models
    │   ├── __init__.py
    │   ├── theme.py
    │   ├── color_scheme.py
    │   ├── typography.py
    │   ├── style_class.py
    │   └── template.py
    ├── admin.py
    ├── apps.py
    └── migrations/
```

---

## 🧩 Core Models

### **1. Theme Model**
```python
class Theme(TenantModel):
    """
    Main theme model for each store.
    Each store can have multiple themes, but only one active theme.
    """
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="Default Theme")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_active', 'name']
        unique_together = [['store', 'name']]
```

### **2. Color Scheme**
```python
class ColorScheme(models.Model):
    """
    Color scheme with light/dark mode support.
    Each theme can have multiple color schemes.
    """
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='color_schemes')
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    key = models.SlugField(max_length=100)
    is_default = models.BooleanField(default=False)

    # Light mode colors
    colors = models.JSONField(default=dict, help_text="Light mode colors", blank=True)

    # Dark mode colors (optional)
    dark_colors = models.JSONField(default=dict, blank=True, help_text="Dark mode colors")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['theme', 'key']]
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.colors:
            self.colors = self.get_default_colors('light')
        if not self.dark_colors:
            self.dark_colors = self.get_default_colors('dark')
        super().save(*args, **kwargs)

    @staticmethod
    def get_default_colors(mode='light'):
        """Return default color scheme based on mode (light/dark)"""
        base = {
            'background': '#ffffff' if mode == 'light' else '#111827',
            'foreground': '#111827' if mode == 'light' else '#f3f4f6',
            'muted': '#6b7280' if mode == 'light' else '#9ca3af',
            'muted_foreground': '#374151' if mode == 'light' else '#d1d5db',

            # Primary colors
            'primary': '#3b82f6',
            'primary_foreground': '#ffffff',
            'primary_hover': '#2563eb',

            # Secondary colors
            'secondary': '#f3f4f6' if mode == 'light' else '#1f2937',
            'secondary_foreground': '#111827' if mode == 'light' else '#f9fafb',
            'secondary_hover': '#e5e7eb' if mode == 'light' else '#374151',

            # Accent colors
            'accent': '#f59e0b',
            'accent_foreground': '#ffffff',
            'accent_hover': '#d97706',

            # Destructive colors
            'destructive': '#ef4444',
            'destructive_foreground': '#ffffff',
            'destructive_hover': '#dc2626',

            # Success colors
            'success': '#10b981',
            'success_foreground': '#ffffff',
            'success_hover': '#059669',

            # Warning colors
            'warning': '#f59e0b',
            'warning_foreground': '#ffffff',
            'warning_hover': '#d97706',

            # Info colors
            'info': '#3b82f6',
            'info_foreground': '#ffffff',
            'info_hover': '#2563eb',

            # Border colors
            'border': '#e5e7eb' if mode == 'light' else '#374151',
            'input': '#d1d5db' if mode == 'light' else '#4b5563',
            'ring': '#93c5fd',

            # Card colors
            'card': '#ffffff' if mode == 'light' else '#1f2937',
            'card_foreground': '#111827' if mode == 'light' else '#f9fafb',

            # Popover colors
            'popover': '#ffffff' if mode == 'light' else '#1f2937',
            'popover_foreground': '#111827' if mode == 'light' else '#f9fafb',

            # Tooltip colors
            'tooltip': '#111827' if mode == 'light' else '#f3f4f6',
            'tooltip_foreground': '#f9fafb' if mode == 'light' else '#111827',

            # Overlay colors
            'overlay': 'rgba(0, 0, 0, 0.5)',

            # Shadow colors
            'shadow': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',

            # Button variants
            'button_primary': {
                'background': '#3b82f6',
                'foreground': '#ffffff',
                'hover': '#2563eb',
                'border': '#3b82f6',
            },
            'button_secondary': {
                'background': '#f3f4f6' if mode == 'light' else '#374151',
                'foreground': '#111827' if mode == 'light' else '#f9fafb',
                'hover': '#e5e7eb' if mode == 'light' else '#4b5563',
                'border': '#e5e7eb' if mode == 'light' else '#4b5563',
            },
            'button_outline': {
                'background': 'transparent',
                'foreground': '#3b82f6',
                'hover': '#f3f4f6' if mode == 'light' else '#1f2937',
                'border': '#d1d5db',
            },
            'button_ghost': {
                'background': 'transparent',
                'foreground': '#3b82f6',
                'hover': '#f3f4f6' if mode == 'light' else '#1f2937',
                'border': 'transparent',
            },
            'button_link': {
                'background': 'transparent',
                'foreground': '#3b82f6',
                'hover': 'transparent',
                'border': 'transparent',
                'underline': True,
            },

            # Form elements
            'input_background': '#ffffff' if mode == 'light' else '#1f2937',
            'input_foreground': '#111827' if mode == 'light' else '#f9fafb',
            'input_placeholder': '#9ca3af',
            'input_border': '#d1d5db',
            'input_ring': '#93c5fd',

            # Checkbox/radio
            'checkbox_background': '#ffffff' if mode == 'light' else '#1f2937',
            'checkbox_foreground': '#3b82f6',
            'checkbox_border': '#d1d5db',

            # Toggle
            'toggle_background': '#e5e7eb' if mode == 'light' else '#374151',
            'toggle_foreground': '#3b82f6',

            # Badge variants
            'badge_primary': {
                'background': '#dbeafe',
                'foreground': '#1e40af',
            },
            'badge_secondary': {
                'background': '#e5e7eb' if mode == 'light' else '#374151',
                'foreground': '#111827' if mode == 'light' else '#f9fafb',
            },
            'badge_destructive': {
                'background': '#fee2e2',
                'foreground': '#b91c1c',
            },
            'badge_outline': {
                'background': 'transparent',
                'foreground': '#111827' if mode == 'light' else '#f9fafb',
                'border': '#e5e7eb' if mode == 'light' else '#374151',
            },
        }

        return base
```

### **3. Typography**
```python
class Typography(models.Model):
    """
    Typography settings for themes with comprehensive controls.
    Supports responsive typography and font loading.
    """
    theme = models.OneToOneField(Theme, on_delete=models.CASCADE, related_name='typography')
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)

    # Base font settings
    base_font_size = models.PositiveSmallIntegerField(
        default=16,
        help_text="Base font size in pixels (16px is recommended)"
    )
    font_smoothing = models.CharField(
        max_length=50,
        default='antialiased',
        choices=[
            ('antialiased', 'Smooth (antialiased)'),
            ('subpixel-antialiased', 'Crisp (subpixel)'),
            ('auto', 'System Default')
        ]
    )

    # Font families
    font_primary = models.CharField(
        max_length=255,
        default="Inter, system-ui, -apple-system, sans-serif",
        help_text="Primary font family (used for headings and UI)"
    )
    font_secondary = models.CharField(
        max_length=255,
        default="Inter, system-ui, -apple-system, sans-serif",
        help_text="Secondary font family (used for body text)"
    )
    font_accent = models.CharField(
        max_length=255,
        default="'Inter Variable', sans-serif",
        help_text="Accent font family (used for special elements)"
    )
    font_mono = models.CharField(
        max_length=255,
        default="'JetBrains Mono', 'Fira Code', monospace",
        help_text="Monospace font family"
    )

    # Font weights
    font_weight_light = models.PositiveIntegerField(default=300)
    font_weight_normal = models.PositiveIntegerField(default=400)
    font_weight_medium = models.PositiveIntegerField(default=500)
    font_weight_semibold = models.PositiveIntegerField(default=600)
    font_weight_bold = models.PositiveIntegerField(default=700)

    # Line heights
    line_height_none = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    line_height_tight = models.DecimalField(max_digits=3, decimal_places=2, default=1.25)
    line_height_snug = models.DecimalField(max_digits=3, decimal_places=2, default=1.375)
    line_height_normal = models.DecimalField(max_digits=3, decimal_places=2, default=1.5)
    line_height_relaxed = models.DecimalField(max_digits=3, decimal_places=2, default=1.625)
    line_height_loose = models.DecimalField(max_digits=3, decimal_places=2, default=2.0)

    # Letter spacing
    letter_spacing_tighter = models.DecimalField(max_digits=4, decimal_places=3, default=-0.05)
    letter_spacing_tight = models.DecimalField(max_digits=4, decimal_places=3, default=-0.025)
    letter_spacing_normal = models.DecimalField(max_digits=4, decimal_places=3, default=0)
    letter_spacing_wide = models.DecimalField(max_digits=4, decimal_places=3, default=0.025)
    letter_spacing_wider = models.DecimalField(max_digits=4, decimal_places=3, default=0.05)
    letter_spacing_widest = models.DecimalField(max_digits=4, decimal_places=3, default=0.1)

    # Headings configuration
    headings = models.JSONField(
        default=dict,
        help_text="Advanced heading configurations (h1-h6)"
    )

    # Paragraph styles
    paragraph_margin = models.JSONField(
        default=dict,
        help_text="Margin settings for paragraphs"
    )

    # Text transforms
    text_transform_headings = models.CharField(
        max_length=20,
        default='none',
        choices=[
            ('none', 'None'),
            ('uppercase', 'Uppercase'),
            ('lowercase', 'Lowercase'),
            ('capitalize', 'Capitalize')
        ]
    )

    # Font loading strategy
    font_display = models.CharField(
        max_length=20,
        default='swap',
        choices=[
            ('auto', 'Auto'),
            ('block', 'Block'),
            ('swap', 'Swap'),
            ('fallback', 'Fallback'),
            ('optional', 'Optional')
        ],
        help_text="Controls how fonts are displayed while loading"
    )

    # Text rendering
    text_rendering = models.CharField(
        max_length=50,
        default='optimizeLegibility',
        choices=[
            ('auto', 'Auto'),
            ('optimizeSpeed', 'Optimize Speed'),
            ('optimizeLegibility', 'Optimize Legibility'),
            ('geometricPrecision', 'Geometric Precision')
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Typography"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.headings:
            self.headings = self.get_default_headings()
        if not self.paragraph_margin:
            self.paragraph_margin = self.get_default_paragraph_margins()
        super().save(*args, **kwargs)

    def get_default_headings(self):
        """Generate default heading configurations"""
        return {
            'h1': {
                'font_size': {'base': '2.5rem', 'md': '3rem', 'lg': '3.5rem'},
                'line_height': 1.2,
                'letter_spacing': '-0.025em',
                'font_weight': self.font_weight_bold,
                'margin_top': '0',
                'margin_bottom': '1rem',
                'text_transform': self.text_transform_headings,
            },
            'h2': {
                'font_size': {'base': '2rem', 'md': '2.25rem', 'lg': '2.5rem'},
                'line_height': 1.25,
                'letter_spacing': '-0.025em',
                'font_weight': self.font_weight_semibold,
                'margin_top': '1.5rem',
                'margin_bottom': '1rem',
                'text_transform': self.text_transform_headings,
            },
            'h3': {
                'font_size': {'base': '1.75rem', 'md': '1.875rem', 'lg': '2rem'},
                'line_height': 1.3,
                'letter_spacing': '-0.025em',
                'font_weight': self.font_weight_semibold,
                'margin_top': '1.5rem',
                'margin_bottom': '1rem',
                'text_transform': self.text_transform_headings,
            },
            'h4': {
                'font_size': {'base': '1.5rem', 'md': '1.5rem', 'lg': '1.75rem'},
                'line_height': 1.35,
                'letter_spacing': '-0.02em',
                'font_weight': self.font_weight_semibold,
                'margin_top': '1.5rem',
                'margin_bottom': '1rem',
                'text_transform': self.text_transform_headings,
            },
            'h5': {
                'font_size': {'base': '1.25rem', 'md': '1.25rem', 'lg': '1.5rem'},
                'line_height': 1.4,
                'letter_spacing': '-0.015em',
                'font_weight': self.font_weight_semibold,
                'margin_top': '1.25rem',
                'margin_bottom': '0.75rem',
                'text_transform': self.text_transform_headings,
            },
            'h6': {
                'font_size': {'base': '1rem', 'md': '1rem', 'lg': '1.125rem'},
                'line_height': 1.5,
                'letter_spacing': '0em',
                'font_weight': self.font_weight_semibold,
                'margin_top': '1rem',
                'margin_bottom': '0.5rem',
                'text_transform': self.text_transform_headings,
            }
        }

    def get_default_paragraph_margins(self):
        """Generate default paragraph margins"""
        return {
            'margin_top': '0',
            'margin_bottom': '1rem',
            'first_child': {'margin_top': '0'},
            'last_child': {'margin_bottom': '0'}
        }

    def get_font_face_rules(self):
        """Generate @font-face rules for selected fonts"""
        return f"""
        /* Primary Font */
        @font-face {{
            font-family: 'Primary Font';
            src: local('{self.font_primary.split(",")[0].strip(" '")}'),
                 url('/fonts/primary.woff2') format('woff2'),
                 url('/fonts/primary.woff') format('woff');
            font-weight: 100 900;
            font-style: normal;
            font-display: {self.font_display};
        }}

        /* Secondary Font */
        @font-face {{
            font-family: 'Secondary Font';
            src: local('{self.font_secondary.split(",")[0].strip(" '")}'),
                 url('/fonts/secondary.woff2') format('woff2'),
                 url('/fonts/secondary.woff') format('woff');
            font-weight: 100 900;
            font-style: normal;
            font-display: {self.font_display};
        }}
        """

    def get_css_variables(self):
        """Generate CSS variables for typography"""
        return {
            '--font-sans': self.font_primary,
            '--font-serif': 'ui-serif, Georgia, Cambria, "Times New Roman", Times, serif',
            '--font-mono': self.font_mono,
            '--font-accent': self.font_accent,

            '--text-base': f'{self.base_font_size}px',
            '--text-scale-ratio': '1.2',

            '--font-weight-light': str(self.font_weight_light),
            '--font-weight-normal': str(self.font_weight_normal),
            '--font-weight-medium': str(self.font_weight_medium),
            '--font-weight-semibold': str(self.font_weight_semibold),
            '--font-weight-bold': str(self.font_weight_bold),

            '--line-height-none': str(self.line_height_none),
            '--line-height-tight': str(self.line_height_tight),
            '--line-height-snug': str(self.line_height_snug),
            '--line-height-normal': str(self.line_height_normal),
            '--line-height-relaxed': str(self.line_height_relaxed),
            '--line-height-loose': str(self.line_height_loose),

            '--letter-spacing-tighter': f'{self.letter_spacing_tighter}em',
            '--letter-spacing-tight': f'{self.letter_spacing_tight}em',
            '--letter-spacing-normal': f'{self.letter_spacing_normal}em',
            '--letter-spacing-wide': f'{self.letter_spacing_wide}em',
            '--letter-spacing-wider': f'{self.letter_spacing_wider}em',
            '--letter-spacing-widest': f'{self.letter_spacing_widest}em',

            '--text-rendering': self.text_rendering,
            '--font-smoothing': self.font_smoothing,
        }
```

### **4. Style Class**
```python
class StyleClass(models.Model):
    """
    Reusable style classes with light/dark mode support and version-specific overrides.
    """
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='style_classes')
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)

    # Default CSS properties (base styles)
    default_css = models.JSONField(
        default=dict,
        help_text="Default CSS properties for this style class"
    )

    # Light/Dark mode overrides
    light_css = models.JSONField(
        default=dict,
        blank=True,
        help_text="Light mode CSS overrides (merges with default_css)"
    )
    dark_css = models.JSONField(
        default=dict,
        blank=True,
        help_text="Dark mode CSS overrides (merges with default_css)"
    )

    # Version-specific overrides (for different template versions)
    version_css = models.JSONField(
        default=dict,
        blank=True,
        help_text="Version-specific CSS overrides (e.g., {'v1': {...}, 'v2': {...}})"
    )

    # Media queries for responsive design
    media_queries = models.JSONField(
        default=dict,
        blank=True,
        help_text="Responsive styles (e.g., {'sm': {...}, 'md': {...}, 'lg': {...}})"
    )

    # Pseudo-class styles
    pseudo_classes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Pseudo-class styles (e.g., {'hover': {...}, 'focus': {...}, 'active': {...}})"
    )

    # Animation properties
    animations = models.JSONField(
        default=dict,
        blank=True,
        help_text="Animation properties (e.g., {'transition': 'all 0.3s ease', 'animation': 'fadeIn 0.5s'})"
    )

    # Custom CSS (raw CSS for complex styles)
    custom_css = models.TextField(
        blank=True,
        help_text="Raw CSS for complex styles that can't be expressed in JSON"
    )

    # Version-specific custom CSS
    version_custom_css = models.JSONField(
        default=dict,
        blank=True,
        help_text="Version-specific raw CSS (e.g., {'v1': '...', 'v2': '...'})"
    )

    # CSS variables for this class
    css_variables = models.JSONField(
        default=dict,
        blank=True,
        help_text="CSS variables specific to this class"
    )

    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False, help_text="System style classes cannot be deleted")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['theme', 'slug']]
        ordering = ['name']

    def get_css_for_version(self, version='default', mode='light'):
        """
        Get CSS properties for a specific version and mode
        """
        # Start with default CSS
        css = self.default_css.copy()

        # Apply mode-specific overrides
        if mode == 'dark' and self.dark_css:
            css.update(self.dark_css)
        elif mode == 'light' and self.light_css:
            css.update(self.light_css)

        # Apply version-specific overrides
        if version != 'default' and self.version_css.get(version):
            css.update(self.version_css[version])

        return css

    def get_custom_css_for_version(self, version='default'):
        """
        Get custom CSS for a specific version
        """
        if version != 'default' and self.version_custom_css.get(version):
            return self.version_custom_css[version]
        return self.custom_css

    def get_media_query_css(self, version='default', mode='light'):
        """
        Get media query CSS for responsive design
        """
        result = {}
        for breakpoint, styles in self.media_queries.items():
            # Apply version and mode overrides to media query styles
            css = styles.copy()
            if mode == 'dark' and self.dark_css:
                css.update(self.dark_css)
            if version != 'default' and self.version_css.get(version):
                css.update(self.version_css[version])
            result[breakpoint] = css
        return result

    def get_pseudo_class_css(self, pseudo_class, version='default', mode='light'):
        """
        Get pseudo-class CSS (hover, focus, active, etc.)
        """
        css = self.pseudo_classes.get(pseudo_class, {}).copy()

        # Apply mode-specific overrides
        if mode == 'dark' and self.dark_css:
            css.update(self.dark_css)
        elif mode == 'light' and self.light_css:
            css.update(self.light_css)

        # Apply version-specific overrides
        if version != 'default' and self.version_css.get(version):
            css.update(self.version_css[version])

        return css

    def generate_css_class(self, version='default', mode='light'):
        """
        Generate complete CSS class with all properties
        """
        css_rules = []

        # Main class
        main_css = self.get_css_for_version(version, mode)
        if main_css:
            main_props = '; '.join([f"{k}: {v}" for k, v in main_css.items()])
            css_rules.append(f".{self.slug} {{ {main_props}; }}")

        # Media queries
        media_css = self.get_media_query_css(version, mode)
        for breakpoint, styles in media_css.items():
            if styles:
                props = '; '.join([f"{k}: {v}" for k, v in styles.items()])
                css_rules.append(f"@media (min-width: {breakpoint}) {{ .{self.slug} {{ {props}; }} }}")

        # Pseudo-classes
        for pseudo in ['hover', 'focus', 'active', 'disabled']:
            pseudo_css = self.get_pseudo_class_css(pseudo, version, mode)
            if pseudo_css:
                props = '; '.join([f"{k}: {v}" for k, v in pseudo_css.items()])
                css_rules.append(f".{self.slug}:{pseudo} {{ {props}; }}")

        # Custom CSS
        custom_css = self.get_custom_css_for_version(version)
        if custom_css:
            css_rules.append(custom_css)

        # CSS variables
        if self.css_variables:
            var_props = '; '.join([f"{k}: {v}" for k, v in self.css_variables.items()])
            css_rules.append(f".{self.slug} {{ {var_props}; }}")

        return '\n'.join(css_rules)

    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
```

### **5. Layout**
```python
class Layout(models.Model):
    """
    Defines global structure including header, footer, and content slots.
    Each theme can have multiple layouts, with one default layout.
    """
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='layouts')
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    key = models.SlugField(max_length=100)
    description = models.TextField(blank=True)

    # Header & footer templates
    header_template = models.ForeignKey(
        'Template',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_as_header'
    )
    footer_template = models.ForeignKey(
        'Template',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_as_footer'
    )

    # Layout settings
    is_default = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Content slots (for dynamic content injection)
    content_slots = models.JSONField(
        default=dict,
        blank=True,
        help_text="Defines content slots and their default content"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['theme', 'key']]
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.theme.name})"

    def clean(self):
        # Ensure only one default layout per theme
        if self.is_default and self.theme:
            Layout.objects.filter(
                theme=self.theme,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
```

### **6. Template**
```python
class Template(models.Model):
    """
    Defines reusable template components with a specific role in the layout system.
    Templates are body-only by default, with specialized roles for headers and footers.
    """
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='templates')
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)

    TEMPLATE_ROLES = [
        ('body', 'Body'),        # Main content (default)
        ('header', 'Header'),    # Header component
        ('footer', 'Footer'),    # Footer component
        ('partial', 'Partial'),  # Reusable partials
        ('section', 'Section'),  # Page sections
    ]

    name = models.CharField(max_length=100)
    key = models.SlugField(max_length=100)
    template_role = models.CharField(
        max_length=20,
        choices=TEMPLATE_ROLES,
        default='body',
        help_text="Defines the template's role in the layout system"
    )
    description = models.TextField(blank=True)

    # Template content (body-only for header/footer roles)
    content = models.TextField(
        help_text="HTML template with variables (Django template syntax)"
    )
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    key = models.SlugField(max_length=100)
    description = models.TextField(blank=True)

    # Template content
    content = models.TextField(
        help_text="HTML template with variables (Django template syntax)"
    )

    # Advanced customization tab
    custom_css = models.TextField(
        blank=True,
        help_text="Custom CSS for this template"
    )
    custom_js = models.TextField(
        blank=True,
        help_text="Custom JavaScript for this template"
    )

    # Version-specific customizations
    version_css = models.JSONField(
        default=dict,
        blank=True,
        help_text="Version-specific CSS (e.g., {'v1': '...', 'v2': '...'})"
    )
    version_js = models.JSONField(
        default=dict,
        blank=True,
        help_text="Version-specific JavaScript (e.g., {'v1': '...', 'v2': '...'})"
    )

    # Template metadata
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Default meta title for pages using this template"
    )
    meta_description = models.TextField(
        blank=True,
        help_text="Default meta description for pages using this template"
    )
    meta_keywords = models.CharField(
        max_length=500,
        blank=True,
        help_text="Default meta keywords for pages using this template"
    )

    # Template settings
    is_default = models.BooleanField(
        default=False,
        help_text="Default template for this type and role"
    )
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(
        default=False,
        help_text="System templates cannot be deleted"
    )

    # Layout association (for body templates)
    layout = models.ForeignKey(
        'Layout',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Default layout for this template (body templates only)",
        related_name='templates_using_this_layout'
    )

    # Template variables (for documentation)
    variables = models.JSONField(
        default=dict,
        blank=True,
        help_text="Available variables in this template"
    )

    # Template dependencies
    requires = models.JSONField(
        default=list,
        blank=True,
        help_text="Required components or templates"
    )

    # Preview settings
    preview_image = models.URLField(
        blank=True,
        help_text="Preview image for template selection"
    )
    preview_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Sample data for template preview"
    )

    # Performance settings
    cache_duration = models.PositiveIntegerField(
        default=300,
        help_text="Cache duration in seconds"
    )
    minify_html = models.BooleanField(
        default=False,
        help_text="Minify HTML output"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['theme', 'key']]
        ordering = ['template_type', 'name']
        indexes = [
            models.Index(fields=['theme', 'template_type']),
            models.Index(fields=['is_default', 'is_active']),
        ]

    def get_css_for_version(self, version='default'):
        """
        Get CSS for a specific version
        """
        if version != 'default' and self.version_css.get(version):
            return self.version_css[version]
        return self.custom_css

    def get_js_for_version(self, version='default'):
        """
        Get JavaScript for a specific version
        """
        if version != 'default' and self.version_js.get(version):
            return self.version_js[version]
        return self.custom_js

    def render_content(self, context=None):
        """
        Render template content with context.
        For header/footer templates, ensures no <html> or <body> tags.
        """
        from django.template import Template, Context
        from django.template.exceptions import TemplateSyntaxError

        content = Template(self.content).render(Context(context or {}))
            'template_name': self.name,
            'template_key': self.key,
        })

        # Render the template
        django_template = DjangoTemplate(self.content)
        return django_template.render(DjangoContext(template_context))

    def get_variables_list(self):
        """
        Extract variables from template content
        """
        import re
        variables = set()

        # Find Django template variables
        pattern = r'\{\{\s*([^}]+)\s*\}\}'
        matches = re.findall(pattern, self.content)

        for match in matches:
            # Clean up the variable name
            var = match.strip().split('.')[0].strip()
            if var and not var.startswith('|') and not var.startswith('if'):
                variables.add(var)

        return sorted(list(variables))

    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)

        # Extract variables from content
        if not self.variables:
            self.variables = self.get_variables_list()

        super().save(*args, **kwargs)

---

## API Endpoints

### **Public API (v2)**
```
GET    /api/v2/themes/current/           # Get current theme
GET    /api/v2/themes/current/scheme/    # Get active color scheme
GET    /api/v2/templates/{type}/{slug}/  # Get template by type and slug
```

### **Dashboard API (v2)**
```
# Themes
GET    /api/v2/dashboard/themes/                 # List themes
POST   /api/v2/dashboard/themes/                 # Create theme
GET    /api/v2/dashboard/themes/{id}/            # Get theme
PUT    /api/v2/dashboard/themes/{id}/            # Update theme
DELETE /api/v2/dashboard/themes/{id}/            # Delete theme
POST   /api/v2/dashboard/themes/{id}/activate/   # Activate theme

# Color Schemes
GET    /api/v2/dashboard/themes/{id}/schemes/    # List color schemes
POST   /api/v2/dashboard/themes/{id}/schemes/    # Create color scheme

# Templates
GET    /api/v2/dashboard/templates/              # List templates
POST   /api/v2/dashboard/templates/              # Create template
GET    /api/v2/dashboard/templates/{id}/         # Get template
PUT    /api/v2/dashboard/templates/{id}/         # Update template
DELETE /api/v2/dashboard/templates/{id}/         # Delete template
```

---

## 🔒 Permissions

### **Public Access**
- Read-only access to active theme and templates
- No authentication required

### **Store Staff**
- Full CRUD on own store's themes
- Can activate/deactivate themes
- Can manage color schemes and templates

### **Super Admin**
- Full access to all themes across stores
- Can manage global theme settings

---

## 🧪 Testing Strategy

### **Unit Tests**
- Model validation and methods
- Service layer logic
- Template rendering

### **Integration Tests**
- API endpoints
- Theme activation flow
- Template inheritance

### **Performance Tests**
- Theme compilation
- Template rendering speed
- Asset loading

---

## 🚀 Deployment

### **Environment Variables**
```bash
# Theme Settings
DEFAULT_THEME="default"
THEME_CACHE_TIMEOUT=3600  # 1 hour
ENABLE_THEME_PREVIEW=true
```

### **Required Services**
- Redis (for theme caching)
- Storage (for theme assets)

### **Migrations**
```bash
python manage.py makemigrations themes
python manage.py migrate themes
```

---

## 📝 Implementation Notes

1. **Caching Strategy**
   - Cache compiled themes
   - Invalidate on theme update
   - Use cache tags for selective invalidation

2. **Template Variables**
   - Use Django template syntax
   - Predefined variables: `{{ store }}`, `{{ page }}`, `{{ request }}`
   - Custom variables via context processors

3. **Asset Management**
   - Store assets in theme-specific directories
   - Version assets for cache busting
   - Support CDN integration

4. **Theme Editor**
   - Live preview
   - Undo/redo functionality
   - Version history

---

## 🔄 Versioning

- Current version: v2 (only version)
- No backward compatibility with v1
- All new features go into v2

---

## 📚 References

1. [Shopify Theme Architecture](https://shopify.dev/themes/architecture)
2. [Django Templates](https://docs.djangoproject.com/en/stable/topics/templates/)
3. [Tailwind CSS Configuration](https://tailwindcss.com/docs/configuration)

---

## ✅ Checklist

### **Phase 1: Core Functionality**
- [ ] Theme model and API
- [ ] Color scheme management
- [ ] Basic template rendering

### **Phase 2: Advanced Features**
- [ ] Typography system
- [ ] Style classes
- [ ] Template inheritance

### **Phase 3: Editor & Tools**
- [ ] Theme editor UI
- [ ] Asset management
- [ ] Preview system

### **Phase 4: Optimization**
- [ ] Caching layer
- [ ] Performance tuning
- [ ] Documentation

---

## 📅 Timeline

- **Week 1-2**: Core models and API
- **Week 3-4**: Template system
- **Week 5-6**: Editor UI
- **Week 7-8**: Testing and optimization

---

## 🧩 Layout System

### Core Concepts

1. **Templates are body-only by default**
   - No `<html>`, `<head>`, or `<body>` tags in templates
   - Each template has a specific role (body, header, footer, etc.)

2. **Layouts define page structure**
   - Composed of header, footer, and content slots
   - Multiple layouts per theme, with one default
   - Pages can override their layout

3. **Separation of concerns**
   - Layout = Structure (header + footer + slots)
   - Template = Content (body only)
   - Page = Template + Layout

### Implementation Rules

1. **Template Roles**
   ```python
   # Allowed template roles
   TEMPLATE_ROLES = [
       ('body', 'Body'),        # Main content (default)
       ('header', 'Header'),    # Header component
       ('footer', 'Footer'),    # Footer component
       ('partial', 'Partial'),  # Reusable partials
       ('section', 'Section'),  # Page sections
   ]
   ```

2. **Layout Resolution**
   ```python
   def get_page_layout(page):
       """Resolve layout for a page with fallbacks"""
       # 1. Page-specific layout
       if page.layout:
           return page.layout

       # 2. Template's default layout
       if page.template and page.template.layout:
           return page.template.layout

       # 3. Theme's default layout
       return Layout.objects.filter(
           theme=page.theme,
           is_default=True
       ).first()
   ```

3. **Rendering Flow**
   ```python
   def render_page(page, context):
       """Render a complete page with layout"""
       layout = get_page_layout(page)

       # Start with empty HTML
       html = []

       # Add header if layout has one
       if layout and layout.header_template:
           html.append(layout.header_template.render_content(context))

       # Add main content
       html.append(page.template.render_content(context))

       # Add footer if layout has one
       if layout and layout.footer_template:
           html.append(layout.footer_template.render_content(context))

       return '\n'.join(html)
   ```

## 🚨 Known Limitations

1. No visual editor (code-only templates)
2. Limited to single-level template inheritance
3. No built-in theme marketplace

---

## 🔮 Future Enhancements

1. Visual theme editor
2. Theme marketplace
3. A/B testing for themes
4. Theme versioning and rollback
5. Multi-language support

---

Last Updated: January 23, 2026

<!-- ===============================================================================
 END THEMES.MD
 ================================================================================= -->


<!-- ===============================================================================
 START TRANSLATIONS.MD
 ================================================================================= -->
# Translation System Rules

## 1. Overview

This document outlines the backend-driven translation system for DFCMS, enabling multi-language support across all store content with a focus on:

- Backend-only translation processing
- HTML content support with XSS protection
- Store-specific language defaults
- High performance with Redis caching
- Admin UI for translation management

## 2. Core Components

### 2.1 Models

```python
# translations/models.py
from django.db import models
from django.conf import settings
import bleach

class Language(models.Model):
    """Supported languages in the system"""
    code = models.CharField(max_length=10, unique=True)  # ISO 639-1
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TranslationKey(models.Model):
    """Translation keys with metadata"""
    key = models.CharField(max_length=255, unique=True, db_index=True)
    namespace = models.CharField(max_length=100, db_index=True, default='default')
    description = models.TextField(blank=True)
    content_type = models.CharField(
        max_length=20,
        choices=[('plain', 'Plain Text'), ('html', 'HTML Content')],
        default='plain'
    )
    plural_form = models.CharField(
        max_length=10,
        choices=[
            ('none', 'Not pluralizable'),
            ('en', 'English (1 item/2 items)'),
            ('ar', 'Arabic (complex forms)')
        ],
        default='none'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Translation(models.Model):
    """Actual translations"""
    key = models.ForeignKey(TranslationKey, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    is_auto_translated = models.BooleanField(default=False)
    needs_review = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['key', 'language', 'store']]
```

### 2.2 Translation Parser

```python
# translations/utils/translation_parser.py
import hashlib
import bleach
from bs4 import BeautifulSoup, NavigableString
from django.conf import settings
from django.core.cache import caches

class TranslationParser:
    """Parses and translates HTML content"""

    def __init__(self, store=None, language_code=None, user=None):
        self.store = store
        self.language_code = language_code or settings.LANGUAGE_CODE
        self.user = user
        self.cache = caches['translations']

    def parse_html(self, html_content, cache_key=None):
        """Parse and translate HTML content with caching"""
        if not html_content:
            return html_content

        if not cache_key and self.store:
            cache_key = self._generate_cache_key(html_content)
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        soup = BeautifulSoup(html_content, 'html.parser')
        self._process_nodes(soup)

        result = str(soup)
        if cache_key:
            self.cache.set(cache_key, result, timeout=3600)

        return result

    def _process_nodes(self, soup):
        """Process all translatable nodes"""
        for text_node in self._find_translatable_text_nodes(soup):
            self._process_text_node(text_node)

        for tag in soup.find_all(attrs=True):
            self._process_attributes(tag)

    def _process_text_node(self, text_node):
        """Process a single text node with XSS protection"""
        original = text_node.string.strip()
        if not original or len(original) < 2:
            return

        # Sanitize HTML content
        if '<' in original:
            original = bleach.clean(
                original,
                tags=settings.BLEACH_ALLOWED_TAGS,
                attributes=settings.BLEACH_ALLOWED_ATTRIBUTES
            )

        # Get or create translation key
        key = self._get_or_create_key(original)

        # Get translation
        translation = self._get_translation(key, original)
        if translation and translation.text != original:
            text_node.replace_with(translation.text)

    # ... (other helper methods)
```

## 3. Middleware

```python
# translations/middleware.py
from django.utils import translation
from django.conf import settings
import re

class TranslationMiddleware:
    """Handles request/response translation"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.ignore_paths = [
            r'^/admin/', r'^/static/', r'^/media/', r'^/api/',
            r'\.(js|css|jpg|jpeg|png|gif|ico|svg|woff|ttf|eot|webp|mp4|webm|mp3|wav|ogg|json|xml|csv)$'
        ]

    def __call__(self, request):
        # Set language from request
        self.set_language(request)

        # Process response
        response = self.get_response(request)

        # Skip translation for certain paths/content types
        if self.should_skip_translation(request, response):
            return response

        # Parse and translate response
        return self.translate_response(request, response)

    def set_language(self, request):
        """Set language from request"""
        language = self.get_language_from_request(request)
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

    def get_language_from_request(self, request):
        """Get language with store fallback"""
        # 1. URL parameter
        if 'lang' in request.GET:
            return request.GET['lang']

        # 2. Session
        if hasattr(request, 'session') and 'django_language' in request.session:
            return request.session['django_language']

        # 3. Store default
        store = getattr(request, 'store', None)
        if store and hasattr(store, 'default_language') and store.default_language:
            return store.default_language.code

        # 4. Accept-Language header
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            try:
                return translation.get_supported_language_variant(
                    request.META['HTTP_ACCEPT_LANGUAGE'].split(',')[0].split(';')[0].strip()
                )
            except LookupError:
                pass

        # 5. Default from settings
        return settings.LANGUAGE_CODE
```

## 4. Admin Integration

### 4.1 Admin Interface

```python
# translations/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import TranslationKey, Translation, Language

@admin.register(TranslationKey)
class TranslationKeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'namespace', 'content_type', 'translation_count')
    list_filter = ('namespace', 'content_type', 'plural_form')
    search_fields = ('key', 'description')

    def translation_count(self, obj):
        return obj.translations.count()
    translation_count.short_description = 'Translations'

@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('key', 'language', 'store', 'preview_text', 'is_auto_translated')
    list_filter = ('language', 'store', 'is_auto_translated')
    search_fields = ('key__key', 'text')

    def preview_text(self, obj):
        return obj.text[:100] + ('...' if len(obj.text) > 100 else '')
    preview_text.short_description = 'Text Preview'

admin.site.register(Language)
```

### 4.2 Editor Integration

1. **HTML Markup**:
   ```html
   <div data-i18n="welcome.message">Hello World</div>
   <span data-i18n-plural="items.count" data-count="5">
     {count} items
   </span>
   ```

2. **Editor Toolbar**:
   - Add "Translate" button to editor
   - On click, open translation dialog with:
     - Original text
     - Available languages
     - Translation inputs
     - Save/Cancel buttons

## 5. Caching Strategy

### 5.1 Cache Keys

```python
def get_cache_key(store_id, language_code, content_hash):
    return f"trans:{store_id or 'global'}:{language_code}:{content_hash}"
```

### 5.2 Cache Invalidation

- Invalidate on translation update
- Use cache versioning for bulk updates
- Set appropriate TTL (e.g., 1 hour)

## 6. Security

### 6.1 XSS Protection

- Always use Bleach for HTML sanitization
- Define allowed tags and attributes in settings
- Escape all user-provided content

### 6.2 Rate Limiting

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'translation': '50/hour'  # For translation API
    }
}
```

## 7. Performance Optimization

### 7.1 Caching Layers

1. **Full Page Caching**:
   - Cache entire rendered pages per language
   - Invalidate on content/translation updates

2. **Fragment Caching**:
   - Cache individual components
   - Use template fragment caching

3. **Database Query Optimization**:
   - Use `select_related` and `prefetch_related`
   - Add appropriate database indexes

### 7.2 Async Processing

```python
# tasks.py
from celery import shared_task
from .utils.translation_parser import TranslationParser

@shared_task
def prewarm_translation_cache(store_id, language_code, content_hashes):
    """Prewarm cache for common translations"""
    parser = TranslationParser(store_id=store_id, language_code=language_code)
    for content_hash in content_hashes:
        parser.get_cached_translation(content_hash)
```

## 8. Testing

### 8.1 Test Cases

```python
# tests/test_translations.py
from django.test import TestCase
from django.test.utils import override_settings
from .factories import TranslationFactory

class TranslationTests(TestCase):
    def test_html_sanitization(self):
        # Test XSS protection
        pass

    def test_plural_forms(self):
        # Test pluralization
        pass

    def test_performance(self):
        # Test with large content
        pass
```

## 9. Deployment

### 9.1 Requirements

- Redis server for caching
- Database with JSON field support
- Sufficient memory for cache

### 9.2 Monitoring

- Cache hit/miss ratios
- Translation lookup times
- Error rates
- Memory usage

## 10. Maintenance

### 10.1 Cleanup Tasks

```python
# management/commands/cleanup_translations.py
from django.core.management.base import BaseCommand
from django.db.models import Count
from ..models import TranslationKey

class Command(BaseCommand):
    help = 'Clean up unused translation keys'

    def handle(self, *args, **options):
        # Find and delete unused keys
        unused = TranslationKey.objects.annotate(
            trans_count=Count('translations')
        ).filter(trans_count=0)

        count = unused.count()
        if count > 0:
            self.stdout.write(f'Deleting {count} unused translation keys...')
            unused.delete()
            self.stdout.write(self.style.SUCCESS('Cleanup complete'))
        else:
            self.stdout.write('No unused translation keys found')
```

## 11. Best Practices

1. **Key Naming**:
   - Use dot notation: `namespace.component.key`
   - Be descriptive but concise
   - Group related keys

2. **Content Guidelines**:
   - Keep translations complete sentences when possible
   - Avoid string concatenation
   - Provide context for translators

3. **Performance**:
   - Cache aggressively
   - Use bulk operations
   - Monitor and optimize queries

## Review this final polished backend-only translation plan carefully before applying.

<!-- ===============================================================================
 END TRANSLATIONS.MD
 ================================================================================= -->


<!-- ===============================================================================
 START WEEBHOOKS.MD
 ================================================================================= -->
# Webhooks App Rules v1.0

## 🎯 Purpose

This document defines strict development rules for the **webhooks** app in CMS-Updated backend, implementing a secure and reliable webhook system for event-driven integrations with external services.

---

## 🏗️ Webhooks App Structure

### **Fixed Directory Structure**
```
apps/
├── webhooks/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── admin.py
│   ├── signals.py
│   ├── services.py
│   ├── tasks.py
│   ├── management/
│   │   └── commands/
│   │       ├── cleanup_webhooks.py
│   │       └── retry_failed_deliveries.py
│   ├── migrations/
│   ├── v2/
│   │   ├── __init__.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_services.py
│       └── test_views.py
```

---

## 📋 Core Models

### **Model Inheritance**
All webhooks models must inherit from `TenantModel` for store scoping:

```python
from core.models import TenantModel
from django.db import models

class Webhook(TenantModel):
    # Store-scoped webhook model
    pass
```

### **Webhook Model**
```python
# apps/webhooks/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import TenantModel
import secrets

User = get_user_model()

class Webhook(TenantModel):
    """
    Store-scoped webhook configuration for external integrations
    """

    # Core fields
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Endpoint configuration
    url = models.URLField(max_length=2048)
    method = models.CharField(max_length=10, choices=[('POST', 'POST'), ('PUT', 'PUT')], default='POST')

    # Security
    secret = models.CharField(max_length=255, default=secrets.token_urlsafe, help_text="HMAC signature secret")
    verify_ssl = models.BooleanField(default=True, help_text="Verify SSL certificate")

    # Event filtering
    events = models.JSONField(default=list, help_text="List of event types to subscribe to")
    event_filter = models.JSONField(default=dict, help_text="Advanced event filtering rules")

    # Headers
    headers = models.JSONField(default=dict, help_text="Custom HTTP headers")

    # Status
    is_active = models.BooleanField(default=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)

    # Retry configuration
    max_retries = models.PositiveSmallIntegerField(default=5)
    retry_delay = models.PositiveIntegerField(default=60, help_text="Initial retry delay in seconds")
    retry_backoff_multiplier = models.FloatField(default=2.0, help_text="Exponential backoff multiplier")

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = 'webhooks_webhook'
        unique_together = [['store', 'url']]
        indexes = [
            models.Index(fields=['store', 'is_active']),
            models.Index(fields=['last_triggered_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.url}"

    def generate_signature(self, payload):
        """Generate HMAC signature for payload"""
        import hmac
        import hashlib
        import json

        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self.secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return f"sha256={signature}"

    def is_event_subscribed(self, event_type, event_data=None):
        """Check if webhook should be triggered for this event"""
        # Check if event type is in subscribed events
        if event_type not in self.events:
            return False

        # Apply advanced filtering if configured
        if self.event_filter:
            return self._apply_event_filter(event_type, event_data)

        return True

    def _apply_event_filter(self, event_type, event_data):
        """Apply advanced event filtering rules"""
        # Example filter: {"entity_type": "Order", "status": ["completed", "refunded"]}
        for key, value in self.event_filter.items():
            if key in event_data:
                if isinstance(value, list):
                    if event_data[key] not in value:
                        return False
                elif event_data[key] != value:
                    return False
        return True
```

### **WebhookEvent Model**
```python
class WebhookEvent(TenantModel):
    """
    Represents an event that can trigger webhooks
    """

    # Core fields
    event_type = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=[
        ('content', 'Content'),
        ('ecommerce', 'Ecommerce'),
        ('user', 'User'),
        ('system', 'System'),
    ])

    # Event schema
    schema = models.JSONField(default=dict, help_text="Event payload schema")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'webhooks_event'
        ordering = ['category', 'event_type']

    def __str__(self):
        return f"{self.event_type} ({self.category})"
```

### **WebhookDelivery Model**
```python
class WebhookDelivery(TenantModel):
    """
    Tracks individual webhook delivery attempts
    """

    # Relationships
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name='deliveries')

    # Event details
    event_type = models.CharField(max_length=100)
    event_id = models.CharField(max_length=100, blank=True)

    # Payload
    payload = models.JSONField(default=dict)

    # Delivery details
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ], default='pending')

    # Response details
    response_status = models.PositiveIntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    response_headers = models.JSONField(default=dict, blank=True)

    # Retry tracking
    attempt_number = models.PositiveSmallIntegerField(default=1)
    next_retry_at = models.DateTimeField(null=True, blank=True)

    # Timing
    triggered_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    # Error details
    error_message = models.TextField(blank=True)
    error_code = models.CharField(max_length=50, blank=True)

    class Meta(TenantModel.Meta):
        db_table = 'webhooks_delivery'
        indexes = [
            models.Index(fields=['webhook', 'status']),
            models.Index(fields=['event_type']),
            models.Index(fields=['triggered_at']),
            models.Index(fields=['next_retry_at']),
        ]
        ordering = ['-triggered_at']

    def __str__(self):
        return f"Delivery #{self.id} - {self.event_type} ({self.status})"
```

---

## 🔌 API Endpoints

### **V2-Only Implementation**
All webhook endpoints must be V2-only with clean architecture:

#### WebhookViewSet
```python
# apps/webhooks/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class WebhookViewSet(TenantViewSet):
    """
    Webhook management endpoints for dashboard
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    queryset = Webhook.objects.all()
    serializer_class = WebhookSerializer
    filterset_fields = ['is_active']
    search_fields = ['name', 'url', 'description']
    ordering_fields = ['created_at', 'name', 'last_triggered_at']
    ordering = ['-created_at']

    @extend_schema(
        summary="Test Webhook",
        description="Send test payload to webhook endpoint",
        responses={200: WebhookDeliverySerializer}
    )
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Send test event to webhook"""
        webhook = self.get_object()

        from services.webhook import WebhookService
        delivery = WebhookService.trigger_webhook(
            webhook=webhook,
            event_type='test',
            event_data={'test': True, 'timestamp': timezone.now().isoformat()},
            store=webhook.store
        )

        serializer = WebhookDeliverySerializer(delivery)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Regenerate Secret",
        description="Generate new webhook secret",
        responses={200: WebhookSerializer}
    )
    @action(detail=True, methods=['post'])
    def regenerate_secret(self, request, pk=None):
        """Regenerate webhook secret"""
        webhook = self.get_object()
        webhook.secret = secrets.token_urlsafe()
        webhook.save(update_fields=['secret'])

        serializer = self.get_serializer(webhook)
        return Response(serializer.data, status=status.HTTP_200_OK)
```

#### WebhookDeliveryViewSet
```python
class WebhookDeliveryViewSet(TenantViewSet):
    """
    Webhook delivery tracking endpoints
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    queryset = WebhookDelivery.objects.all()
    serializer_class = WebhookDeliverySerializer
    filterset_fields = ['webhook', 'status', 'event_type']
    ordering_fields = ['triggered_at', 'delivered_at']
    ordering = ['-triggered_at']
```

---

## 🛠️ Services Layer

### **Business Logic Centralization**
All webhook business logic must be in services.py:

#### WebhookService
```python
# apps/webhooks/services.py
import requests
from django.utils import timezone
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class WebhookService:
    """Shared webhook management service"""

    @staticmethod
    @transaction.atomic
    def trigger_webhook(webhook, event_type, event_data, store):
        """
        Trigger a webhook with retry logic
        """
        # Check if webhook is subscribed to this event
        if not webhook.is_event_subscribed(event_type, event_data):
            return None

        # Create delivery record
        delivery = WebhookDelivery.objects.create(
            webhook=webhook,
            event_type=event_type,
            event_id=event_data.get('id', ''),
            payload=event_data,
            status='pending',
            attempt_number=1
        )

        # Update webhook last triggered timestamp
        webhook.last_triggered_at = timezone.now()
        webhook.save(update_fields=['last_triggered_at'])

        # Trigger async delivery
        from .tasks import deliver_webhook
        deliver_webhook.delay(delivery.id)

        return delivery

    @staticmethod
    def deliver_webhook_sync(delivery):
        """
        Synchronous webhook delivery
        """
        webhook = delivery.webhook

        # Prepare request
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': webhook.generate_signature(delivery.payload),
            'X-Webhook-Event': delivery.event_type,
            'X-Webhook-ID': str(delivery.id),
            'X-Store-ID': str(webhook.store.id),
            **webhook.headers
        }

        # Measure delivery time
        start_time = timezone.now()

        try:
            response = requests.request(
                method=webhook.method,
                url=webhook.url,
                json=delivery.payload,
                headers=headers,
                verify=webhook.verify_ssl,
                timeout=30
            )

            # Calculate duration
            duration_ms = int((timezone.now() - start_time).total_seconds() * 1000)

            # Update delivery
            delivery.response_status = response.status_code
            delivery.response_body = response.text[:10000]  # Limit response body size
            delivery.response_headers = dict(response.headers)
            delivery.delivered_at = timezone.now()
            delivery.duration_ms = duration_ms

            # Determine status
            if 200 <= response.status_code < 300:
                delivery.status = 'success'
            else:
                delivery.status = 'failed'
                delivery.error_message = f"HTTP {response.status_code}"
                delivery.error_code = 'HTTP_ERROR'

            delivery.save(update_fields=[
                'response_status', 'response_body', 'response_headers',
                'delivered_at', 'duration_ms', 'status', 'error_message', 'error_code'
            ])

            # Log delivery
            logger.info(
                f"Webhook #{delivery.id} delivered to {webhook.url} "
                f"- Status: {response.status_code} - Duration: {duration_ms}ms"
            )

        except requests.exceptions.Timeout:
            delivery.status = 'failed'
            delivery.error_message = 'Request timeout'
            delivery.error_code = 'TIMEOUT'
            delivery.save(update_fields=['status', 'error_message', 'error_code'])
            logger.error(f"Webhook #{delivery.id} timeout")

        except requests.exceptions.SSLError as e:
            delivery.status = 'failed'
            delivery.error_message = f'SSL error: {str(e)}'
            delivery.error_code = 'SSL_ERROR'
            delivery.save(update_fields=['status', 'error_message', 'error_code'])
            logger.error(f"Webhook #{delivery.id} SSL error: {e}")

        except requests.exceptions.RequestException as e:
            delivery.status = 'failed'
            delivery.error_message = str(e)
            delivery.error_code = 'REQUEST_ERROR'
            delivery.save(update_fields=['status', 'error_message', 'error_code'])
            logger.error(f"Webhook #{delivery.id} request error: {e}")

        # Schedule retry if failed and retries remaining
        if delivery.status == 'failed' and delivery.attempt_number < webhook.max_retries:
            WebhookService.schedule_retry(delivery)

        return delivery

    @staticmethod
    def schedule_retry(delivery):
        """
        Schedule webhook delivery retry with exponential backoff
        """
        webhook = delivery.webhook

        # Calculate retry delay with exponential backoff
        retry_delay = webhook.retry_delay * (webhook.retry_backoff_multiplier ** (delivery.attempt_number - 1))

        # Update delivery
        delivery.status = 'retrying'
        delivery.attempt_number += 1
        delivery.next_retry_at = timezone.now() + timezone.timedelta(seconds=retry_delay)
        delivery.save(update_fields=['status', 'attempt_number', 'next_retry_at'])

        # Schedule retry task
        from .tasks import deliver_webhook
        deliver_webhook.apply_async(
            args=[delivery.id],
            eta=delivery.next_retry_at
        )

        logger.info(
            f"Webhook #{delivery.id} scheduled for retry #{delivery.attempt_number} "
            f"in {retry_delay}s"
        )
```

---

## 🔄 Celery Tasks

### **Async Webhook Delivery**
```python
# apps/webhooks/tasks.py
from celery import shared_task
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def deliver_webhook(self, delivery_id):
    """
    Async webhook delivery task
    """
    from .models import WebhookDelivery
    from .services import WebhookService

    try:
        delivery = WebhookDelivery.objects.select_related('webhook').get(id=delivery_id)

        # Skip if already successful
        if delivery.status == 'success':
            return {'status': 'already_delivered'}

        # Deliver webhook
        result = WebhookService.deliver_webhook_sync(delivery)

        return {
            'delivery_id': delivery_id,
            'status': result.status,
            'response_status': result.response_status
        }

    except WebhookDelivery.DoesNotExist:
        logger.error(f"Webhook delivery #{delivery_id} not found")
        raise

    except Exception as exc:
        logger.error(f"Webhook delivery failed: {exc}")
        raise self.retry(exc=exc, countdown=60)

@shared_task
def cleanup_old_deliveries(days=90):
    """
    Clean up old webhook delivery records
    """
    from django.utils import timezone
    from .models import WebhookDelivery

    cutoff = timezone.now() - timezone.timedelta(days=days)
    deleted_count = WebhookDelivery.objects.filter(
        triggered_at__lt=cutoff,
        status='success'
    ).delete()[0]

    logger.info(f"Cleaned up {deleted_count} old webhook deliveries")
    return deleted_count
```

---

## 🔒 Security Rules

### **Webhook Security**
- **Signature Verification**: All webhooks must use HMAC SHA-256 signatures
- **Secret Management**: Secrets must be cryptographically secure and rotatable
- **SSL Verification**: SSL verification should be enabled by default
- **Rate Limiting**: Implement rate limiting on webhook endpoints
- **Payload Validation**: Validate payload structure before processing
- **URL Validation**: Validate webhook URLs to prevent SSRF attacks
- **Timeout Protection**: Implement request timeouts to prevent hanging
- **Size Limits**: Limit payload and response sizes

### **Signature Verification**
```python
# Example signature verification in external service
import hmac
import hashlib
import json

def verify_webhook_signature(payload, signature, secret):
    """
    Verify webhook signature
    """
    payload_str = json.dumps(payload, sort_keys=True)
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(f"sha256={expected_signature}", signature)
```

---

## 📊 Performance Rules

### **Delivery Optimization**
- **Async Delivery**: All webhook deliveries must be asynchronous
- **Batch Processing**: Process multiple webhooks in parallel where appropriate
- **Retry Logic**: Implement exponential backoff for retries
- **Queue Management**: Use Celery for delivery queue management
- **Cleanup**: Regular cleanup of old delivery records

### **Database Optimization**
- **Indexes**: Add indexes on frequently queried fields
- **Query Optimization**: Use `select_related` for webhook lookups
- **Bulk Operations**: Use bulk operations for cleanup tasks
- **Partitioning**: Consider partitioning large delivery tables by date

---

## 🧪 Testing Rules

### **Required Coverage**
- **Models**: 95% code coverage
- **Services**: 100% code coverage
- **Views**: 90% code coverage
- **Integration**: Critical path testing

### **Test Examples**
```python
# apps/webhooks/tests/test_services.py
from django.test import TestCase
from django.utils import timezone
from ..models import Webhook, WebhookDelivery
from ..services import WebhookService

class WebhookServiceTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', slug='test-store')
        self.webhook = Webhook.objects.create(
            store=self.store,
            name='Test Webhook',
            url='https://example.com/webhook',
            events=['order.created']
        )

    def test_trigger_webhook(self):
        """Test webhook triggering"""
        event_data = {'id': '123', 'status': 'created'}
        delivery = WebhookService.trigger_webhook(
            webhook=self.webhook,
            event_type='order.created',
            event_data=event_data,
            store=self.store
        )

        self.assertIsNotNone(delivery)
        self.assertEqual(delivery.event_type, 'order.created')
        self.assertEqual(delivery.status, 'pending')

    def test_webhook_not_subscribed(self):
        """Test webhook not subscribed to event"""
        delivery = WebhookService.trigger_webhook(
            webhook=self.webhook,
            event_type='product.created',
            event_data={'id': '456'},
            store=self.store
        )

        self.assertIsNone(delivery)

    def test_signature_generation(self):
        """Test signature generation"""
        payload = {'test': 'data'}
        signature = self.webhook.generate_signature(payload)

        self.assertTrue(signature.startswith('sha256='))
        self.assertEqual(len(signature), 71)  # sha256= + 64 hex chars
```

---

## 🔗 Integration Rules

### **Required Integrations**
- **stores.md**: Store scoping and multi-tenancy
- **logs.md**: Activity logging for webhook events
- **accounts.md**: User authentication and permissions
- **core.md**: TenantModel and TenantViewSet

### **Integration Examples**
```python
# Integration with logs.md for event logging
from services.log import LogService

def log_webhook_event(delivery):
    """Log webhook delivery event"""
    LogService.log_event(
        event_type='webhook_delivered',
        level='INFO',
        message=f"Webhook #{delivery.id} delivered to {delivery.webhook.url}",
        store=delivery.webhook.store,
        metadata={
            'webhook_id': delivery.webhook.id,
            'event_type': delivery.event_type,
            'status': delivery.status,
            'response_status': delivery.response_status
        }
    )

# Integration with ecommerce.md for order events
from signals import order_created

@receiver(order_created)
def trigger_order_webhooks(sender, instance, **kwargs):
    """Trigger webhooks on order creation"""
    webhooks = Webhook.objects.filter(
        store=instance.store,
        is_active=True
    )

    event_data = {
        'id': str(instance.id),
        'order_number': instance.order_number,
        'status': instance.status,
        'total': float(instance.total),
        'created_at': instance.created_at.isoformat()
    }

    for webhook in webhooks:
        WebhookService.trigger_webhook(
            webhook=webhook,
            event_type='order.created',
            event_data=event_data,
            store=instance.store
        )
```

---

## 📈 Event Types Reference

### **Content Events**
- `page.created` - New page created
- `page.updated` - Page updated
- `page.published` - Page published
- `page.deleted` - Page deleted
- `post.created` - New blog post created
- `post.updated` - Blog post updated
- `post.published` - Blog post published
- `post.deleted` - Blog post deleted

### **Ecommerce Events**
- `product.created` - New product created
- `product.updated` - Product updated
- `product.deleted` - Product deleted
- `order.created` - New order created
- `order.updated` - Order updated
- `order.completed` - Order completed
- `order.refunded` - Order refunded
- `cart.created` - Cart created
- `cart.updated` - Cart updated
- `checkout.completed` - Checkout completed

### **User Events**
- `user.registered` - New user registered
- `user.login` - User logged in
- `user.logout` - User logged out
- `user.updated` - User profile updated

### **System Events**
- `store.created` - New store created
- `store.updated` - Store updated
- `webhook.test` - Test webhook event

---

## 🚀 Deployment Notes

### **Required Dependencies**
```python
# requirements.txt
requests>=2.31.0
celery>=5.3.0
```

### **Celery Configuration**
```python
# settings.py
CELERY_BEAT_SCHEDULE = {
    'cleanup-webhook-deliveries': {
        'task': 'apps.webhooks.tasks.cleanup_old_deliveries',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}
```

### **Monitoring**
- Monitor webhook delivery success rates
- Track retry attempts and failures
- Alert on high failure rates
- Monitor queue sizes

---

## 📚 Best Practices

1. **Always use async delivery** - Never block on webhook delivery
2. **Implement proper retry logic** - Use exponential backoff
3. **Validate all payloads** - Ensure data integrity
4. **Log all deliveries** - Maintain audit trail
5. **Rotate secrets regularly** - Security best practice
6. **Rate limit endpoints** - Prevent abuse
7. **Clean up old records** - Prevent table bloat
8. **Monitor performance** - Track delivery times and success rates
9. **Provide clear error messages** - Help with debugging
10. **Document event schemas** - Ensure external integrators understand payloads

---

## 🔧 Management Commands

### **Cleanup Old Deliveries**
```bash
python manage.py cleanup_webhooks --days=90
```

### **Retry Failed Deliveries**
```bash
python manage.py retry_failed_deliveries --webhook-id=1
```

---

## 📝 API Documentation

### **Base URL**
```
/v2/api/webhooks/
```

### **Endpoints**

#### Webhooks
- `GET /v2/api/webhooks/` - List webhooks
- `POST /v2/api/webhooks/` - Create webhook
- `GET /v2/api/webhooks/{id}/` - Get webhook details
- `PUT /v2/api/webhooks/{id}/` - Update webhook
- `DELETE /v2/api/webhooks/{id}/` - Delete webhook
- `POST /v2/api/webhooks/{id}/test/` - Test webhook
- `POST /v2/api/webhooks/{id}/regenerate_secret/` - Regenerate secret

#### Webhook Deliveries
- `GET /v2/api/webhook-deliveries/` - List deliveries
- `GET /v2/api/webhook-deliveries/{id}/` - Get delivery details

---

## 🎯 Implementation Checklist

- [ ] Create Webhook, WebhookEvent, WebhookDelivery models
- [ ] Implement WebhookService with retry logic
- [ ] Create Celery tasks for async delivery
- [ ] Implement signature verification
- [ ] Create API endpoints (WebhookViewSet, WebhookDeliveryViewSet)
- [ ] Add admin interface
- [ ] Implement event filtering
- [ ] Add rate limiting
- [ ] Create tests (models, services, views)
- [ ] Add monitoring and logging
- [ ] Implement cleanup tasks
- [ ] Create management commands
- [ ] Document event schemas
- [ ] Add integration examples

---

## 📖 Version History

- **v1.0** - Initial version with core webhook functionality

<!-- ===============================================================================
 END WEEBHOOKS.MD
 ================================================================================= -->

<!-- ===============================================================================
 START ECOMMERCE.MD
 ================================================================================= -->
<!-- ===============================================================================
 START ECOMMERCE.MD
================================================================================ -->
# 🎯 Ecommerce Module Rules

## 🎯 Ecommerce Module Purpose

This document defines strict development rules for the **ecommerce** module, providing unified product, cart, order, and fulfillment management for DFCMS stores.

### Scope
- Product and variant management
- Shopping cart and checkout
- Order processing and fulfillment
- Customer management
- Discount and coupon system
- Collection management
- Inventory tracking
- Payment integration
- Shipping and tax calculations

### Architecture Principles
- **Store-scoped**: All models must reference `stores.Store` explicitly
- **V2-only**: Clean implementation without legacy compatibility
- **Service layer**: Business logic centralized in `services.py`
- **Auto-logging**: Integration with the `logs` app for audit trails
- **Multi-tenant**: Strict data isolation between stores

### Directory Structure
```
apps/
├── public/                    # Public APIs (no authentication)
│   └── ecommerce/             # Public ecommerce APIs
│       ├── v2/               # Version 2 (Current Only)
│       │   ├── urls.py
│       │   ├── views.py
│       │   ├── serializers.py
│       │   ├── services.py
│       │   └── tests.py
│       ├── models/             # Shared models across versions
│       │   ├── __init__.py
│       │   ├── products.py      # Product, ProductVariant, ProductCategory
│       │   ├── cart.py         # Cart, CartItem
│       │   ├── orders.py        # Order, OrderItem
│       │   ├── customers.py    # Customer
│       │   ├── collections.py   # Collection, CollectionCondition
│       │   ├── coupons.py       # CouponCampaign, Coupon
│       │   ├── inventory.py    # Inventory, InventoryTransaction
│       │   └── payments.py     # PaymentMethod, Payment
│       ├── admin.py
│       ├── apps.py
│       └── migrations/
├── customer/                  # Customer APIs (customer authentication)
│   └── ecommerce/             # Customer ecommerce APIs
│       ├── v2/               # Version 2 (Current Only)
│       │   ├── urls.py
│       │   ├── views.py
│       │   ├── serializers.py
│       │   ├── services.py
│       │   └── tests.py
│       └── models/             # Same shared models
└── dashboard/                 # Dashboard APIs (admin authentication)
    └── ecommerce/             # Dashboard ecommerce APIs
        ├── v2/               # Version 2 (Current Only)
        │   ├── urls.py
        │   ├── views.py
        │   ├── serializers.py
        │   ├── services.py
        │   └── tests.py
        └── models/             # Same shared models
```

### 1.5 Integration Points
- **Media**: Product images, variant images, category images
- **Accounts**: Customer profiles, user management
- **Stores**: Multi-tenant store scoping
- **Logs**: Auto-logging for all ecommerce activities
- **Translations**: Product/content internationalization
- **SMTP**: Order confirmations, notifications

### 1.6 API Versioning
- **V1**: Not implemented (clean V2-only approach)
- **V2**: Current version with full feature set
- **Future**: V3 planned for breaking changes

### 1.7 Security Requirements
- Store isolation mandatory
- Input validation on all endpoints
- Rate limiting on public APIs
- PCI compliance for payment processing
- GDPR compliance for customer data

### 1.8 Performance Requirements
- Optimized database queries with proper indexing
- Caching strategies for product data
- Efficient cart operations
- Scalable inventory management

### 1.9 Testing Requirements
- 95% model coverage
- 90% API endpoint coverage
- 100% service layer coverage
- Integration tests for critical flows

---

## 2. Core Models

### 2.1 Model Inheritance
All ecommerce models must inherit from `TenantModel` for store scoping:

```python
from core.models import TenantModel

class Product(TenantModel):
    # Store-scoped product model
    pass
```
# Ecommerce Models

## 2. Core Models

### 2.1 Model Inheritance

All ecommerce models must use explicit `store` ForeignKey for store scoping:

```python
from django.db import models
```

### 2.2 Product Models

#### Product
```python
# apps/public/ecommerce/models/products.py
from django.db import models

class Product(models.Model):
    """
    Store-scoped product model with comprehensive e-commerce features
    """
    # Core Identification
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique_for_store=True)
    sku = models.CharField(max_length=100, unique=True)
    upc = models.CharField(max_length=12, blank=True, null=True, unique=True)

    # Descriptions
    description = models.TextField(blank=True)
    short_description = models.TextField(max_length=500, blank=True)

    # Pricing
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    compare_at_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Inventory
    track_inventory = models.BooleanField(default=True)
    inventory_quantity = models.IntegerField(default=0)
    allow_backorder = models.BooleanField(default=False)
    backorder_quantity = models.IntegerField(default=0, help_text="Quantity available for backorder")

    # Shipping
    requires_shipping = models.BooleanField(default=True)
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight in grams"
    )

    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    is_featured = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    # SEO
    seo_title = models.CharField(max_length=60, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    seo_keywords = models.CharField(max_length=255, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['store', 'status']),
            models.Index(fields=['store', 'is_available']),
            models.Index(fields=['store', 'is_featured']),
            models.Index(fields=['store', 'type']),
            models.Index(fields=['store', 'sku']),
            models.Index(fields=['store', 'status', 'is_available']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['store', 'sku'],
                name='unique_store_sku'
            ),
            models.UniqueConstraint(
                fields=['store', 'slug'],
                name='unique_store_slug'
            )
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure slug is unique
            queryset = self.__class__.objects.filter(
                store=self.store,
                slug__startswith=self.slug
            )
            if queryset.exists():
                self.slug = f"{self.slug}-{queryset.count() + 1}"
        super().save(*args, **kwargs)

    @property
    def is_in_stock(self):
        if not self.track_inventory:
            return True
        return self.inventory_quantity > 0

    @property
    def can_backorder(self):
        return self.allow_backorder and self.backorder_quantity > 0

    @property
    def inventory_status(self):
        """Get current inventory status"""
        if not self.is_available or self.status != 'active':
            return 'unavailable'
        if not self.track_inventory:
            return 'in_stock'
        if self.inventory_quantity > 0:
            return 'in_stock'
        if self.allow_backorder and self.backorder_quantity > 0:
            return 'available_for_backorder'
        return 'out_of_stock'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('product-detail', kwargs={'slug': self.slug})

    def get_price(self):
        """Get the current price, considering sales/discounts"""
        # Implementation for getting price with discounts
        return self.base_price

    def get_availability(self):
        """
        Get product availability status

        Note: This method is kept for backward compatibility.
        Consider using the inventory_status property instead.
        """
        return self.inventory_status

    def update_inventory(self, quantity, action='decrease'):
        """Update inventory levels"""
        if not self.track_inventory:
            return True

        if action == 'decrease':
            new_quantity = self.inventory_quantity - quantity
            if new_quantity < 0 and not self.allow_backorder:
                return False
            self.inventory_quantity = max(new_quantity, 0)
            if new_quantity < 0:
                self.backorder_quantity += abs(new_quantity)
        elif action == 'increase':
            self.inventory_quantity += quantity
        elif action == 'set':
            self.inventory_quantity = quantity

        self.save()
        return True

    # Media relationships
    primary_image = models.ForeignKey(
        'media.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_products'
    )

    # Relations
    categories = models.ManyToManyField(
        'Category',
        related_name='products',
        blank=True
    )
    collections = models.ManyToManyField(
        'Collection',
        related_name='products',
        blank=True
    )
    tags = models.ManyToManyField(
        'ProductTag',
        related_name='products',
        blank=True
    )

    # Digital product specific
    digital_file = models.FileField(
        upload_to='digital_products/%Y/%m/',
        null=True,
        blank=True
    )
    download_limit = models.PositiveIntegerField(
        default=3,
        help_text="Number of times the file can be downloaded"
    )
    download_expiry_days = models.PositiveIntegerField(
        default=30,
        help_text="Number of days the download link is valid"
    )

    # Inventory alerts
    low_stock_threshold = models.PositiveIntegerField(
        default=5,
        help_text="When to trigger low stock alerts"
    )

    # Advanced options
    requires_shipping_address = models.BooleanField(default=True)
    is_giftcard = models.BooleanField(default=False)
    giftcard_expiry_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of days until gift card expires"
    )

    # Type of product
    TYPE_CHOICES = [
        ('physical', 'Physical'),
        ('digital', 'Digital'),
        ('service', 'Service'),
        ('gift_card', 'Gift Card')
    ]
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='physical'
    )

    # Tax
    tax_class = models.ForeignKey(
        'TaxClass',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    seo_description = models.CharField(max_length=500, blank=True)

    # Media relationships
    featured_image = models.ForeignKey(
        'media.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='featured_products'
    )

    # Category relationships
    categories = models.ManyToManyField(
        'ProductCategory',
        blank=True,
        related_name='products'
    )

    class Meta:
        db_table = 'ecommerce_product'
        unique_together = [['store', 'slug'], ['store', 'sku']]
        indexes = [
            models.Index(fields=['store', 'status']),
            models.Index(fields=['store', 'featured']),
            models.Index(fields=['sku']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_current_price(self):
        """Get current price from variants or base price"""
        variant = self.variants.first()
        return variant.price if variant else self.base_price or 0

#### ProductVariant
```python
class ProductVariant(TenantModel):
    """
    Product variant with store scoping
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    barcode = models.CharField(max_length=50, blank=True)

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Inventory
    inventory_quantity = models.IntegerField(default=0)
    inventory_policy = models.CharField(max_length=20, choices=INVENTORY_POLICY_CHOICES, default='deny')

    # Physical attributes
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Variant options
    option1 = models.CharField(max_length=100, blank=True)
    option2 = models.CharField(max_length=100, blank=True)
    option3 = models.CharField(max_length=100, blank=True)

    # Position for ordering
    position = models.IntegerField(default=0)

    class Meta:
        db_table = 'ecommerce_product_variant'
        unique_together = [['store', 'sku'], ['product', 'sku']]
        indexes = [
            models.Index(fields=['store', 'product']),
            models.Index(fields=['product', 'position']),
            models.Index(fields=['sku']),
        ]
        ordering = ['position']
```

#### ProductCategory
```python
class ProductCategory(TenantModel):
    """
    Store-scoped product category with hierarchical structure
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)

    # Hierarchical structure
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    # Media
    image = models.ForeignKey(
        'media.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='category_images'
    )

    # SEO fields
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.CharField(max_length=500, blank=True)

    # Position and status
    position = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'ecommerce_product_category'
        unique_together = [['store', 'slug']]
        verbose_name_plural = 'Product Categories'
        indexes = [
            models.Index(fields=['store', 'parent']),
            models.Index(fields=['store', 'position']),
            models.Index(fields=['store', 'is_active']),
        ]
        ordering = ['position']

    def clean(self):
        if self.parent and self.parent.parent == self:
            raise ValidationError("Cannot create circular category reference")
```

### 2.2 Cart Models

#### Cart
```python
class Cart(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=CART_STATUS_CHOICES, default='active')
    currency = models.CharField(max_length=3, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['store', 'session_key']
        indexes = [
            models.Index(fields=['store', 'customer']),
            models.Index(fields=['store', 'session_key']),
            models.Index(fields=['status']),
        ]

    def get_item_count(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    def get_subtotal(self):
        return sum(item.get_total() for item in self.items.all())

    def get_tax(self):
        # Tax calculation logic
        return Decimal('0.00')

    def get_shipping(self):
        # Shipping calculation logic
        return Decimal('0.00')

    def get_total(self):
        return self.get_subtotal() + self.get_tax() + self.get_shipping()
```

#### CartItem
```python
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cart', 'product', 'variant']
        indexes = [
            models.Index(fields=['cart', 'product']),
            models.Index(fields=['cart', 'variant']),
        ]

    def clean(self):
        if self.variant and self.variant.product != self.product:
            raise ValidationError("Variant must belong to the specified product")

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def get_total(self):
        return self.total_price
```

### 2.3 Order Models

#### Order
```python
class Order(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    fulfillment_status = models.CharField(max_length=20, choices=FULFILLMENT_STATUS_CHOICES, default='unfulfilled')
    currency = models.CharField(max_length=3, default='USD')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    shipping = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Address fields
    billing_address = models.JSONField(default=dict)
    shipping_address = models.JSONField(default=dict)

    # Additional fields
    notes = models.TextField(blank=True)
    customer_notes = models.TextField(blank=True)
    tags = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['store', 'status']),
            models.Index(fields=['store', 'customer']),
            models.Index(fields=['order_number']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        random_str = ''.join(random.choices(string.digits, k=4))
        return f"ORD-{timestamp}-{random_str}"

    def calculate_totals(self):
        self.subtotal = sum(item.get_total() for item in self.items.all())
        self.tax = self.calculate_tax()
        self.shipping = self.calculate_shipping()
        self.discount = self.calculate_discount()
        self.total = self.subtotal + self.tax + self.shipping - self.discount

    def is_paid(self):
        return self.payment_status == 'paid'

    def is_fulfilled(self):
        return self.fulfillment_status == 'fulfilled'
```

#### OrderItem
```python
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['order', 'product']),
            models.Index(fields=['order', 'variant']),
        ]

    def get_total(self):
        return self.total_price
```

### 2.4 Customer Models

#### Customer
```python
class Customer(models.Model):
    user = models.OneToOneField(GlobalUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)

    # Marketing preferences
    email_marketing = models.BooleanField(default=True)
    sms_marketing = models.BooleanField(default=False)

    # Statistics
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_count = models.IntegerField(default=0)
    last_order_at = models.DateTimeField(null=True, blank=True)

    # Addresses
    default_billing_address = models.JSONField(default=dict)
    default_shipping_address = models.JSONField(default=dict)

    # Metadata
    tags = models.JSONField(default=list)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['total_spent']),
            models.Index(fields=['order_count']),
            models.Index(fields=['last_order_at']),
        ]

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def update_statistics(self):
        orders = Order.objects.filter(customer=self)
        self.order_count = orders.count()
        self.total_spent = orders.aggregate(total=models.Sum('total'))['total'] or 0
        last_order = orders.order_by('-created_at').first()
        self.last_order_at = last_order.created_at if last_order else None
        self.save()
```

### 2.3 Product Variants and Options

#### OptionType
```python
class OptionType(models.Model):
    """Product option types (e.g., Size, Color)"""
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    display_name = models.CharField(max_length=50)
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ['position']
        unique_together = ['store', 'name']
        indexes = [
            models.Index(fields=['store', 'position']),
        ]

class OptionValue(models.Model):
    """Values for product options (e.g., Red, Blue, Large, Small)"""
    option_type = models.ForeignKey(OptionType, on_delete=models.CASCADE, related_name='values')
    name = models.CharField(max_length=100)
    presentation = models.CharField(max_length=100)
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ['position']

class ProductVariant(models.Model):
    """Product variants for different options"""
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    sku = models.CharField(max_length=100, unique=True)
    barcode = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    inventory_quantity = models.IntegerField(default=0)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    requires_shipping = models.BooleanField(default=True)
    position = models.IntegerField(default=0)
    option_values = models.ManyToManyField(OptionValue, related_name='variants')

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f"{self.product.title} - {self.sku}"
```

### 2.4 Inventory Management

```python
class InventoryItem(models.Model):
    """Tracks individual inventory items for better stock control"""
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    sku = models.CharField(max_length=100, unique=True)
    product_variant = models.OneToOneField(
        ProductVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    quantity = models.IntegerField(default=0)
    committed = models.IntegerField(default=0)  # Reserved in carts/orders
    available = models.IntegerField(default=0)  # quantity - committed
    last_counted = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['store', 'sku']),
            models.Index(fields=['store', 'product_variant']),
        ]

    def update_available_quantity(self):
        """Update available quantity based on current stock and commitments"""
        self.available = max(0, self.quantity - self.committed)
        self.save(update_fields=['available', 'updated_at'])
        return self.available

class StockMovement(models.Model):
    """Tracks all inventory changes"""
    MOVEMENT_TYPES = [
        ('purchase', 'Purchase Order'),
        ('sale', 'Sale'),
        ('return', 'Return'),
        ('adjustment', 'Adjustment'),
        ('damaged', 'Damaged'),
        ('found', 'Found'),
        ('lost', 'Lost'),
    ]

    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='movements')
    quantity = models.IntegerField()
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    reference = models.CharField(max_length=100, blank=True)  # PO#, Order#, etc.
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['inventory_item', 'created_at']),
        ]
```

### 2.5 Collection Models

#### Collection
```python
class Collection(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ForeignKey('media.MediaFile', on_delete=models.SET_NULL, null=True, blank=True)
    is_smart = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.CharField(max_length=20, choices=SORT_ORDER_CHOICES, default='manual')
    created_by = models.ForeignKey(GlobalUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['store', 'slug']
        indexes = [
            models.Index(fields=['store', 'is_active']),
            models.Index(fields=['store', 'is_smart']),
        ]
```

#### CollectionCondition
```python
class CollectionCondition(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='conditions')
    field = models.CharField(max_length=50, choices=CONDITION_FIELD_CHOICES)
    operator = models.CharField(max_length=20, choices=CONDITION_OPERATOR_CHOICES)
    value = models.JSONField()
    position = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['collection', 'position']),
        ]
```

### 2.6 Coupon Models

#### CouponCampaign
```python
class CouponCampaign(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(GlobalUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['store', 'is_active']),
            models.Index(fields=['starts_at', 'ends_at']),
        ]
```

#### Coupon
```python
class Coupon(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    campaign = models.ForeignKey(CouponCampaign, on_delete=models.CASCADE, null=True, blank=True)
    code = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=20, choices=COUPON_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usage_limit = models.IntegerField(null=True, blank=True)
    usage_limit_per_customer = models.IntegerField(null=True, blank=True)
    used_count = models.IntegerField(default=0)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(GlobalUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['store', 'code']),
            models.Index(fields=['store', 'is_active']),
            models.Index(fields=['starts_at', 'ends_at']),
        ]

    def is_valid(self, customer=None, cart_total=0):
        now = timezone.now()

        if not self.is_active:
            return False, "Coupon is inactive"

        if now < self.starts_at:
            return False, "Coupon not yet active"

        if now > self.ends_at:
            return False, "Coupon has expired"

        if cart_total < self.minimum_order_amount:
            return False, f"Minimum order amount of {self.minimum_order_amount} required"

        if self.usage_limit and self.used_count >= self.usage_limit:
            return False, "Coupon usage limit reached"

        if customer and self.usage_limit_per_customer:
            customer_usage = Order.objects.filter(
                customer=customer,
                coupons__code=self.code
            ).count()
            if customer_usage >= self.usage_limit_per_customer:
                return False, "Customer usage limit reached"

        return True, "Valid"

    def apply_discount(self, cart_total):
        if self.type == 'fixed_amount':
            return min(self.value, cart_total)
        elif self.type == 'percentage':
            return cart_total * (self.value / 100)
        elif self.type == 'free_shipping':
            return 0  # Handled separately in shipping calculation
        return 0
```

### 2.7 Inventory Models

#### Inventory
```python
class Inventory(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    reserved = models.IntegerField(default=0)
    available = models.IntegerField(default=0)
    location = models.CharField(max_length=100, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['store', 'product', 'variant']
        indexes = [
            models.Index(fields=['store', 'product']),
            models.Index(fields=['store', 'variant']),
        ]

    def save(self, *args, **kwargs):
        self.available = self.quantity - self.reserved
        super().save(*args, **kwargs)

    def reserve(self, quantity):
        if self.available >= quantity:
            self.reserved += quantity
            self.save()
            return True
        return False

    def release(self, quantity):
        if self.reserved >= quantity:
            self.reserved -= quantity
            self.save()
            return True
        return False

    def deduct(self, quantity):
        if self.reserved >= quantity:
            self.reserved -= quantity
            self.quantity -= quantity
            self.save()
            return True
        return False
```

#### InventoryTransaction
```python
class InventoryTransaction(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(GlobalUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['inventory', 'type']),
            models.Index(fields=['created_at']),
        ]
```

### 2.8 Payment Models

#### PaymentMethod
```python
class PaymentMethod(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['store', 'is_active']),
        ]
```

#### Payment
```python
class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=255, blank=True)
    gateway_response = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['order', 'status']),
            models.Index(fields=['transaction_id']),
        ]
```
# Ecommerce Views and API Endpoints

## 3. ViewSets and API Endpoints

### 3.1 Base Classes

#### TenantViewSet
```python
# All ecommerce ViewSets must inherit from TenantViewSet
from core.viewsets import TenantViewSet
from core.permissions import IsStoreOwner, IsStoreStaff, IsStoreUser

class EcommerceViewSet(TenantViewSet):
    """
    Base ViewSet for all ecommerce endpoints with store scoping
    Follows main backend rules pattern
    """

    def get_queryset(self):
        """Filter queryset by store (inherited from TenantViewSet)"""
        return super().get_queryset()

    def perform_create(self, serializer):
        """Set store on create (inherited from TenantViewSet)"""
        return super().perform_create(serializer)
```

### 3.2 Product Views

#### ProductViewSet
```python
# apps/dashboard/ecommerce/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema

class ProductViewSet(TenantViewSet):
    """
    Product management endpoints for dashboard
    Follows main backend rules pattern
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    queryset = Product.objects.select_related('store').prefetch_related(
        'variants', 'categories', 'images'
    ).all()
    serializer_class = ProductSerializer
    filterset_fields = ['status', 'featured', 'categories']
    search_fields = ['title', 'description', 'sku']
    ordering_fields = ['title', 'created_at', 'updated_at']
    ordering = ['-created_at']

    @extend_schema(
        summary="Duplicate Product",
        description="Create a duplicate of existing product",
        responses={201: ProductSerializer}
    )
    def duplicate(self, request, pk=None):
        """Duplicate a product using service layer"""
        product = self.get_object()

        from services.product import ProductService
        new_product = ProductService.duplicate_product(product, request.user)

        serializer = self.get_serializer(new_product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def bulk_update_variants(self, request, pk=None):
        """Bulk update product variants"""
        product = self.get_object()
        variants_data = request.data.get('variants', [])

        for variant_data in variants_data:
            variant_id = variant_data.get('id')
            if variant_id:
                variant = product.variants.get(id=variant_id)
                for attr, value in variant_data.items():
                    if attr != 'id':
                        setattr(variant, attr, value)
                variant.save()

        return Response({'status': 'updated'})

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export products to CSV"""
        store = self.get_store()
        products = self.get_queryset()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'

        writer = csv.writer(response)
        writer.writerow(['Title', 'SKU', 'Price', 'Status', 'Created At'])

        for product in products:
            writer.writerow([
                product.title,
                product.sku,
                product.variants.first().price if product.variants.exists() else '',
                product.status,
                product.created_at
            ])

        return response
```

#### ProductVariantViewSet
```python
class ProductVariantViewSet(StoreScopedViewSet):
    """
    Product variant management endpoints
    """
    queryset = ProductVariant.objects.select_related('product').all()
    serializer_class = ProductVariantSerializer
    filterset_fields = ['product', 'inventory_policy']
    search_fields = ['title', 'sku', 'barcode']
    ordering_fields = ['position', 'price', 'created_at']
    ordering = ['position']

    def get_queryset(self):
        store = self.get_store()
        return super().get_queryset().filter(product__store=store)

    @action(detail=True, methods=['post'])
    def adjust_inventory(self, request, pk=None):
        """Adjust variant inventory"""
        variant = self.get_object()
        quantity = request.data.get('quantity', 0)
        transaction_type = request.data.get('type', 'adjustment')
        notes = request.data.get('notes', '')

        inventory, created = Inventory.objects.get_or_create(
            store=variant.product.store,
            product=variant.product,
            variant=variant,
            defaults={'quantity': 0}
        )

        if transaction_type == 'add':
            inventory.quantity += quantity
        elif transaction_type == 'subtract':
            inventory.quantity -= quantity
        else:
            inventory.quantity = quantity

        inventory.save()

        # Create transaction record
        InventoryTransaction.objects.create(
            inventory=inventory,
            type=transaction_type,
            quantity=quantity,
            notes=notes,
            created_by=request.user
        )

        return Response({'quantity': inventory.quantity})
```

#### ProductCategoryViewSet
```python
class ProductCategoryViewSet(StoreScopedViewSet):
    """
    Product category management endpoints
    """
    queryset = ProductCategory.objects.select_related('parent', 'image').all()
    serializer_class = ProductCategorySerializer
    filterset_fields = ['parent', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'position', 'created_at']
    ordering = ['position']

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get category tree structure"""
        store = self.get_store()
        categories = self.get_queryset().filter(store=store, is_active=True)

        def build_tree(parent=None):
            children = categories.filter(parent=parent)
            return [
                {
                    'id': cat.id,
                    'name': cat.name,
                    'slug': cat.slug,
                    'children': build_tree(cat)
                }
                for cat in children
            ]

        tree = build_tree()
        return Response(tree)
```

### 3.3 Public API Views

#### PublicProductViewSet
```python
# apps/public/ecommerce/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import AllowAny

class PublicProductViewSet(TenantViewSet):
    """
    Public product catalog endpoints
    No authentication required
    """
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    queryset = Product.objects.filter(status='published').select_related('store').prefetch_related(
        'variants', 'categories', 'images'
    )
    serializer_class = PublicProductSerializer
    filterset_fields = ['status', 'featured', 'categories']
    search_fields = ['title', 'description', 'sku']
    ordering_fields = ['title', 'created_at']
    ordering = ['-created_at']

    @extend_schema(
        summary="List Public Products",
        description="Get paginated list of published products",
        responses={200: PublicProductSerializer}
    )
    def list(self, request, *args, **kwargs):
        """List published products"""
        return super().list(request, *args, **kwargs)
### 3.4 Customer API Views

#### CustomerCartViewSet
```python
# apps/customer/ecommerce/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreUser

class CustomerCartViewSet(TenantViewSet):
    """
    Customer cart management endpoints
    Customer authentication required
    """
    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = CartSerializer

    def get_queryset(self):
        """Get cart for authenticated customer"""
        from services.cart import CartService
        return CartService.get_cart_for_customer(self.request.user, self.request.store)

    @extend_schema(
        summary="Get Customer Cart",
        description="Get current customer's shopping cart",
        responses={200: CartSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        """Get or create cart for customer"""
        cart = self.get_queryset()
        if not cart:
            from services.cart import CartService
            cart = CartService.create_cart_for_customer(self.request.user, self.request.store)

        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    def get_store(self):
        """Get store from request"""
        if hasattr(self.request, 'store'):
            return self.request.store
        raise ValidationError("Store not found")

    ### 3.5 URL Structure

#### Main Ecommerce URLs
```python
# apps/public/ecommerce/urls.py
from django.urls import include, path

app_name = 'ecommerce'

urlpatterns = [
    path('v2/', include('apps.public.ecommerce.v2.urls')),
]

# apps/customer/ecommerce/urls.py
urlpatterns = [
    path('v2/', include('apps.customer.ecommerce.v2.urls')),
]

# apps/dashboard/ecommerce/urls.py
urlpatterns = [
    path('v2/', include('apps.dashboard.ecommerce.v2.urls')),
]

# Main project URLs
# config/urls.py
urlpatterns = [
    path('v2/api/public/ecommerce/', include('apps.public.ecommerce.urls')),
    path('v2/api/customer/ecommerce/', include('apps.customer.ecommerce.urls')),
    path('v2/api/dashboard/ecommerce/', include('apps.dashboard.ecommerce.urls')),
]
            'shipping': str(cart.get_shipping()),
            'total': str(cart.get_total()),
            'currency': cart.currency
        })
```

### 3.4 Order Views

#### OrderViewSet
```python
# apps/dashboard/ecommerce/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema

class OrderViewSet(TenantViewSet):
    """
    Order management endpoints for dashboard
    Follows main backend rules pattern
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    queryset = Order.objects.select_related(
        'customer', 'store'
    ).prefetch_related('items', 'payments').all()
    serializer_class = OrderSerializer
    filterset_fields = ['status', 'payment_status', 'fulfillment_status']
    search_fields = ['order_number', 'customer__email']
    ordering_fields = ['created_at', 'total', 'order_number']
    ordering = ['-created_at']

    @extend_schema(
        summary="Create Order from Cart",
        description="Convert shopping cart to order",
        request=OrderCreateSerializer,
        responses={201: OrderSerializer}
    )
    @action(detail=False, methods=['post'])
    def create_from_cart(self, request):
        """Create order from cart using service layer"""
        from services.order import OrderService

        try:
            order = OrderService.create_order_from_cart(
                request.user,
                request.store,
                request.data
            )

            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Update Order Status",
        description="Update order status with validation",
        request=OrderStatusSerializer,
        responses={200: OrderSerializer}
    )
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update order status using service layer"""
        order = self.get_object()
        new_status = request.data.get('status')

        from services.order import OrderService
        try:
            updated_order = OrderService.update_order_status(
                order, new_status, request.user
            )

            serializer = self.get_serializer(updated_order)
            return Response(serializer.data)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Create Payment",
        description="Process payment for order",
        request=PaymentSerializer,
        responses={201: PaymentSerializer}
    )
    @action(detail=True, methods=['post'])
    def create_payment(self, request, pk=None):
        """Create payment for order using service layer"""
        order = self.get_object()

        from services.payment import PaymentService
        try:
            payment = PaymentService.process_payment(
                order, request.data, request.user
            )

            serializer = PaymentSerializer(payment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Generate Invoice",
        description="Generate PDF invoice for order",
        responses={200: 'application/pdf'}
    )
    @action(detail=True, methods=['get'])
    def invoice(self, request, pk=None):
        """Generate order invoice PDF"""
        order = self.get_object()

        from services.order import OrderService
        pdf_buffer = OrderService.generate_invoice_pdf(order)

        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_number}.pdf"'

        return response
```

### 3.5 Customer Views

#### CustomerViewSet
```python
# apps/dashboard/ecommerce/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema

class CustomerViewSet(TenantViewSet):
    """
    Customer management endpoints for dashboard
    Follows main backend rules pattern
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    queryset = Customer.objects.select_related('user').all()
    serializer_class = CustomerSerializer
    filterset_fields = ['email_marketing', 'sms_marketing']
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ['created_at', 'total_spent', 'order_count']
    ordering = ['-created_at']

    @extend_schema(
        summary="List Customers",
        description="Get paginated list of store customers",
        responses={200: CustomerSerializer}
    )
    def list(self, request, *args, **kwargs):
        """List customers with filtering and search"""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Get Customer Orders",
        description="Get orders for specific customer",
        responses={200: OrderSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """Get orders for specific customer"""
        customer = self.get_object()

        from services.customer import CustomerService
        orders = CustomerService.get_customer_orders(customer, request.store)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
```

### 3.6 Collection Views

#### CollectionViewSet
```python
# apps/dashboard/ecommerce/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema

class CollectionViewSet(TenantViewSet):
    """
    Collection management endpoints for dashboard
    Follows main backend rules pattern
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    queryset = Collection.objects.select_related('image').prefetch_related('conditions').all()
    serializer_class = CollectionSerializer
    filterset_fields = ['is_smart', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at']
    ordering = ['title']

    @extend_schema(
        summary="List Collections",
        description="Get paginated list of store collections",
        responses={200: CollectionSerializer}
    )
    def list(self, request, *args, **kwargs):
        """List collections with filtering and search"""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Get Collection Products",
        description="Get products in collection",
        responses={200: ProductSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get products in collection using service layer"""
        collection = self.get_object()

        from services.collection import CollectionService
        products = CollectionService.get_products_for_collection(collection)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Add Products to Collection",
        description="Add products to manual collection",
        request=CollectionProductSerializer,
        responses={200: dict}
    )
    @action(detail=True, methods=['post'])
    def add_products(self, request, pk=None):
        """Add products to manual collection using service layer"""
        collection = self.get_object()

        from services.collection import CollectionService
        try:
            CollectionService.add_products_to_collection(
                collection, request.data.get('product_ids', [])
            )

            return Response({'status': 'products_added'})

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Remove Products from Collection",
        description="Remove products from manual collection",
        request=CollectionProductSerializer,
        responses={200: dict}
    )
    @action(detail=True, methods=['post'])
    def remove_products(self, request, pk=None):
        """Remove products from manual collection using service layer"""
        collection = self.get_object()

        from services.collection import CollectionService
        try:
            CollectionService.remove_products_from_collection(
                collection, request.data.get('product_ids', [])
            )

            return Response({'status': 'products_removed'})

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

### 3.7 Coupon Views

#### CouponViewSet
```python
# apps/dashboard/ecommerce/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema

class CouponViewSet(TenantViewSet):
    """
    Coupon management endpoints for dashboard
    Follows main backend rules pattern
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    queryset = Coupon.objects.select_related('campaign').all()
    serializer_class = CouponSerializer
    filterset_fields = ['type', 'is_active', 'campaign']
    search_fields = ['code', 'name']
    ordering_fields = ['created_at', 'used_count']
    ordering = ['-created_at']

    @extend_schema(
        summary="Validate Coupon",
        description="Validate coupon code for cart",
        request=CouponValidateSerializer,
        responses={200: dict}
    )
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """Validate coupon code using service layer"""
        from services.coupon import CouponService

        try:
            result = CouponService.validate_coupon(
                request.data.get('code'),
                request.data.get('cart_total', 0),
                request.user,
                request.store
            )

            return Response(result)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Generate Coupon Codes",
        description="Generate multiple coupon codes",
        request=CouponGenerateSerializer,
        responses={200: dict}
    )
    @action(detail=True, methods=['post'])
    def generate_codes(self, request, pk=None):
        """Generate multiple coupon codes using service layer"""
        coupon = self.get_object()

        from services.coupon import CouponService
        try:
            codes = CouponService.generate_bulk_coupons(
                coupon,
                request.data.get('count', 1),
                request.data.get('prefix', ''),
                request.user
            )

            return Response({'codes': codes})

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
```

### 3.8 Public API Views

#### PublicProductViewSet
```python
class PublicProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public product catalog endpoints
    """
    serializer_class = PublicProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'categories', 'featured']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at', 'price']
    ordering = ['-created_at']

    def get_queryset(self):
        store = self.get_store()
        return Product.objects.filter(
            store=store,
            status='published'
        ).select_related('store').prefetch_related(
            'variants', 'categories', 'images'
        )

    def get_store(self):
        """Get store from subdomain or header"""
        host = self.request.get_host()
        subdomain = host.split('.')[0] if '.' in host else None

        if subdomain:
            try:
                return Store.objects.get(subdomain=subdomain, is_active=True)
            except Store.DoesNotExist:
                return Store.objects.filter(is_default=True, is_active=True).first()

        # Fallback to default store
        return Store.objects.filter(is_default=True, is_active=True).first()

    @action(detail=True, methods=['get'])
    def variants(self, request, pk=None):
        """Get product variants"""
        product = self.get_object()
        variants = product.variants.all()
        serializer = PublicProductVariantSerializer(variants, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        """Get related products"""
        product = self.get_object()

        # Get products from same categories
        category_ids = product.categories.values_list('id', flat=True)
        related = Product.objects.filter(
            store=product.store,
            status='published',
            categories__in=category_ids
        ).exclude(id=product.id).distinct()[:8]

        serializer = self.get_serializer(related, many=True)
        return Response(serializer.data)
```

### 3.8 URL Structure

#### Main Ecommerce URLs
```python
# apps/public/ecommerce/urls.py
from django.urls import include, path

app_name = 'ecommerce'

urlpatterns = [
    path('v2/', include('apps.public.ecommerce.v2.urls')),
]

# apps/customer/ecommerce/urls.py
urlpatterns = [
    path('v2/', include('apps.customer.ecommerce.v2.urls')),
]

# apps/dashboard/ecommerce/urls.py
urlpatterns = [
    path('v2/', include('apps.dashboard.ecommerce.v2.urls')),
]

# Main project URLs
# config/urls.py
urlpatterns = [
    path('v2/api/public/ecommerce/', include('apps.public.ecommerce.urls')),
    path('v2/api/customer/ecommerce/', include('apps.customer.ecommerce.urls')),
    path('v2/api/dashboard/ecommerce/', include('apps.dashboard.ecommerce.urls')),
]
```

#### Individual App URLs
```python
# apps/public/ecommerce/v2/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PublicProductViewSet

router = DefaultRouter()
router.register(r'products', PublicProductViewSet, basename='public-products')

urlpatterns = [
    path('', include(router.urls)),
]

# apps/customer/ecommerce/v2/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomerCartViewSet

router = DefaultRouter()
router.register(r'cart', CustomerCartViewSet, basename='customer-cart')

urlpatterns = [
    path('', include(router.urls)),
]

# apps/dashboard/ecommerce/v2/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import (
    ProductViewSet, OrderViewSet, CustomerViewSet,
    CollectionViewSet, CouponViewSet
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='dashboard-products')
router.register(r'orders', OrderViewSet, basename='dashboard-orders')
router.register(r'customers', CustomerViewSet, basename='dashboard-customers')
router.register(r'collections', CollectionViewSet, basename='dashboard-collections')
router.register(r'coupons', CouponViewSet, basename='dashboard-coupons')

# Nested routes
products_router = routers.NestedDefaultRouter(router, r'products', lookup='product')
products_router.register(r'images', ProductImageViewSet, basename='product-images')
products_router.register(r'variants', ProductVariantViewSet, basename='product-variants')

orders_router = routers.NestedDefaultRouter(router, r'orders', lookup='order')
orders_router.register(r'items', OrderItemViewSet, basename='order-items')
orders_router.register(r'payments', PaymentViewSet, basename='order-payments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(products_router.urls)),
    path('', include(orders_router.urls)),
]
# Ecommerce Services

## 4. Service Layer

### 4.1 Product Services

#### ProductService
```python
class ProductService:
    """Business logic for product management"""

    @staticmethod
    def create_product(store, user, data):
        """Create new product with variants and categories"""
        product = Product.objects.create(
            store=store,
            title=data['title'],
            slug=data['slug'],
            description=data.get('description', ''),
            short_description=data.get('short_description', ''),
            sku=data['sku'],
            barcode=data.get('barcode', ''),
            track_inventory=data.get('track_inventory', True),
            allow_backorder=data.get('allow_backorder', False),
            requires_shipping=data.get('requires_shipping', True),
            weight=data.get('weight'),
            status=data.get('status', 'draft'),
            featured=data.get('featured', False),
            seo_title=data.get('seo_title', ''),
            seo_description=data.get('seo_description', ''),
            created_by=user
        )

        # Create variants
        if 'variants' in data:
            for variant_data in data['variants']:
                ProductVariant.objects.create(
                    product=product,
                    title=variant_data['title'],
                    sku=variant_data['sku'],
                    barcode=variant_data.get('barcode', ''),
                    price=variant_data['price'],
                    compare_at_price=variant_data.get('compare_at_price'),
                    cost_price=variant_data.get('cost_price'),
                    weight=variant_data.get('weight'),
                    inventory_quantity=variant_data.get('inventory_quantity', 0),
                    inventory_policy=variant_data.get('inventory_policy', 'deny'),
                    requires_shipping=variant_data.get('requires_shipping', True),
                    taxable=variant_data.get('taxable', True),
                    position=variant_data.get('position', 0),
                    option1=variant_data.get('option1', ''),
                    option2=variant_data.get('option2', ''),
                    option3=variant_data.get('option3', '')
                )

        # Add categories
        if 'category_ids' in data:
            product.categories.set(data['category_ids'])

        # Create inventory records
        for variant in product.variants.all():
            Inventory.objects.get_or_create(
                store=store,
                product=product,
                variant=variant,
                defaults={'quantity': variant.inventory_quantity}
            )

        # Log creation
        log_event_async(
            user=user,
            store=store,
            action='product_created',
            object_type='product',
            object_id=product.id,
            details={'title': product.title, 'sku': product.sku}
        )

        return product

    @staticmethod
    def update_product(product, user, data):
        """Update product and related data"""
        old_status = product.status

        # Update product fields
        for field, value in data.items():
            if field not in ['variants', 'category_ids']:
                setattr(product, field, value)

        product.save()

        # Update variants
        if 'variants' in data:
            for variant_data in data['variants']:
                variant_id = variant_data.get('id')
                if variant_id:
                    variant = product.variants.get(id=variant_id)
                    for field, value in variant_data.items():
                        if field != 'id':
                            setattr(variant, field, value)
                    variant.save()
                else:
                    # Create new variant
                    ProductVariant.objects.create(
                        product=product,
                        **variant_data
                    )

        # Update categories
        if 'category_ids' in data:
            product.categories.set(data['category_ids'])

        # Log status change
        if 'status' in data and old_status != data['status']:
            log_event_async(
                user=user,
                store=product.store,
                action='product_status_updated',
                object_type='product',
                object_id=product.id,
                details={
                    'old_status': old_status,
                    'new_status': data['status']
                }
            )

        return product

    @staticmethod
    def duplicate_product(product, user):
        """Duplicate product with variants"""
        new_product = Product.objects.create(
            store=product.store,
            title=f"{product.title} (Copy)",
            slug=f"{product.slug}-copy-{int(time.time())}",
            description=product.description,
            short_description=product.short_description,
            sku=f"{product.sku}-COPY",
            barcode=product.barcode,
            track_inventory=product.track_inventory,
            allow_backorder=product.allow_backorder,
            requires_shipping=product.requires_shipping,
            weight=product.weight,
            status='draft',
            featured=False,
            seo_title=product.seo_title,
            seo_description=product.seo_description,
            created_by=user
        )

        # Duplicate variants
        for variant in product.variants.all():
            ProductVariant.objects.create(
                product=new_product,
                title=variant.title,
                sku=f"{variant.sku}-COPY",
                barcode=variant.barcode,
                price=variant.price,
                compare_at_price=variant.compare_at_price,
                cost_price=variant.cost_price,
                weight=variant.weight,
                inventory_quantity=0,
                inventory_policy=variant.inventory_policy,
                requires_shipping=variant.requires_shipping,
                taxable=variant.taxable,
                position=variant.position,
                option1=variant.option1,
                option2=variant.option2,
                option3=variant.option3
            )

        # Copy categories
        new_product.categories.set(product.categories.all())

        # Log duplication
        log_event_async(
            user=user,
            store=product.store,
            action='product_duplicated',
            object_type='product',
            object_id=new_product.id,
            details={
                'original_product_id': product.id,
                'original_title': product.title
            }
        )

        return new_product

    @staticmethod
    def delete_product(product, user):
        """Soft delete product"""
        product.status = 'deleted'
        product.save()

        # Log deletion
        log_event_async(
            user=user,
            store=product.store,
            action='product_deleted',
            object_type='product',
            object_id=product.id,
            details={'title': product.title}
        )
```

### 4.2 Cart Services

#### CartService
```python
class CartService:
    """Business logic for shopping cart management"""

    @staticmethod
    def get_cart(store, user=None, session_key=None):
        """Get or create cart for user or session"""
        if user and hasattr(user, 'customer'):
            customer = user.customer
            cart, created = Cart.objects.get_or_create(
                store=store,
                customer=customer,
                defaults={'status': 'active'}
            )
        elif session_key:
            cart, created = Cart.objects.get_or_create(
                store=store,
                session_key=session_key,
                defaults={'status': 'active'}
            )
        else:
            cart = None

        return cart

    @staticmethod
    def add_item(cart, product, variant=None, quantity=1):
        """Add item to cart with inventory check"""
        if variant:
            inventory = Inventory.objects.filter(
                store=cart.store,
                product=product,
                variant=variant
            ).first()
        else:
            inventory = Inventory.objects.filter(
                store=cart.store,
                product=product,
                variant__isnull=True
            ).first()

        # Check inventory availability
        if inventory and inventory.available < quantity:
            raise ValidationError(f"Only {inventory.available} items available")

        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={
                'quantity': quantity,
                'unit_price': variant.price if variant else product.variants.first().price
            }
        )

        if not created:
            new_quantity = cart_item.quantity + quantity

            # Check inventory again for additional quantity
            if inventory and inventory.available < new_quantity:
                raise ValidationError(f"Only {inventory.available} items available")

            cart_item.quantity = new_quantity
            cart_item.save()

        # Reserve inventory
        if inventory:
            inventory.reserve(cart_item.quantity)

        return cart_item

    @staticmethod
    def update_item_quantity(cart_item, quantity):
        """Update cart item quantity with inventory check"""
        if quantity <= 0:
            # Remove item and release inventory
            inventory = Inventory.objects.filter(
                store=cart_item.cart.store,
                product=cart_item.product,
                variant=cart_item.variant
            ).first()

            if inventory:
                inventory.release(cart_item.quantity)

            cart_item.delete()
            return True

        # Check inventory availability
        inventory = Inventory.objects.filter(
            store=cart_item.cart.store,
            product=cart_item.product,
            variant=cart_item.variant
        ).first()

        if inventory and inventory.available < quantity:
            raise ValidationError(f"Only {inventory.available} items available")

        # Update quantity and adjust reservation
        if inventory:
            inventory.release(cart_item.quantity)
            inventory.reserve(quantity)

        cart_item.quantity = quantity
        cart_item.save()

        return cart_item

    @staticmethod
    def remove_item(cart_item):
        """Remove item from cart and release inventory"""
        inventory = Inventory.objects.filter(
            store=cart_item.cart.store,
            product=cart_item.product,
            variant=cart_item.variant
        ).first()

        if inventory:
            inventory.release(cart_item.quantity)

        cart_item.delete()

    @staticmethod
    def clear_cart(cart):
        """Clear all items from cart and release inventory"""
        for item in cart.items.all():
            inventory = Inventory.objects.filter(
                store=cart.store,
                product=item.product,
                variant=item.variant
            ).first()

            if inventory:
                inventory.release(item.quantity)

        cart.items.all().delete()

    @staticmethod
    def convert_to_order(cart, billing_address, shipping_address, customer_notes=''):
        """Convert cart to order"""
        if not cart.items.exists():
            raise ValidationError("Cannot create order from empty cart")

        # Create order
        order = Order.objects.create(
            store=cart.store,
            customer=cart.customer,
            cart=cart,
            billing_address=billing_address,
            shipping_address=shipping_address,
            customer_notes=customer_notes,
            currency=cart.currency
        )

        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                title=cart_item.product.title,
                sku=cart_item.variant.sku if cart_item.variant else cart_item.product.sku,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                total_price=cart_item.get_total()
            )

        # Calculate totals
        order.calculate_totals()
        order.save()

        # Reserve inventory for order
        for cart_item in cart.items.all():
            inventory = Inventory.objects.filter(
                store=cart.store,
                product=cart_item.product,
                variant=cart_item.variant
            ).first()

            if inventory:
                inventory.reserve(cart_item.quantity)

        # Update cart status
        cart.status = 'converted'
        cart.save()

        return order
```

### 4.3 Order Services

#### OrderService
```python
class OrderService:
    """Business logic for order management"""

    @staticmethod
    def create_order_from_cart(cart, billing_address, shipping_address, customer_notes=''):
        """Create order from cart"""
        return CartService.convert_to_order(
            cart, billing_address, shipping_address, customer_notes
        )

    @staticmethod
    def update_order_status(order, new_status, user=None):
        """Update order status with validation"""
        old_status = order.status

        # Validate status transition
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['processing', 'cancelled'],
            'processing': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'cancelled'],
            'delivered': [],
            'cancelled': []
        }

        if new_status not in valid_transitions.get(old_status, []):
            raise ValidationError(f"Cannot transition from {old_status} to {new_status}")

        order.status = new_status
        order.save()

        # Handle inventory based on status
        if new_status == 'cancelled':
            OrderService.release_inventory(order)
        elif new_status == 'shipped':
            OrderService.deduct_inventory(order)

        # Log status change
        log_event_async(
            user=user,
            store=order.store,
            action='order_status_updated',
            object_type='order',
            object_id=order.id,
            details={
                'old_status': old_status,
                'new_status': new_status,
                'order_number': order.order_number
            }
        )

        # Send notifications
        if new_status in ['confirmed', 'shipped', 'delivered', 'cancelled']:
            send_order_status_email.delay(order.id, new_status)

        return order

    @staticmethod
    def release_inventory(order):
        """Release reserved inventory for cancelled order"""
        for order_item in order.items.all():
            inventory = Inventory.objects.filter(
                store=order.store,
                product=order_item.product,
                variant=order_item.variant
            ).first()

            if inventory:
                inventory.release(order_item.quantity)

    @staticmethod
    def deduct_inventory(order):
        """Deduct inventory for shipped order"""
        for order_item in order.items.all():
            inventory = Inventory.objects.filter(
                store=order.store,
                product=order_item.product,
                variant=order_item.variant
            ).first()

            if inventory:
                inventory.deduct(order_item.quantity)

    @staticmethod
    def process_payment(order, payment_method, payment_data):
        """Process payment for order"""
        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=order.total
        )

        # Process based on payment method
        if payment_method.type == 'stripe':
            result = process_stripe_payment(payment, payment_data)
        elif payment_method.type == 'paypal':
            result = process_paypal_payment(payment, payment_data)
        elif payment_method.type == 'cash_on_delivery':
            result = {'status': 'pending'}
        else:
            result = {'status': 'failed', 'error': 'Unsupported payment method'}

        payment.status = result.get('status', 'failed')
        payment.transaction_id = result.get('transaction_id', '')
        payment.gateway_response = result
        payment.save()

        # Update order payment status
        if payment.status == 'completed':
            order.payment_status = 'paid'
            order.save()
        elif payment.status == 'failed':
            order.payment_status = 'failed'
            order.save()

        # Log payment
        log_event_async(
            user=None,
            store=order.store,
            action='payment_processed',
            object_type='payment',
            object_id=payment.id,
            details={
                'order_id': order.id,
                'amount': str(payment.amount),
                'status': payment.status,
                'method': payment_method.type
            }
        )

        return payment

    @staticmethod
    def calculate_shipping(order, shipping_method=None):
        """Calculate shipping cost for order"""
        if not shipping_method:
            # Get default shipping method
            shipping_method = ShippingMethod.objects.filter(
                store=order.store,
                is_active=True
            ).first()

        if not shipping_method:
            return Decimal('0.00')

        # Calculate based on shipping method rules
        if shipping_method.type == 'flat_rate':
            return shipping_method.rate
        elif shipping_method.type == 'weight_based':
            total_weight = sum(
                item.variant.weight or 0 for item in order.items.all()
            )
            return total_weight * shipping_method.rate_per_weight
        elif shipping_method.type == 'price_based':
            return order.subtotal * (shipping_method.rate_percentage / 100)

        return Decimal('0.00')

    @staticmethod
    def calculate_tax(order):
        """Calculate tax for order"""
        # Get tax rates for store location
        tax_rates = TaxRate.objects.filter(
            store=order.store,
            is_active=True
        )

        total_tax = Decimal('0.00')

        for tax_rate in tax_rates:
            if tax_rate.applies_to_shipping:
                taxable_amount = order.subtotal + order.shipping
            else:
                taxable_amount = order.subtotal

            tax_amount = taxable_amount * (tax_rate.rate / 100)
            total_tax += tax_amount

        return total_tax
```

### 4.4 Customer Services

#### CustomerService
```python
class CustomerService:
    """Business logic for customer management"""

    @staticmethod
    def create_customer(user, data):
        """Create customer profile for user"""
        customer = Customer.objects.create(
            user=user,
            first_name=data.get('first_name', user.first_name),
            last_name=data.get('last_name', user.last_name),
            email=data.get('email', user.email),
            phone=data.get('phone', ''),
            date_of_birth=data.get('date_of_birth'),
            gender=data.get('gender', ''),
            email_marketing=data.get('email_marketing', True),
            sms_marketing=data.get('sms_marketing', False),
            default_billing_address=data.get('billing_address', {}),
            default_shipping_address=data.get('shipping_address', {})
        )

        # Log customer creation
        log_event_async(
            user=user,
            store=None,  # Global customer
            action='customer_created',
            object_type='customer',
            object_id=customer.id,
            details={'email': customer.email}
        )

        return customer

    @staticmethod
    def update_customer(customer, data):
        """Update customer profile"""
        old_email = customer.email

        for field, value in data.items():
            setattr(customer, field, value)

        customer.save()

        # Log email change
        if 'email' in data and old_email != data['email']:
            log_event_async(
                user=customer.user,
                store=None,
                action='customer_email_updated',
                object_type='customer',
                object_id=customer.id,
                details={'old_email': old_email, 'new_email': customer.email}
            )

        return customer

    @staticmethod
    def merge_customers(target_customer, source_customer):
        """Merge source customer into target customer"""
        # Merge orders
        Order.objects.filter(customer=source_customer).update(customer=target_customer)

        # Merge carts
        Cart.objects.filter(customer=source_customer).update(customer=target_customer)

        # Merge addresses
        if not target_customer.default_billing_address:
            target_customer.default_billing_address = source_customer.default_billing_address

        if not target_customer.default_shipping_address:
            target_customer.default_shipping_address = source_customer.default_shipping_address

        # Update statistics
        target_customer.update_statistics()

        # Log merge
        log_event_async(
            user=target_customer.user,
            store=None,
            action='customers_merged',
            object_type='customer',
            object_id=target_customer.id,
            details={
                'source_customer_id': source_customer.id,
                'source_email': source_customer.email
            }
        )

        # Delete source customer
        source_customer.delete()

        return target_customer

    @staticmethod
    def update_customer_statistics(customer):
        """Update customer order statistics"""
        orders = Order.objects.filter(customer=customer)
        customer.order_count = orders.count()
        customer.total_spent = orders.aggregate(
            total=models.Sum('total')
        )['total'] or 0
        last_order = orders.order_by('-created_at').first()
        customer.last_order_at = last_order.created_at if last_order else None
        customer.save()
```

### 4.5 Collection Services

#### CollectionService
```python
class CollectionService:
    """Business logic for collection management"""

    @staticmethod
    def create_collection(store, user, data):
        """Create new collection"""
        collection = Collection.objects.create(
            store=store,
            title=data['title'],
            slug=data['slug'],
            description=data.get('description', ''),
            is_smart=data.get('is_smart', False),
            is_active=data.get('is_active', True),
            sort_order=data.get('sort_order', 'manual'),
            created_by=user
        )

        # Add image if provided
        if 'image_id' in data:
            collection.image_id = data['image_id']
            collection.save()

        # Add conditions for smart collections
        if collection.is_smart and 'conditions' in data:
            for condition_data in data['conditions']:
                CollectionCondition.objects.create(
                    collection=collection,
                    field=condition_data['field'],
                    operator=condition_data['operator'],
                    value=condition_data['value'],
                    position=condition_data.get('position', 0)
                )

        # Add products for manual collections
        if not collection.is_smart and 'product_ids' in data:
            products = Product.objects.filter(
                id__in=data['product_ids'],
                store=store
            )
            collection.products.add(*products)

        # Log creation
        log_event_async(
            user=user,
            store=store,
            action='collection_created',
            object_type='collection',
            object_id=collection.id,
            details={'title': collection.title, 'is_smart': collection.is_smart}
        )

        return collection

    @staticmethod
    def get_smart_products(collection):
        """Get products for smart collection based on conditions"""
        queryset = Product.objects.filter(store=collection.store, status='published')

        for condition in collection.conditions.all():
            if condition.field == 'title':
                if condition.operator == 'contains':
                    queryset = queryset.filter(title__icontains=condition.value)
                elif condition.operator == 'equals':
                    queryset = queryset.filter(title__iexact=condition.value)
                elif condition.operator == 'starts_with':
                    queryset = queryset.filter(title__istartswith=condition.value)

            elif condition.field == 'price':
                if condition.operator == 'greater_than':
                    queryset = queryset.filter(variants__price__gt=condition.value)
                elif condition.operator == 'less_than':
                    queryset = queryset.filter(variants__price__lt=condition.value)
                elif condition.operator == 'between':
                    queryset = queryset.filter(
                        variants__price__gte=condition.value[0],
                        variants__price__lte=condition.value[1]
                    )

            elif condition.field == 'category':
                queryset = queryset.filter(categories__id=condition.value)

            elif condition.field == 'tag':
                queryset = queryset.filter(tags__contains=condition.value)

        # Apply sorting
        if collection.sort_order == 'price_low_high':
            queryset = queryset.order_by('variants__price')
        elif collection.sort_order == 'price_high_low':
            queryset = queryset.order_by('-variants__price')
        elif collection.sort_order == 'created_at':
            queryset = queryset.order_by('-created_at')
        elif collection.sort_order == 'title':
            queryset = queryset.order_by('title')

        return queryset.distinct()

    @staticmethod
    def update_collection(collection, data):
        """Update collection"""
        old_is_smart = collection.is_smart

        for field, value in data.items():
            if field not in ['conditions', 'product_ids']:
                setattr(collection, field, value)

        collection.save()

        # Update conditions for smart collections
        if collection.is_smart and 'conditions' in data:
            collection.conditions.all().delete()
            for condition_data in data['conditions']:
                CollectionCondition.objects.create(
                    collection=collection,
                    **condition_data
                )

        # Update products for manual collections
        if not collection.is_smart and 'product_ids' in data:
            collection.products.set(data['product_ids'])

        return collection
```

### 4.6 Coupon Services

#### CouponService
```python
class CouponService:
    """Business logic for coupon management"""

    @staticmethod
    def create_coupon(store, user, data):
        """Create new coupon"""
        coupon = Coupon.objects.create(
            store=store,
            campaign_id=data.get('campaign_id'),
            code=data['code'].upper(),
            type=data['type'],
            value=data['value'],
            minimum_order_amount=data.get('minimum_order_amount', 0),
            usage_limit=data.get('usage_limit'),
            usage_limit_per_customer=data.get('usage_limit_per_customer'),
            starts_at=data['starts_at'],
            ends_at=data['ends_at'],
            is_active=data.get('is_active', True),
            created_by=user
        )

        # Log creation
        log_event_async(
            user=user,
            store=store,
            action='coupon_created',
            object_type='coupon',
            object_id=coupon.id,
            details={
                'code': coupon.code,
                'type': coupon.type,
                'value': str(coupon.value)
            }
        )

        return coupon

    @staticmethod
    def validate_coupon(coupon, customer=None, cart_total=0):
        """Validate coupon for use"""
        return coupon.is_valid(customer, cart_total)

    @staticmethod
    def apply_coupon(coupon, order, customer=None):
        """Apply coupon to order"""
        is_valid, message = coupon.is_valid(customer, order.subtotal)

        if not is_valid:
            raise ValidationError(message)

        # Calculate discount
        discount_amount = coupon.apply_discount(order.subtotal)

        # Update order discount
        order.discount = discount_amount
        order.calculate_totals()
        order.save()

        # Add coupon to order
        order.coupons.add(coupon)

        # Increment usage count
        coupon.used_count += 1
        coupon.save()

        # Log coupon usage
        log_event_async(
            user=customer.user if customer else None,
            store=order.store,
            action='coupon_applied',
            object_type='coupon',
            object_id=coupon.id,
            details={
                'code': coupon.code,
                'order_id': order.id,
                'discount_amount': str(discount_amount)
            }
        )

        return discount_amount

    @staticmethod
    def generate_bulk_coupons(store, user, template_data, count):
        """Generate multiple coupons from template"""
        coupons = []
        prefix = template_data.get('prefix', '')
        base_code = template_data['code']

        for i in range(count):
            code = f"{prefix}{base_code}_{i+1}"
            coupon = Coupon.objects.create(
                store=store,
                campaign_id=template_data.get('campaign_id'),
                code=code,
                type=template_data['type'],
                value=template_data['value'],
                minimum_order_amount=template_data.get('minimum_order_amount', 0),
                usage_limit=template_data.get('usage_limit'),
                usage_limit_per_customer=template_data.get('usage_limit_per_customer'),
                starts_at=template_data['starts_at'],
                ends_at=template_data['ends_at'],
                is_active=template_data.get('is_active', True),
                created_by=user
            )
            coupons.append(coupon)

        # Log bulk generation
        log_event_async(
            user=user,
            store=store,
            action='coupons_bulk_generated',
            object_type='coupon',
            details={
                'count': count,
                'base_code': base_code,
                'prefix': prefix
            }
        )

        return coupons
```

### 4.7 Inventory Services

#### InventoryService
```python
class InventoryService:
    """Business logic for inventory management"""

    @staticmethod
    def adjust_inventory(store, product, variant, quantity, transaction_type, user=None, notes=''):
        """Adjust inventory levels"""
        inventory, created = Inventory.objects.get_or_create(
            store=store,
            product=product,
            variant=variant,
            defaults={'quantity': 0}
        )

        old_quantity = inventory.quantity

        if transaction_type == 'add':
            inventory.quantity += quantity
        elif transaction_type == 'subtract':
            inventory.quantity = max(0, inventory.quantity - quantity)
        elif transaction_type == 'set':
            inventory.quantity = quantity
        else:
            raise ValidationError("Invalid transaction type")

        inventory.save()

        # Create transaction record
        InventoryTransaction.objects.create(
            inventory=inventory,
            type=transaction_type,
            quantity=quantity,
            notes=notes,
            created_by=user
        )

        # Log inventory change
        log_event_async(
            user=user,
            store=store,
            action='inventory_adjusted',
            object_type='inventory',
            object_id=inventory.id,
            details={
                'product_title': product.title,
                'variant_title': variant.title if variant else None,
                'old_quantity': old_quantity,
                'new_quantity': inventory.quantity,
                'transaction_type': transaction_type,
                'quantity_change': quantity
            }
        )

        return inventory

    @staticmethod
    def reserve_inventory(order):
        """Reserve inventory for order"""
        for order_item in order.items.all():
            inventory = Inventory.objects.filter(
                store=order.store,
                product=order_item.product,
                variant=order_item.variant
            ).first()

            if inventory:
                if not inventory.reserve(order_item.quantity):
                    raise ValidationError(
                        f"Insufficient inventory for {order_item.product.title}"
                    )

    @staticmethod
    def release_inventory(order):
        """Release reserved inventory for cancelled order"""
        for order_item in order.items.all():
            inventory = Inventory.objects.filter(
                store=order.store,
                product=order_item.product,
                variant=order_item.variant
            ).first()

            if inventory:
                inventory.release(order_item.quantity)

    @staticmethod
    def deduct_inventory(order):
        """Deduct inventory for shipped order"""
        for order_item in order.items.all():
            inventory = Inventory.objects.filter(
                store=order.store,
                product=order_item.product,
                variant=order_item.variant
            ).first()

            if inventory:
                if not inventory.deduct(order_item.quantity):
                    raise ValidationError(
                        f"Insufficient inventory for {order_item.product.title}"
                    )

    @staticmethod
    def get_low_stock_alerts(store, threshold=10):
        """Get products with low inventory"""
        inventories = Inventory.objects.filter(
            store=store,
            available__lte=threshold
        ).select_related('product', 'variant')

        return inventories

    @staticmethod
    def sync_variant_inventory(variant):
        """Sync inventory between variant and inventory records"""
        inventory = Inventory.objects.filter(
            store=variant.product.store,
            product=variant.product,
            variant=variant
        ).first()

        if inventory:
            variant.inventory_quantity = inventory.quantity
            variant.save()
        else:
            # Create inventory record
            Inventory.objects.create(
                store=variant.product.store,
                product=variant.product,
                variant=variant,
                quantity=variant.inventory_quantity
            )
```
# Ecommerce Integration

## 5. Module Integration

### 5.1 Media Integration

#### Product Images
```python
# Product model with media integration
class Product(models.Model):
    # ... other fields
    featured_image = models.ForeignKey(
        'media.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='featured_products'
    )

    def get_all_images(self):
        """Get all product images including variants"""
        image_ids = []

        # Product images
        product_images = self.images.all()
        image_ids.extend([img.id for img in product_images])

        # Variant images
        for variant in self.variants.all():
            variant_images = variant.images.all()
            image_ids.extend([img.id for img in variant_images])

        return MediaFile.objects.filter(id__in=image_ids)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ForeignKey('media.MediaFile', on_delete=models.CASCADE)
    alt_text = models.CharField(max_length=255, blank=True)
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ['position']
```

#### Media File Relationships
```python
# In media/models.py - add reverse relationships
class MediaFile(models.Model):
    # ... existing fields

    # Ecommerce relationships
    featured_products = GenericRelation(
        Product,
        object_id_field='featured_image_id',
        related_query_name='featured_image_files'
    )

    def get_ecommerce_usage(self):
        """Get all ecommerce usage of this media file"""
        usage = {
            'featured_products': self.featured_products.count(),
            'product_images': ProductImage.objects.filter(image=self).count(),
            'variant_images': ProductVariantImage.objects.filter(image=self).count(),
            'category_images': ProductCategory.objects.filter(image=self).count(),
            'collection_images': Collection.objects.filter(image=self).count()
        }
        return usage
```

### 5.2 Accounts Integration

#### Customer Profile
```python
# Customer model linked to GlobalUser
class Customer(models.Model):
    user = models.OneToOneField(GlobalUser, on_delete=models.CASCADE)
    # ... other fields

    def get_user_permissions(self):
        """Get user's ecommerce permissions"""
        return self.user.get_all_permissions()

    def can_access_store(self, store):
        """Check if customer can access store"""
        return store.is_active and (
            store.is_public or
            self.user.stores.filter(id=store.id).exists()
        )
```

#### User Registration
```python
# In accounts/services.py
class AccountService:
    @staticmethod
    def register_customer(user_data, store=None):
        """Register new user with customer profile"""
        user = GlobalUser.objects.create_user(
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )

        customer = CustomerService.create_customer(user, user_data)

        # Add to store if specified
        if store:
            user.stores.add(store)

        # Send welcome email
        send_welcome_email.delay(user.id)

        return user, customer
```

### 5.3 Stores Integration

#### Store Configuration
```python
# Store model with ecommerce settings
class Store(models.Model):
    # ... existing fields

    # Ecommerce settings
    currency = models.CharField(max_length=3, default='USD')
    tax_included = models.BooleanField(default=False)
    allow_guest_checkout = models.BooleanField(default=True)
    require_account_for_purchase = models.BooleanField(default=False)

    # Default settings
    default_shipping_method = models.ForeignKey(
        'ecommerce.ShippingMethod',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='default_stores'
    )

    default_tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    def get_ecommerce_settings(self):
        """Get store ecommerce configuration"""
        return {
            'currency': self.currency,
            'tax_included': self.tax_included,
            'allow_guest_checkout': self.allow_guest_checkout,
            'require_account_for_purchase': self.require_account_for_purchase,
            'default_shipping_method': self.default_shipping_method,
            'default_tax_rate': self.default_tax_rate
        }
```

#### Store Scoping
```python
# Base mixin for store-scoped models
class StoreScopedModel(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def clean(self):
        """Validate store access"""
        if not self.store.is_active:
            raise ValidationError("Store is not active")

# Usage in ecommerce models
class Product(StoreScopedModel):
    # ... fields
    pass

class Order(StoreScopedModel):
    # ... fields
    pass
```

### 5.4 Logs Integration

#### Auto-logging Signals
```python
# In ecommerce/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from logs.services import log_event_async

@receiver(post_save, sender=Product)
def log_product_change(sender, instance, created, **kwargs):
    """Log product changes"""
    action = 'product_created' if created else 'product_updated'

    log_event_async(
        user=getattr(instance, 'created_by', None),
        store=instance.store,
        action=action,
        object_type='product',
        object_id=instance.id,
        details={
            'title': instance.title,
            'sku': instance.sku,
            'status': instance.status
        }
    )

@receiver(post_save, sender=Order)
def log_order_change(sender, instance, created, **kwargs):
    """Log order changes"""
    if created:
        log_event_async(
            user=None,  # Orders can be created by customers
            store=instance.store,
            action='order_created',
            object_type='order',
            object_id=instance.id,
            details={
                'order_number': instance.order_number,
                'total': str(instance.total),
                'customer_email': instance.customer.email
            }
        )

@receiver(post_save, sender=Payment)
def log_payment_change(sender, instance, created, **kwargs):
    """Log payment changes"""
    if created:
        log_event_async(
            user=None,
            store=instance.order.store,
            action='payment_created',
            object_type='payment',
            object_id=instance.id,
            details={
                'order_id': instance.order.id,
                'amount': str(instance.amount),
                'status': instance.status
            }
        )
```

#### Manual Logging
```python
# In ecommerce/services.py
class OrderService:
    @staticmethod
    def update_order_status(order, new_status, user=None):
        """Update order status with logging"""
        old_status = order.status

        # ... business logic ...

        # Log the status change
        log_event_async(
            user=user,
            store=order.store,
            action='order_status_updated',
            object_type='order',
            object_id=order.id,
            details={
                'order_number': order.order_number,
                'old_status': old_status,
                'new_status': new_status
            }
        )

        return order
```

### 5.5 Translations Integration

#### Translatable Product Fields
```python
# In ecommerce/models.py
from translations.fields import TranslatableField

class Product(StoreScopedModel):
    # ... other fields

    # Translatable fields
    title = TranslatableField()
    description = TranslatableField()
    short_description = TranslatableField()
    seo_title = TranslatableField()
    seo_description = TranslatableField()

    def get_translated_title(self, language_code=None):
        """Get translated title"""
        return self.get_translation('title', language_code)

    def get_translated_description(self, language_code=None):
        """Get translated description"""
        return self.get_translation('description', language_code)

class ProductCategory(StoreScopedModel):
    # ... other fields

    # Translatable fields
    name = TranslatableField()
    description = TranslatableField()
    seo_title = TranslatableField()
    seo_description = TranslatableField()
```

#### Translation Service Integration
```python
# In ecommerce/services.py
from translations.services import TranslationService

class ProductService:
    @staticmethod
    def create_product(store, user, data, language_code=None):
        """Create product with translations"""
        product = Product.objects.create(
            store=store,
            # ... non-translatable fields ...
            created_by=user
        )

        # Set translations
        if language_code:
            TranslationService.set_translation(
                object_type='product',
                object_id=product.id,
                field='title',
                language_code=language_code,
                value=data['title']
            )

            if 'description' in data:
                TranslationService.set_translation(
                    object_type='product',
                    object_id=product.id,
                    field='description',
                    language_code=language_code,
                    value=data['description']
                )

        return product

    @staticmethod
    def get_product_with_translations(product, language_code=None):
        """Get product with translated fields"""
        if language_code:
            product.translated_title = product.get_translated_title(language_code)
            product.translated_description = product.get_translated_description(language_code)

        return product
```

### 5.6 SMTP Integration

#### Email Notifications
```python
# In ecommerce/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from smtp.services import EmailService

@shared_task
def send_order_confirmation_email(order_id):
    """Send order confirmation email"""
    order = Order.objects.get(id=order_id)

    # Get customer's preferred language
    language_code = getattr(order.customer.user, 'language_code', 'en')

    # Render email template
    context = {
        'order': order,
        'customer': order.customer,
        'store': order.store,
        'order_items': order.items.all()
    }

    html_content = render_to_string(
        f'ecommerce/emails/order_confirmation_{language_code}.html',
        context
    )

    text_content = render_to_string(
        f'ecommerce/emails/order_confirmation_{language_code}.txt',
        context
    )

    # Send email
    EmailService.send_email(
        store=order.store,
        template_name='order_confirmation',
        recipients=[order.customer.email],
        context=context,
        language_code=language_code
    )

@shared_task
def send_order_status_email(order_id, status):
    """Send order status update email"""
    order = Order.objects.get(id=order_id)

    context = {
        'order': order,
        'customer': order.customer,
        'status': status,
        'store': order.store
    }

    EmailService.send_email(
        store=order.store,
        template_name='order_status_update',
        recipients=[order.customer.email],
        context=context
    )

@shared_task
def send_low_stock_alert_email(store_id, product_ids):
    """Send low stock alert to store admin"""
    store = Store.objects.get(id=store_id)
    products = Product.objects.filter(id__in=product_ids)

    context = {
        'store': store,
        'products': products
    }

    # Send to store admin
    admin_emails = store.users.filter(
        storemembership__role__in=['admin', 'manager']
    ).values_list('email', flat=True)

    EmailService.send_email(
        store=store,
        template_name='low_stock_alert',
        recipients=list(admin_emails),
        context=context
    )
```

#### Email Templates
```python
# In ecommerce/models.py - email template integration
class EmailTemplate(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    language_code = models.CharField(max_length=10, default='en')

    class Meta:
        unique_together = ['store', 'name', 'language_code']

# Predefined ecommerce email templates
ECOMMERCE_EMAIL_TEMPLATES = [
    'order_confirmation',
    'order_status_update',
    'payment_confirmation',
    'shipping_confirmation',
    'delivery_confirmation',
    'refund_confirmation',
    'low_stock_alert',
    'welcome_customer',
    'password_reset',
    'abandoned_cart_reminder'
]
```

### 5.7 Multi-tenant Data Isolation

#### Store-scoped Query Manager
```python
# In ecommerce/managers.py
class StoreScopedManager(models.Manager):
    """Manager for store-scoped queries"""

    def for_store(self, store):
        """Filter by store"""
        return self.filter(store=store)

    def for_user(self, user):
        """Filter by user's stores"""
        return self.filter(store__in=user.stores.all())

# Usage in models
class Product(StoreScopedModel):
    objects = StoreScopedManager()

    class Meta:
        base_manager_name = 'objects'
```

#### Permission Mixins
```python
# In ecommerce/permissions.py
class StoreScopedPermission:
    """Permission mixin for store-scoped access"""

    def has_store_permission(self, request, store):
        """Check if user has permission for store"""
        if not store.is_active:
            return False

        if request.user.is_superuser:
            return True

        return request.user.stores.filter(id=store.id).exists()

    def has_object_permission(self, request, view, obj):
        """Check permission for specific object"""
        if hasattr(obj, 'store'):
            return self.has_store_permission(request, obj.store)

        return True
```

### 5.8 API Integration

#### Store Context Middleware
```python
# In ecommerce/middleware.py
class StoreContextMiddleware:
    """Middleware to add store context to request"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Determine store from subdomain, header, or user
        store = self.get_store_from_request(request)

        if store:
            request.store = store
            request.store_settings = store.get_ecommerce_settings()

        response = self.get_response(request)
        return response

    def get_store_from_request(self, request):
        """Get store from various sources"""
        # Try subdomain
        host = request.get_host()
        subdomain = host.split('.')[0] if '.' in host else None

        if subdomain:
            try:
                return Store.objects.get(subdomain=subdomain, is_active=True)
            except Store.DoesNotExist:
                pass

        # Try header
        store_id = request.META.get('HTTP_X_STORE_ID')
        if store_id:
            try:
                return Store.objects.get(id=store_id, is_active=True)
            except Store.DoesNotExist:
                pass

        # Try user's default store
        if request.user.is_authenticated:
            return request.user.stores.filter(is_active=True).first()

        # Try default store
        return Store.objects.filter(is_default=True, is_active=True).first()
```

#### API Response Formatting
```python
# In ecommerce/serializers.py
class StoreAwareSerializer:
    """Serializer mixin for store-aware responses"""

    def to_representation(self, instance):
        """Add store context to response"""
        data = super().to_representation(instance)

        if hasattr(instance, 'store'):
            data['store'] = {
                'id': instance.store.id,
                'name': instance.store.name,
                'currency': instance.store.currency
            }

        return data

class ProductSerializer(StoreAwareSerializer, serializers.ModelSerializer):
    """Product serializer with store context"""

    store_info = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'description', 'sku', 'status',
            'featured', 'price', 'store_info', 'created_at', 'updated_at'
        ]

    def get_store_info(self, obj):
        return {
            'id': obj.store.id,
            'name': obj.store.name,
            'currency': obj.store.currency
        }
```

### 5.9 Event System Integration

#### Ecommerce Events
```python
# In ecommerce/events.py
class EcommerceEvents:
    """Ecommerce event definitions"""

    PRODUCT_CREATED = 'product_created'
    PRODUCT_UPDATED = 'product_updated'
    PRODUCT_DELETED = 'product_deleted'

    ORDER_CREATED = 'order_created'
    ORDER_UPDATED = 'order_updated'
    ORDER_CANCELLED = 'order_cancelled'
    ORDER_FULFILLED = 'order_fulfilled'

    PAYMENT_RECEIVED = 'payment_received'
    PAYMENT_FAILED = 'payment_failed'

    CART_ABANDONED = 'cart_abandoned'
    CART_CONVERTED = 'cart_converted'

    CUSTOMER_REGISTERED = 'customer_registered'
    CUSTOMER_LOGIN = 'customer_login'

    INVENTORY_LOW = 'inventory_low'
    INVENTORY_OUT_OF_STOCK = 'inventory_out_of_stock'

# Event handlers
@receiver(EcommerceEvents.ORDER_CREATED)
def handle_order_created(sender, order, **kwargs):
    """Handle order created event"""
    # Update customer statistics
    order.customer.update_statistics()

    # Reserve inventory
    OrderService.reserve_inventory(order)

    # Send confirmation email
    send_order_confirmation_email.delay(order.id)

    # Log to analytics
    track_analytics_event.delay('order_created', {
        'order_id': order.id,
        'store_id': order.store.id,
        'total': float(order.total),
        'customer_id': order.customer.id
    })
```

### 5.10 Analytics Integration

#### Analytics Tracking
```python
# In ecommerce/analytics.py
class EcommerceAnalytics:
    """Analytics tracking for ecommerce events"""

    @staticmethod
    def track_product_view(product, user=None):
        """Track product view"""
        track_event.delay('product_viewed', {
            'product_id': product.id,
            'store_id': product.store.id,
            'user_id': user.id if user else None,
            'timestamp': timezone.now().isoformat()
        })

    @staticmethod
    def track_cart_action(cart, action, user=None):
        """Track cart actions"""
        track_event.delay('cart_action', {
            'cart_id': cart.id,
            'store_id': cart.store.id,
            'action': action,  # 'add', 'remove', 'update', 'clear'
            'item_count': cart.get_item_count(),
            'subtotal': float(cart.get_subtotal()),
            'user_id': user.id if user else None,
            'timestamp': timezone.now().isoformat()
        })

    @staticmethod
    def track_purchase(order):
        """Track purchase completion"""
        track_event.delay('purchase_completed', {
            'order_id': order.id,
            'store_id': order.store.id,
            'customer_id': order.customer.id,
            'total': float(order.total),
            'item_count': order.items.count(),
            'payment_method': order.payments.first().payment_method.type,
            'timestamp': timezone.now().isoformat()
        })

# Celery task for analytics
@shared_task
def track_analytics_event(event_name, data):
    """Send analytics event to tracking service"""
    # Integration with Google Analytics, Mixpanel, etc.
    pass
```
# Ecommerce Security

## 6. Security and Privacy Rules

### 6.1 Data Protection

#### GDPR Compliance
```python
# Customer data handling
class Customer(models.Model):
    # ... fields

    def get_personal_data(self):
        """Get all personal data for GDPR export"""
        return {
            'user': {
                'email': self.user.email,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'date_joined': self.user.date_joined.isoformat()
            },
            'customer': {
                'first_name': self.first_name,
                'last_name': self.last_name,
                'email': self.email,
                'phone': self.phone,
                'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
                'addresses': {
                    'billing': self.default_billing_address,
                    'shipping': self.default_shipping_address
                }
            },
            'orders': [
                {
                    'order_number': order.order_number,
                    'total': str(order.total),
                    'created_at': order.created_at.isoformat(),
                    'items': [
                        {
                            'title': item.title,
                            'quantity': item.quantity,
                            'price': str(item.unit_price)
                        }
                        for item in order.items.all()
                    ]
                }
                for order in Order.objects.filter(customer=self)
            ]
        }

    def anonymize_data(self):
        """Anonymize customer data for GDPR right to be forgotten"""
        # Anonymize user data
        self.user.email = f"deleted_{self.user.id}@deleted.com"
        self.user.first_name = "Deleted"
        self.user.last_name = "User"
        self.user.save()

        # Anonymize customer data
        self.email = f"deleted_{self.id}@deleted.com"
        self.first_name = "Deleted"
        self.last_name = "User"
        self.phone = ""
        self.default_billing_address = {}
        self.default_shipping_address = {}
        self.save()

        # Log anonymization
        log_event_async(
            user=None,
            store=None,
            action='customer_data_anonymized',
            object_type='customer',
            object_id=self.id,
            details={'reason': 'GDPR request'}
        )
```

#### Data Encryption
```python
# Sensitive data encryption
from django_cryptography.fields import encrypt

class Payment(models.Model):
    # ... fields

    # Encrypt sensitive payment data
    gateway_response = encrypt(models.JSONField(default=dict))
    billing_address = encrypt(models.JSONField(default=dict))

    class Meta:
        # Ensure encrypted fields are not logged
        exclude_logs = ['gateway_response', 'billing_address']

class Order(models.Model):
    # ... fields

    # Encrypt customer addresses
    billing_address = encrypt(models.JSONField(default=dict))
    shipping_address = encrypt(models.JSONField(default=dict))
    customer_notes = encrypt(models.TextField(blank=True))
```

### 6.2 Access Control

#### Store Isolation
```python
# Strict store-scoped permissions
class StoreScopedPermission(permissions.BasePermission):
    """Ensure users can only access their own store data"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Superuser can access all stores
        if request.user.is_superuser:
            return True

        # Get store from request
        store = getattr(request, 'store', None)
        if not store:
            return False

        # Check user has access to store
        return request.user.stores.filter(id=store.id).exists()

    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, 'store'):
            return True

        if request.user.is_superuser:
            return True

        return obj.store == request.store

# Apply to all ecommerce ViewSets
class ProductViewSet(StoreScopedViewSet):
    permission_classes = [IsAuthenticated, StoreScopedPermission]
    # ... rest of ViewSet
```

#### Role-based Permissions
```python
# Store membership roles
class StoreMembership(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('viewer', 'Viewer')
    ]

    user = models.ForeignKey(GlobalUser, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ['user', 'store']

# Role-based permissions
class EcommerceRolePermission:
    """Define permissions for each role"""

    PERMISSIONS = {
        'owner': ['*'],  # All permissions
        'admin': [
            'product.create', 'product.read', 'product.update', 'product.delete',
            'order.create', 'order.read', 'order.update',
            'customer.create', 'customer.read', 'customer.update',
            'coupon.create', 'coupon.read', 'coupon.update', 'coupon.delete',
            'collection.create', 'collection.read', 'collection.update', 'collection.delete'
        ],
        'manager': [
            'product.create', 'product.read', 'product.update',
            'order.read', 'order.update',
            'customer.read', 'customer.update',
            'coupon.read', 'coupon.create', 'coupon.update',
            'collection.read', 'collection.create', 'collection.update'
        ],
        'staff': [
            'product.read', 'product.update',
            'order.read', 'order.update',
            'customer.read',
            'coupon.read'
        ],
        'viewer': [
            'product.read', 'order.read', 'customer.read', 'coupon.read'
        ]
    }

    @classmethod
    def has_permission(cls, user, store, permission):
        """Check if user has specific permission"""
        try:
            membership = StoreMembership.objects.get(user=user, store=store)
            role_permissions = cls.PERMISSIONS.get(membership.role, [])

            return '*' in role_permissions or permission in role_permissions
        except StoreMembership.DoesNotExist:
            return False
```

### 6.3 Input Validation

#### Product Data Validation
```python
# Comprehensive validation for product data
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def validate_title(self, value):
        """Validate product title"""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("Product title must be at least 3 characters")

        # Check for malicious content
        if any(keyword in value.lower() for keyword in ['script', 'javascript', 'alert']):
            raise serializers.ValidationError("Invalid characters in title")

        return value.strip()

    def validate_price(self, value):
        """Validate price values"""
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")

        if value > 999999.99:
            raise serializers.ValidationError("Price exceeds maximum allowed amount")

        return value

    def validate_sku(self, value):
        """Validate SKU format"""
        if not value:
            raise serializers.ValidationError("SKU is required")

        # Check SKU format (alphanumeric with hyphens/underscores)
        import re
        if not re.match(r'^[A-Za-z0-9_-]+$', value):
            raise serializers.ValidationError("SKU can only contain letters, numbers, hyphens, and underscores")

        return value.upper()

    def validate(self, data):
        """Cross-field validation"""
        # Validate variant prices
        if 'variants' in data:
            for variant in data['variants']:
                if variant.get('price', 0) < 0:
                    raise serializers.ValidationError("Variant price cannot be negative")

                if variant.get('compare_at_price') and variant['compare_at_price'] <= variant.get('price', 0):
                    raise serializers.ValidationError("Compare at price must be greater than regular price")

        return data
```

#### Order Validation
```python
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

    def validate_billing_address(self, value):
        """Validate billing address format"""
        required_fields = ['street', 'city', 'country', 'postal_code']

        for field in required_fields:
            if field not in value or not value[field]:
                raise serializers.ValidationError(f"Billing address missing required field: {field}")

        # Validate postal code format based on country
        country = value.get('country', '').upper()
        postal_code = value.get('postal_code', '')

        if country == 'US' and not re.match(r'^\d{5}(-\d{4})?$', postal_code):
            raise serializers.ValidationError("Invalid US postal code format")

        return value

    def validate_shipping_address(self, value):
        """Validate shipping address format"""
        return self.validate_billing_address(value)

    def validate(self, data):
        """Validate order consistency"""
        # Check if cart belongs to same store
        if 'cart' in data and 'store' in data:
            if data['cart'].store != data['store']:
                raise serializers.ValidationError("Cart must belong to the same store")

        # Validate customer belongs to store
        if 'customer' in data and 'store' in data:
            customer_orders = Order.objects.filter(
                customer=data['customer'],
                store=data['store']
            )
            if not customer_orders.exists() and data['customer'].user.stores.filter(id=data['store'].id).exists():
                # First order for this customer in this store
                pass

        return data
```

### 6.4 Rate Limiting

#### API Rate Limiting
```python
# Custom rate limiting for ecommerce endpoints
from django.core.cache import cache
from django.http import HttpResponseTooManyRequests
from rest_framework.views import APIView

class EcommerceRateLimitMixin:
    """Rate limiting mixin for ecommerce APIs"""

    RATE_LIMITS = {
        'cart': '100/hour',
        'order': '10/hour',
        'payment': '5/hour',
        'product_view': '1000/hour',
        'search': '200/hour'
    }

    def get_rate_limit(self, view_name):
        """Get rate limit for specific view"""
        return self.RATE_LIMITS.get(view_name, '100/hour')

    def check_rate_limit(self, request, view_name):
        """Check if request exceeds rate limit"""
        if not request.user.is_authenticated:
            # Stricter limits for anonymous users
            limit = self.get_rate_limit(view_name)
            limit = str(int(limit.split('/')[0]) // 2) + '/' + limit.split('/')[1]
        else:
            limit = self.get_rate_limit(view_name)

        # Parse limit
        max_requests, period = limit.split('/')
        period_seconds = {'hour': 3600, 'minute': 60, 'second': 1}[period]

        # Generate cache key
        if request.user.is_authenticated:
            key = f"rate_limit:{view_name}:{request.user.id}"
        else:
            key = f"rate_limit:{view_name}:{request.META.get('REMOTE_ADDR', 'unknown')}"

        # Check current count
        count = cache.get(key, 0)

        if count >= int(max_requests):
            return False

        # Increment counter
        cache.set(key, count + 1, period_seconds)
        return True

    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to check rate limits"""
        view_name = self.__class__.__name__.lower().replace('viewset', '')

        if not self.check_rate_limit(request, view_name):
            return HttpResponseTooManyRequests(
                '{"error": "Rate limit exceeded"}',
                content_type='application/json'
            )

        return super().dispatch(request, *args, **kwargs)

# Apply to sensitive endpoints
class CartViewSet(EcommerceRateLimitMixin, viewsets.ModelViewSet):
    # ... ViewSet implementation
    pass

class OrderViewSet(EcommerceRateLimitMixin, viewsets.ModelViewSet):
    # ... ViewSet implementation
    pass
```

### 6.5 Payment Security

#### PCI Compliance
```python
# Payment processing security
class PaymentService:
    """Secure payment processing service"""

    @staticmethod
    def process_payment(order, payment_method, payment_data):
        """Process payment with security measures"""
        # Validate payment method belongs to store
        if payment_method.store != order.store:
            raise ValidationError("Invalid payment method")

        # Never store full credit card details
        sensitive_data = ['card_number', 'cvv', 'expiry']

        # Log payment attempt without sensitive data
        log_data = {
            'order_id': order.id,
            'payment_method': payment_method.type,
            'amount': str(order.total),
            'timestamp': timezone.now().isoformat()
        }

        try:
            # Process payment through secure gateway
            if payment_method.type == 'stripe':
                result = PaymentService._process_stripe_payment(
                    payment_method, payment_data, order
                )
            elif payment_method.type == 'paypal':
                result = PaymentService._process_paypal_payment(
                    payment_method, payment_data, order
                )
            else:
                raise ValidationError("Unsupported payment method")

            # Log successful payment (without sensitive data)
            log_data['status'] = 'success'
            log_data['transaction_id'] = result.get('transaction_id', '')
            log_event_async(
                user=None,
                store=order.store,
                action='payment_processed',
                object_type='payment',
                details=log_data
            )

            return result

        except Exception as e:
            # Log failed payment
            log_data['status'] = 'failed'
            log_data['error'] = str(e)
            log_event_async(
                user=None,
                store=order.store,
                action='payment_failed',
                object_type='payment',
                details=log_data
            )

            raise

    @staticmethod
    def _process_stripe_payment(payment_method, payment_data, order):
        """Process Stripe payment securely"""
        import stripe

        stripe.api_key = payment_method.config.get('secret_key')

        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(order.total * 100),  # Convert to cents
            currency=order.currency.lower(),
            payment_method=payment_data.get('payment_method_id'),
            confirmation_method='manual',
            confirm=True
        )

        return {
            'status': 'completed' if intent.status == 'succeeded' else 'pending',
            'transaction_id': intent.id,
            'gateway_response': {'status': intent.status}
        }
```

#### Fraud Detection
```python
# Basic fraud detection
class FraudDetectionService:
    """Fraud detection for ecommerce transactions"""

    @staticmethod
    def analyze_order(order):
        """Analyze order for fraud indicators"""
        risk_score = 0
        indicators = []

        # Check order value
        if order.total > 1000:
            risk_score += 20
            indicators.append('high_value_order')

        # Check shipping vs billing address
        if order.billing_address != order.shipping_address:
            risk_score += 10
            indicators.append('address_mismatch')

        # Check customer order history
        if order.customer.order_count == 0:
            risk_score += 15
            indicators.append('first_time_customer')

        # Check order frequency
        recent_orders = Order.objects.filter(
            customer=order.customer,
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).count()

        if recent_orders > 5:
            risk_score += 25
            indicators.append('high_frequency_orders')

        # Check IP address (if available)
        # This would require storing IP addresses with orders

        return {
            'risk_score': risk_score,
            'indicators': indicators,
            'is_suspicious': risk_score > 50
        }

    @staticmethod
    def flag_suspicious_order(order):
        """Flag suspicious order for review"""
        analysis = FraudDetectionService.analyze_order(order)

        if analysis['is_suspicious']:
            order.status = 'flagged'
            order.save()

            # Notify admin
            send_fraud_alert_email.delay(order.id, analysis)

            # Log fraud detection
            log_event_async(
                user=None,
                store=order.store,
                action='order_flagged_fraud',
                object_type='order',
                object_id=order.id,
                details=analysis
            )

        return analysis
```

### 6.6 Data Privacy

#### Customer Consent Management
```python
# Marketing consent tracking
class CustomerConsent(models.Model):
    """Track customer consent for marketing and data processing"""

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    consent_type = models.CharField(max_length=50)  # 'email_marketing', 'sms_marketing', 'data_processing'
    granted = models.BooleanField(default=False)
    granted_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        unique_together = ['customer', 'consent_type']

class ConsentService:
    """Manage customer consent"""

    @staticmethod
    def record_consent(customer, consent_type, granted, request=None):
        """Record customer consent"""
        consent, created = CustomerConsent.objects.get_or_create(
            customer=customer,
            consent_type=consent_type,
            defaults={
                'granted': granted,
                'granted_at': timezone.now() if granted else None,
                'revoked_at': timezone.now() if not granted else None
            }
        )

        if not created:
            consent.granted = granted
            if granted:
                consent.granted_at = timezone.now()
                consent.revoked_at = None
            else:
                consent.revoked_at = timezone.now()
            consent.save()

        # Record request details if available
        if request:
            consent.ip_address = request.META.get('REMOTE_ADDR')
            consent.user_agent = request.META.get('HTTP_USER_AGENT', '')
            consent.save()

        # Log consent change
        log_event_async(
            user=customer.user,
            store=None,
            action=f'consent_{consent_type}',
            object_type='customer_consent',
            object_id=consent.id,
            details={
                'granted': granted,
                'ip_address': consent.ip_address
            }
        )

        return consent

    @staticmethod
    def has_consent(customer, consent_type):
        """Check if customer has granted consent"""
        try:
            consent = CustomerConsent.objects.get(
                customer=customer,
                consent_type=consent_type
            )
            return consent.granted and consent.revoked_at is None
        except CustomerConsent.DoesNotExist:
            return False
```

### 6.7 Security Headers

#### API Security Headers
```python
# Security middleware for ecommerce APIs
class EcommerceSecurityMiddleware:
    """Add security headers to ecommerce responses"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://js.stripe.com; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.stripe.com;"
        )

        # Remove server information
        response.pop('Server', None)

        return response
```

### 6.8 Audit Logging

#### Comprehensive Audit Trail
```python
# Enhanced audit logging for ecommerce
class EcommerceAuditLog(models.Model):
    """Detailed audit log for ecommerce operations"""

    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    user = models.ForeignKey(GlobalUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=50)
    object_id = models.CharField(max_length=50)
    old_values = models.JSONField(default=dict)
    new_values = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['store', 'action']),
            models.Index(fields=['object_type', 'object_id']),
            models.Index(fields=['timestamp']),
        ]

# Signal handlers for audit logging
@receiver(post_save, sender=Product)
def audit_product_change(sender, instance, created, **kwargs):
    """Audit product changes"""
    if created:
        EcommerceAuditLog.objects.create(
            store=instance.store,
            user=instance.created_by,
            action='product_created',
            object_type='product',
            object_id=instance.id,
            new_values={
                'title': instance.title,
                'sku': instance.sku,
                'status': instance.status,
                'price': str(instance.variants.first().price) if instance.variants.exists() else '0'
            }
        )
    else:
        # Track field changes
        old_instance = sender.objects.get(id=instance.id)
        changes = {}

        for field in ['title', 'status', 'featured']:
            old_value = getattr(old_instance, field)
            new_value = getattr(instance, field)
            if old_value != new_value:
                changes[field] = {'old': old_value, 'new': new_value}

        if changes:
            EcommerceAuditLog.objects.create(
                store=instance.store,
                user=getattr(instance, 'updated_by', None),
                action='product_updated',
                object_type='product',
                object_id=instance.id,
                old_values=changes
            )
```

### 6.9 Security Best Practices

#### Input Sanitization
```python
# Sanitize all user inputs
import bleach
from django.utils.html import strip_tags

class SanitizedCharField(models.CharField):
    """CharField that automatically sanitizes input"""

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if value:
            # Remove HTML tags and sanitize
            clean_value = bleach.clean(value, tags=[], strip=True)
            setattr(model_instance, self.attname, clean_value)
        return value

class SanitizedTextField(models.TextField):
    """TextField that automatically sanitizes input"""

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if value:
            # Allow limited HTML tags for descriptions
            allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li']
            clean_value = bleach.clean(value, tags=allowed_tags, strip=True)
            setattr(model_instance, self.attname, clean_value)
        return value

# Usage in models
class Product(models.Model):
    title = SanitizedCharField(max_length=255)
    description = SanitizedTextField(blank=True)
    # ... other fields
```

#### SQL Injection Prevention
```python
# Use Django ORM properly to prevent SQL injection
class ProductQuerySet(models.QuerySet):
    """Safe custom queries for products"""

    def by_price_range(self, min_price, max_price):
        """Safe price range filtering"""
        return self.filter(
            variants__price__gte=min_price,
            variants__price__lte=max_price
        )

    def search_safely(self, query):
        """Safe search implementation"""
        return self.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(sku__icontains=query)
        )

# Never use raw SQL with user input
# BAD: Product.objects.raw(f"SELECT * FROM product WHERE title LIKE '%{user_input}%'")
# GOOD: Product.objects.filter(title__icontains=user_input)
```
# Ecommerce Testing

## 7. Testing Requirements

### 7.1 Model Tests

#### Product Model Tests
```python
# tests/test_models.py
import pytest
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from ecommerce.models import Product, ProductVariant, ProductCategory
from stores.models import Store
from accounts.models import GlobalUser

class ProductModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            subdomain="test",
            is_active=True
        )
        self.user = GlobalUser.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.category = ProductCategory.objects.create(
            store=self.store,
            name="Test Category",
            slug="test-category",
            created_by=self.user
        )

    def test_product_creation(self):
        """Test product creation with required fields"""
        product = Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            created_by=self.user
        )

        assert product.title == "Test Product"
        assert product.slug == "test-product"
        assert product.sku == "TEST-001"
        assert product.status == "draft"
        assert product.store == self.store
        assert product.created_by == self.user

    def test_product_slug_uniqueness_per_store(self):
        """Test that product slugs are unique per store"""
        Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            created_by=self.user
        )

        # Should raise ValidationError for duplicate slug
        with pytest.raises(ValidationError):
            Product.objects.create(
                store=self.store,
                title="Test Product 2",
                slug="test-product",  # Duplicate slug
                sku="TEST-002",
                created_by=self.user
            )

    def test_product_can_have_same_slug_in_different_stores(self):
        """Test that same slug can exist in different stores"""
        store2 = Store.objects.create(
            name="Test Store 2",
            subdomain="test2",
            is_active=True
        )

        product1 = Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            created_by=self.user
        )

        product2 = Product.objects.create(
            store=store2,
            title="Test Product",
            slug="test-product",  # Same slug, different store
            sku="TEST-002",
            created_by=self.user
        )

        assert product1.slug == product2.slug
        assert product1.store != product2.store

    def test_product_variant_creation(self):
        """Test product variant creation"""
        product = Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            created_by=self.user
        )

        variant = ProductVariant.objects.create(
            product=product,
            title="Small",
            sku="TEST-001-S",
            price=Decimal('19.99'),
            inventory_quantity=10
        )

        assert variant.product == product
        assert variant.title == "Small"
        assert variant.price == Decimal('19.99')
        assert variant.inventory_quantity == 10

    def test_product_variant_sku_uniqueness(self):
        """Test that variant SKUs are unique"""
        product = Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            created_by=self.user
        )

        ProductVariant.objects.create(
            product=product,
            title="Small",
            sku="TEST-001-S",
            price=Decimal('19.99')
        )

        # Should raise ValidationError for duplicate SKU
        with pytest.raises(ValidationError):
            ProductVariant.objects.create(
                product=product,
                title="Medium",
                sku="TEST-001-S",  # Duplicate SKU
                price=Decimal('24.99')
            )

class ProductCategoryTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            subdomain="test",
            is_active=True
        )
        self.user = GlobalUser.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

    def test_category_hierarchy(self):
        """Test category parent-child relationships"""
        parent = ProductCategory.objects.create(
            store=self.store,
            name="Parent Category",
            slug="parent-category",
            created_by=self.user
        )

        child = ProductCategory.objects.create(
            store=self.store,
            name="Child Category",
            slug="child-category",
            parent=parent,
            created_by=self.user
        )

        assert child.parent == parent
        assert parent.children.first() == child

    def test_prevent_circular_reference(self):
        """Test prevention of circular category references"""
        parent = ProductCategory.objects.create(
            store=self.store,
            name="Parent Category",
            slug="parent-category",
            created_by=self.user
        )

        child = ProductCategory.objects.create(
            store=self.store,
            name="Child Category",
            slug="child-category",
            parent=parent,
            created_by=self.user
        )

        # Should raise ValidationError when trying to set parent as child's parent
        with pytest.raises(ValidationError):
            parent.parent = child
            parent.clean()
```

#### Order Model Tests
```python
class OrderModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            subdomain="test",
            is_active=True
        )
        self.user = GlobalUser.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.customer = Customer.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="test@example.com"
        )

    def test_order_number_generation(self):
        """Test automatic order number generation"""
        order = Order.objects.create(
            store=self.store,
            customer=self.customer,
            subtotal=Decimal('100.00'),
            tax=Decimal('10.00'),
            shipping=Decimal('5.00'),
            total=Decimal('115.00')
        )

        assert order.order_number.startswith("ORD-")
        assert len(order.order_number) > 10

    def test_order_status_transitions(self):
        """Test valid order status transitions"""
        order = Order.objects.create(
            store=self.store,
            customer=self.customer,
            status='pending',
            subtotal=Decimal('100.00'),
            tax=Decimal('10.00'),
            shipping=Decimal('5.00'),
            total=Decimal('115.00')
        )

        # Valid transition
        order.status = 'confirmed'
        order.save()
        assert order.status == 'confirmed'

        # Invalid transition should be handled by service layer
        # This would be tested in service tests

    def test_order_total_calculation(self):
        """Test order total calculation"""
        order = Order.objects.create(
            store=self.store,
            customer=self.customer,
            subtotal=Decimal('100.00'),
            tax=Decimal('10.00'),
            shipping=Decimal('5.00'),
            discount=Decimal('10.00'),
            total=Decimal('105.00')
        )

        assert order.total == order.subtotal + order.tax + order.shipping - order.discount
```

### 7.2 ViewSet Tests

#### Product ViewSet Tests
```python
# tests/test_views.py
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from ecommerce.models import Product, ProductVariant
from stores.models import Store

User = get_user_model()

class ProductViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = Store.objects.create(
            name="Test Store",
            subdomain="test",
            is_active=True
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.user.stores.add(self.store)
        self.client.force_authenticate(user=self.user)

        # Add store to request context
        self.client.defaults['HTTP_X_STORE_ID'] = self.store.id

    def test_list_products(self):
        """Test listing products"""
        Product.objects.create(
            store=self.store,
            title="Product 1",
            slug="product-1",
            sku="PROD-001",
            created_by=self.user
        )

        Product.objects.create(
            store=self.store,
            title="Product 2",
            slug="product-2",
            sku="PROD-002",
            created_by=self.user
        )

        response = self.client.get('/api/v2/ecommerce/products/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_create_product(self):
        """Test creating a product"""
        data = {
            'title': 'New Product',
            'slug': 'new-product',
            'sku': 'NEW-001',
            'description': 'Test description',
            'status': 'published'
        }

        response = self.client.post('/api/v2/ecommerce/products/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Product.objects.count() == 1
        assert Product.objects.first().title == 'New Product'

    def test_create_product_requires_store(self):
        """Test that product creation requires store context"""
        self.client.defaults.pop('HTTP_X_STORE_ID', None)

        data = {
            'title': 'New Product',
            'slug': 'new-product',
            'sku': 'NEW-001'
        }

        response = self.client.post('/api/v2/ecommerce/products/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_product(self):
        """Test updating a product"""
        product = Product.objects.create(
            store=self.store,
            title="Original Title",
            slug="original-title",
            sku="ORIG-001",
            created_by=self.user
        )

        data = {
            'title': 'Updated Title',
            'status': 'published'
        }

        response = self.client.patch(
            f'/api/v2/ecommerce/products/{product.id}/',
            data
        )

        assert response.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert product.title == 'Updated Title'
        assert product.status == 'published'

    def test_delete_product(self):
        """Test deleting a product"""
        product = Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            created_by=self.user
        )

        response = self.client.delete(f'/api/v2/ecommerce/products/{product.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Product.objects.count() == 0

    def test_duplicate_product(self):
        """Test duplicating a product"""
        product = Product.objects.create(
            store=self.store,
            title="Original Product",
            slug="original-product",
            sku="ORIG-001",
            created_by=self.user
        )

        ProductVariant.objects.create(
            product=product,
            title="Small",
            sku="ORIG-001-S",
            price=Decimal('19.99')
        )

        response = self.client.post(
            f'/api/v2/ecommerce/products/{product.id}/duplicate/'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Product.objects.count() == 2

        duplicated = Product.objects.last()
        assert duplicated.title == "Original Product (Copy)"
        assert duplicated.variants.count() == 1

    def test_store_isolation(self):
        """Test that users can only access their own store's products"""
        other_store = Store.objects.create(
            name="Other Store",
            subdomain="other",
            is_active=True
        )

        # Create product in other store
        Product.objects.create(
            store=other_store,
            title="Other Product",
            slug="other-product",
            sku="OTHER-001",
            created_by=self.user
        )

        # Create product in user's store
        Product.objects.create(
            store=self.store,
            title="My Product",
            slug="my-product",
            sku="MY-001",
            created_by=self.user
        )

        response = self.client.get('/api/v2/ecommerce/products/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'My Product'
```

#### Cart ViewSet Tests
```python
class CartViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = Store.objects.create(
            name="Test Store",
            subdomain="test",
            is_active=True
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.customer = Customer.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="test@example.com"
        )
        self.client.force_authenticate(user=self.user)
        self.client.defaults['HTTP_X_STORE_ID'] = self.store.id

        # Create test product
        self.product = Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            created_by=self.user
        )

        self.variant = ProductVariant.objects.create(
            product=self.product,
            title="Small",
            sku="TEST-001-S",
            price=Decimal('19.99'),
            inventory_quantity=10
        )

    def test_add_item_to_cart(self):
        """Test adding item to cart"""
        data = {
            'product_id': self.product.id,
            'variant_id': self.variant.id,
            'quantity': 2
        }

        response = self.client.post('/api/v2/ecommerce/cart/add_item/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Cart.objects.count() == 1
        assert CartItem.objects.count() == 1

        cart_item = CartItem.objects.first()
        assert cart_item.quantity == 2
        assert cart_item.product == self.product
        assert cart_item.variant == self.variant

    def test_update_cart_item_quantity(self):
        """Test updating cart item quantity"""
        # Add item first
        cart = Cart.objects.create(
            store=self.store,
            customer=self.customer
        )
        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            variant=self.variant,
            quantity=1,
            unit_price=self.variant.price
        )

        data = {
            'item_id': cart_item.id,
            'quantity': 3
        }

        response = self.client.put('/api/v2/ecommerce/cart/update_item/', data)

        assert response.status_code == status.HTTP_200_OK
        cart_item.refresh_from_db()
        assert cart_item.quantity == 3

    def test_remove_item_from_cart(self):
        """Test removing item from cart"""
        cart = Cart.objects.create(
            store=self.store,
            customer=self.customer
        )
        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            variant=self.variant,
            quantity=1,
            unit_price=self.variant.price
        )

        data = {'item_id': cart_item.id}
        response = self.client.delete('/api/v2/ecommerce/cart/remove_item/', data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert CartItem.objects.count() == 0

    def test_cart_summary(self):
        """Test getting cart summary"""
        cart = Cart.objects.create(
            store=self.store,
            customer=self.customer
        )
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            variant=self.variant,
            quantity=2,
            unit_price=self.variant.price
        )

        response = self.client.get('/api/v2/ecommerce/cart/summary/')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['item_count'] == 2
        assert Decimal(data['subtotal']) == Decimal('39.98')
```

### 7.3 Service Tests

#### Product Service Tests
```python
# tests/test_services.py
import pytest
from decimal import Decimal
from django.test import TestCase
from ecommerce.services import ProductService
from ecommerce.models import Product, ProductVariant
from stores.models import Store
from accounts.models import GlobalUser

class ProductServiceTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            subdomain="test",
            is_active=True
        )
        self.user = GlobalUser.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

    def test_create_product_with_variants(self):
        """Test creating product with variants"""
        data = {
            'title': 'Test Product',
            'slug': 'test-product',
            'sku': 'TEST-001',
            'description': 'Test description',
            'status': 'published',
            'variants': [
                {
                    'title': 'Small',
                    'sku': 'TEST-001-S',
                    'price': Decimal('19.99'),
                    'inventory_quantity': 10
                },
                {
                    'title': 'Medium',
                    'sku': 'TEST-001-M',
                    'price': Decimal('24.99'),
                    'inventory_quantity': 15
                }
            ]
        }

        product = ProductService.create_product(self.store, self.user, data)

        assert product.title == 'Test Product'
        assert product.variants.count() == 2
        assert product.variants.first().price == Decimal('19.99')

    def test_duplicate_product(self):
        """Test duplicating a product"""
        # Create original product
        original = Product.objects.create(
            store=self.store,
            title="Original Product",
            slug="original-product",
            sku="ORIG-001",
            created_by=self.user
        )

        ProductVariant.objects.create(
            product=original,
            title="Small",
            sku="ORIG-001-S",
            price=Decimal('19.99')
        )

        # Duplicate product
        duplicate = ProductService.duplicate_product(original, self.user)

        assert duplicate.title == "Original Product (Copy)"
        assert duplicate.slug.startswith("original-product-copy-")
        assert duplicate.variants.count() == 1
        assert duplicate.variants.first().sku == "ORIG-001-S-COPY"

    def test_update_product_status_logs_change(self):
        """Test that status changes are logged"""
        product = Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            status='draft',
            created_by=self.user
        )

        # Update status
        ProductService.update_product(product, self.user, {'status': 'published'})

        # Check that log was created (this would require mocking log_event_async)
        product.refresh_from_db()
        assert product.status == 'published'
```

#### Cart Service Tests
```python
class CartServiceTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            subdomain="test",
            is_active=True
        )
        self.user = GlobalUser.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.customer = Customer.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="test@example.com"
        )

        self.product = Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            created_by=self.user
        )

        self.variant = ProductVariant.objects.create(
            product=self.product,
            title="Small",
            sku="TEST-001-S",
            price=Decimal('19.99'),
            inventory_quantity=10
        )

        # Create inventory
        Inventory.objects.create(
            store=self.store,
            product=self.product,
            variant=self.variant,
            quantity=10
        )

    def test_add_item_to_cart_with_inventory_check(self):
        """Test adding item with inventory validation"""
        cart = Cart.objects.create(
            store=self.store,
            customer=self.customer
        )

        cart_item = CartService.add_item(
            cart, self.product, self.variant, 5
        )

        assert cart_item.quantity == 5
        assert cart_item.unit_price == self.variant.price

        # Check inventory was reserved
        inventory = Inventory.objects.get(
            store=self.store,
            product=self.product,
            variant=self.variant
        )
        assert inventory.reserved == 5

    def test_add_item_exceeds_inventory(self):
        """Test that adding items exceeding inventory raises error"""
        cart = Cart.objects.create(
            store=self.store,
            customer=self.customer
        )

        with pytest.raises(ValidationError):
            CartService.add_item(
                cart, self.product, self.variant, 15  # Exceeds inventory
            )

    def test_convert_cart_to_order(self):
        """Test converting cart to order"""
        cart = Cart.objects.create(
            store=self.store,
            customer=self.customer
        )

        CartItem.objects.create(
            cart=cart,
            product=self.product,
            variant=self.variant,
            quantity=2,
            unit_price=self.variant.price
        )

        billing_address = {
            'street': '123 Main St',
            'city': 'Test City',
            'country': 'US',
            'postal_code': '12345'
        }

        shipping_address = {
            'street': '123 Main St',
            'city': 'Test City',
            'country': 'US',
            'postal_code': '12345'
        }

        order = CartService.convert_to_order(
            cart, billing_address, shipping_address
        )

        assert order.customer == self.customer
        assert order.items.count() == 1
        assert order.status == 'pending'
        assert cart.status == 'converted'
```

### 7.4 Integration Tests

#### End-to-End Order Flow Tests
```python
# tests/test_integration.py
class OrderFlowIntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = Store.objects.create(
            name="Test Store",
            subdomain="test",
            is_active=True
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.customer = Customer.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="test@example.com"
        )
        self.client.force_authenticate(user=self.user)
        self.client.defaults['HTTP_X_STORE_ID'] = self.store.id

        # Create test product
        self.product = Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            status='published',
            created_by=self.user
        )

        self.variant = ProductVariant.objects.create(
            product=self.product,
            title="Small",
            sku="TEST-001-S",
            price=Decimal('19.99'),
            inventory_quantity=10
        )

        Inventory.objects.create(
            store=self.store,
            product=self.product,
            variant=self.variant,
            quantity=10
        )

    def test_complete_order_flow(self):
        """Test complete order flow from cart to payment"""
        # 1. Add item to cart
        cart_data = {
            'product_id': self.product.id,
            'variant_id': self.variant.id,
            'quantity': 2
        }
        response = self.client.post('/api/v2/ecommerce/cart/add_item/', cart_data)
        assert response.status_code == status.HTTP_201_CREATED

        # 2. Get cart summary
        response = self.client.get('/api/v2/ecommerce/cart/summary/')
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.json()['subtotal']) == Decimal('39.98')

        # 3. Create order from cart
        order_data = {
            'billing_address': {
                'street': '123 Main St',
                'city': 'Test City',
                'country': 'US',
                'postal_code': '12345'
            },
            'shipping_address': {
                'street': '123 Main St',
                'city': 'Test City',
                'country': 'US',
                'postal_code': '12345'
            }
        }
        response = self.client.post('/api/v2/ecommerce/orders/create_from_cart/', order_data)
        assert response.status_code == status.HTTP_201_CREATED

        order_id = response.json()['id']

        # 4. Check order was created
        response = self.client.get(f'/api/v2/ecommerce/orders/{order_id}/')
        assert response.status_code == status.HTTP_200_OK
        order_data = response.json()
        assert order_data['status'] == 'pending'
        assert order_data['items'][0]['quantity'] == 2

        # 5. Update order status
        response = self.client.post(
            f'/api/v2/ecommerce/orders/{order_id}/update_status/',
            {'status': 'confirmed'}
        )
        assert response.status_code == status.HTTP_200_OK

        # 6. Check inventory was updated
        inventory = Inventory.objects.get(
            store=self.store,
            product=self.product,
            variant=self.variant
        )
        assert inventory.reserved == 2
```

### 7.5 Performance Tests

#### Database Query Optimization Tests
```python
# tests/test_performance.py
import pytest
from django.test import TestCase
from django.test.utils import override_settings
from django.db import connection
from ecommerce.models import Product, ProductVariant

class PerformanceTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            subdomain="test",
            is_active=True
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

        # Create test data
        for i in range(100):
            product = Product.objects.create(
                store=self.store,
                title=f"Product {i}",
                slug=f"product-{i}",
                sku=f"PROD-{i:03d}",
                created_by=self.user
            )

            for j in range(3):
                ProductVariant.objects.create(
                    product=product,
                    title=f"Size {j}",
                    sku=f"PROD-{i:03d}-{j}",
                    price=Decimal(f"{i + j}.99")
                )

    def test_product_list_query_count(self):
        """Test that product list uses optimized queries"""
        with self.assertNumQueries(2):  # Should be 2 queries with select_related/prefetch_related
            products = Product.objects.select_related('store').prefetch_related(
                'variants'
            ).all()

            # Access data to trigger queries
            for product in products:
                list(product.variants.all())

    def test_search_performance(self):
        """Test search query performance"""
        with self.assertNumQueries(1):
            products = Product.objects.filter(
                title__icontains='Product 1'
            ).select_related('store')

            list(products)  # Execute query

    @override_settings(DEBUG=True)
    def test_no_n_plus_one_queries(self):
        """Test that no N+1 queries are made"""
        # Reset query count
        connection.queries_log.clear()

        # Get products with variants
        products = Product.objects.select_related('store').prefetch_related(
            'variants'
        ).all()[:10]

        # Access all data
        for product in products:
            print(product.title)
            for variant in product.variants.all():
                print(variant.title)

        # Should only have 2 queries (products + variants)
        assert len(connection.queries) <= 2
```

### 7.6 Security Tests

#### Security Test Cases
```python
# tests/test_security.py
class SecurityTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = Store.objects.create(
            name="Test Store",
            subdomain="test",
            is_active=True
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123"
        )

        self.user.stores.add(self.store)
        self.client.force_authenticate(user=self.user)
        self.client.defaults['HTTP_X_STORE_ID'] = self.store.id

    def test_store_isolation(self):
        """Test that users cannot access other stores' data"""
        other_store = Store.objects.create(
            name="Other Store",
            subdomain="other",
            is_active=True
        )

        # Create product in other store
        product = Product.objects.create(
            store=other_store,
            title="Other Product",
            slug="other-product",
            sku="OTHER-001",
            created_by=self.other_user
        )

        # Try to access other store's product
        response = self.client.get(f'/api/v2/ecommerce/products/{product.id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_input_sanitization(self):
        """Test that malicious input is sanitized"""
        malicious_data = {
            'title': '<script>alert("xss")</script>Product',
            'slug': 'malicious-product',
            'sku': 'MAL-001',
            'description': '<p>Valid description</p><script>alert("xss")</script>'
        }

        response = self.client.post('/api/v2/ecommerce/products/', malicious_data)

        assert response.status_code == status.HTTP_201_CREATED

        product = Product.objects.get()
        assert '<script>' not in product.title
        assert '<script>' not in product.description
        assert '<p>' in product.description  # Valid HTML should remain

    def test_rate_limiting(self):
        """Test API rate limiting"""
        # Make many requests quickly
        for i in range(150):  # Exceed rate limit
            response = self.client.get('/api/v2/ecommerce/products/')
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                break

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
```

### 7.7 Test Configuration

#### pytest Configuration
```python
# pytest.ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = backend.settings.test
python_files = tests.py test_*.py *_tests.py
addopts = --reuse-db --nomigrations --cov=ecommerce --cov-report=html --cov-report=term-missing
```

#### Test Settings
```python
# settings/test.py
from .base import *

# Test database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for speed
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Test-specific settings
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Faster for tests
]

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Celery task always eager for testing
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
```

### 7.8 Test Coverage Requirements

#### Coverage Targets
- **Models**: 95% coverage
- **Views**: 90% coverage
- **Services**: 95% coverage
- **Utilities**: 85% coverage
- **Overall**: 90% coverage

#### Required Test Scenarios
1. **Happy path** - Normal operation flows
2. **Error conditions** - Invalid inputs, edge cases
3. **Security** - Unauthorized access, input validation
4. **Performance** - Query optimization, N+1 prevention
5. **Integration** - Cross-module functionality
6. **Multi-tenancy** - Store isolation, permissions

#### Test Data Management
```python
# tests/fixtures.py
import pytest
from decimal import Decimal
from stores.models import Store
from accounts.models import GlobalUser
from ecommerce.models import Product, ProductVariant, Customer

@pytest.fixture
def store():
    return Store.objects.create(
        name="Test Store",
        subdomain="test",
        is_active=True
    )

@pytest.fixture
def user():
    return GlobalUser.objects.create_user(
        email="test@example.com",
        password="testpass123"
    )

@pytest.fixture
def customer(user):
    return Customer.objects.create(
        user=user,
        first_name="John",
        last_name="Doe",
        email="test@example.com"
    )

@pytest.fixture
def product(store, user):
    return Product.objects.create(
        store=store,
        title="Test Product",
        slug="test-product",
        sku="TEST-001",
        created_by=user
    )

@pytest.fixture
def product_variant(product):
    return ProductVariant.objects.create(
        product=product,
        title="Small",
        sku="TEST-001-S",
        price=Decimal('19.99')
    )
```
# Ecommerce Migration

## 8. Migration Strategy

### 8.1 Legacy Data Analysis

#### Current DFCMS Ecommerce Structure
```python
# Legacy models in dfcms/backend/modules/ecommerce/models.py

# 1. Product Models
- Product (basic fields)
- ProductVariant (limited fields)
- ProductCategory (hierarchical)
- ProductImage (media integration)

# 2. Order Models
- Order (basic order tracking)
- OrderItem (order line items)
- OrderStatus (status tracking)

# 3. Cart Models
- Cart (session/customer based)
- CartItem (cart line items)

# 4. Customer Models
- Customer (linked to User)
- CustomerAddress (address management)

# 5. Discount Models
- Discount (simple discounts)
- Coupon (coupon codes)

# 6. Inventory Models
- Inventory (basic tracking)
- InventoryTransaction (movement tracking)
```

#### Migration Complexity Assessment
```python
# Migration complexity matrix
MIGRATION_COMPLEXITY = {
    'products': {
        'data_volume': 'high',
        'relationship_complexity': 'medium',
        'business_logic_changes': 'high',
        'estimated_effort': '3-4 days'
    },
    'orders': {
        'data_volume': 'high',
        'relationship_complexity': 'high',
        'business_logic_changes': 'medium',
        'estimated_effort': '4-5 days'
    },
    'customers': {
        'data_volume': 'medium',
        'relationship_complexity': 'low',
        'business_logic_changes': 'low',
        'estimated_effort': '1-2 days'
    },
    'cart': {
        'data_volume': 'low',
        'relationship_complexity': 'low',
        'business_logic_changes': 'medium',
        'estimated_effort': '1 day'
    },
    'discounts': {
        'data_volume': 'low',
        'relationship_complexity': 'medium',
        'business_logic_changes': 'high',
        'estimated_effort': '2-3 days'
    },
    'inventory': {
        'data_volume': 'medium',
        'relationship_complexity': 'medium',
        'business_logic_changes': 'medium',
        'estimated_effort': '2-3 days'
    }
}
```

### 8.2 Migration Phases

#### Phase 1: Infrastructure Setup
```python
# Phase 1: Create new V2 structure
# Duration: 1-2 days

# 1. Create new models structure
# 2. Set up store scoping
# 3. Create migration framework
# 4. Set up data validation

class MigrationPhase1:
    """Phase 1: Infrastructure and model creation"""

    def create_new_models(self):
        """Create new V2 models with store scoping"""
        # Create Product model with store FK
        # Create ProductVariant with enhanced fields
        # Create Order model with new fields
        # Create Customer model linked to GlobalUser
        # Create new inventory system
        pass

    def setup_store_scoping(self):
        """Add store FK to all models"""
        # Add store field to all models
        # Create indexes for store-based queries
        # Set up store isolation
        pass

    def create_migration_utilities(self):
        """Create migration helper functions"""
        # Data validation utilities
        # Data transformation utilities
        # Progress tracking utilities
        pass
```

#### Phase 2: Data Migration
```python
# Phase 2: Migrate core data
# Duration: 5-7 days

class MigrationPhase2:
    """Phase 2: Core data migration"""

    def migrate_products(self):
        """Migrate products and variants"""
        # 1. Map legacy products to new structure
        # 2. Create store associations
        # 3. Migrate product categories
        # 4. Migrate product images
        # 5. Set up inventory records

        legacy_products = LegacyProduct.objects.all()

        for legacy_product in legacy_products:
            # Determine store (default to first store or create mapping)
            store = self.get_store_for_legacy_product(legacy_product)

            # Create new product
            new_product = Product.objects.create(
                store=store,
                title=legacy_product.name,
                slug=self.generate_slug(legacy_product.name),
                sku=legacy_product.sku or self.generate_sku(legacy_product),
                description=legacy_product.description or '',
                status=self.map_status(legacy_product.status),
                created_by=self.get_created_by(legacy_product),
                created_at=legacy_product.created_at,
                updated_at=legacy_product.updated_at
            )

            # Migrate variants
            self.migrate_variants(legacy_product, new_product)

            # Migrate categories
            self.migrate_product_categories(legacy_product, new_product)

            # Migrate images
            self.migrate_product_images(legacy_product, new_product)

    def migrate_variants(self, legacy_product, new_product):
        """Migrate product variants"""
        for legacy_variant in legacy_product.variants.all():
            ProductVariant.objects.create(
                product=new_product,
                title=legacy_variant.name or 'Default',
                sku=legacy_variant.sku or f"{new_product.sku}-VAR",
                price=legacy_variant.price or Decimal('0.00'),
                compare_at_price=legacy_variant.compare_price,
                cost_price=legacy_variant.cost_price,
                weight=legacy_variant.weight,
                inventory_quantity=legacy_variant.stock or 0,
                inventory_policy='deny' if legacy_variant.track_stock else 'ignore',
                option1=legacy_variant.option1,
                option2=legacy_variant.option2,
                option3=legacy_variant.option3
            )

    def migrate_orders(self):
        """Migrate orders and order items"""
        legacy_orders = LegacyOrder.objects.all()

        for legacy_order in legacy_orders:
            # Get or create customer
            customer = self.get_or_create_customer(legacy_order)

            # Determine store
            store = self.get_store_for_legacy_order(legacy_order)

            # Create new order
            new_order = Order.objects.create(
                store=store,
                customer=customer,
                order_number=legacy_order.order_number or self.generate_order_number(),
                status=self.map_order_status(legacy_order.status),
                payment_status=self.map_payment_status(legacy_order.payment_status),
                fulfillment_status=self.map_fulfillment_status(legacy_order.fulfillment_status),
                currency=legacy_order.currency or 'USD',
                subtotal=legacy_order.subtotal or Decimal('0.00'),
                tax=legacy_order.tax or Decimal('0.00'),
                shipping=legacy_order.shipping or Decimal('0.00'),
                discount=legacy_order.discount or Decimal('0.00'),
                total=legacy_order.total or Decimal('0.00'),
                billing_address=self.migrate_address(legacy_order.billing_address),
                shipping_address=self.migrate_address(legacy_order.shipping_address),
                notes=legacy_order.notes,
                created_at=legacy_order.created_at,
                updated_at=legacy_order.updated_at
            )

            # Migrate order items
            self.migrate_order_items(legacy_order, new_order)

    def migrate_customers(self):
        """Migrate customer data"""
        legacy_customers = LegacyCustomer.objects.all()

        for legacy_customer in legacy_customers:
            # Get or create GlobalUser
            user = self.get_or_create_user(legacy_customer)

            # Create new customer
            customer = Customer.objects.create(
                user=user,
                first_name=legacy_customer.first_name,
                last_name=legacy_customer.last_name,
                email=legacy_customer.email,
                phone=legacy_customer.phone,
                date_of_birth=legacy_customer.date_of_birth,
                gender=legacy_customer.gender,
                email_marketing=legacy_customer.email_marketing,
                sms_marketing=legacy_customer.sms_marketing,
                total_spent=legacy_customer.total_spent or Decimal('0.00'),
                order_count=legacy_customer.order_count or 0,
                last_order_at=legacy_customer.last_order_at,
                default_billing_address=self.migrate_address(legacy_customer.billing_address),
                default_shipping_address=self.migrate_address(legacy_customer.shipping_address),
                created_at=legacy_customer.created_at,
                updated_at=legacy_customer.updated_at
            )
```

#### Phase 3: Data Validation and Cleanup
```python
# Phase 3: Validation and cleanup
# Duration: 2-3 days

class MigrationPhase3:
    """Phase 3: Data validation and cleanup"""

    def validate_data_integrity(self):
        """Validate migrated data integrity"""
        validation_errors = []

        # Validate products
        for product in Product.objects.all():
            if not product.store:
                validation_errors.append(f"Product {product.id} missing store")

            if not product.variants.exists():
                validation_errors.append(f"Product {product.id} has no variants")

            if not product.slug:
                validation_errors.append(f"Product {product.id} missing slug")

        # Validate orders
        for order in Order.objects.all():
            if not order.customer:
                validation_errors.append(f"Order {order.id} missing customer")

            if not order.store:
                validation_errors.append(f"Order {order.id} missing store")

            if not order.items.exists():
                validation_errors.append(f"Order {order.id} has no items")

        return validation_errors

    def cleanup_legacy_data(self):
        """Clean up legacy data after successful migration"""
        # Archive legacy tables
        # Create backup
        # Remove unused fields
        pass

    def update_references(self):
        """Update system references to new models"""
        # Update foreign key references
        # Update API endpoints
        # Update admin configurations
        pass
```

### 8.3 Data Mapping Functions

#### Status Mapping
```python
class StatusMapper:
    """Map legacy status values to new system"""

    PRODUCT_STATUS_MAP = {
        'active': 'published',
        'inactive': 'draft',
        'draft': 'draft',
        'published': 'published',
        'archived': 'archived',
        'deleted': 'deleted'
    }

    ORDER_STATUS_MAP = {
        'pending': 'pending',
        'processing': 'processing',
        'shipped': 'shipped',
        'delivered': 'delivered',
        'cancelled': 'cancelled',
        'refunded': 'refunded'
    }

    PAYMENT_STATUS_MAP = {
        'pending': 'pending',
        'paid': 'paid',
        'failed': 'failed',
        'refunded': 'refunded',
        'partially_refunded': 'partially_refunded'
    }

    FULFILLMENT_STATUS_MAP = {
        'unfulfilled': 'unfulfilled',
        'partial': 'partial',
        'fulfilled': 'fulfilled',
        'restocked': 'restocked'
    }

    @classmethod
    def map_product_status(cls, legacy_status):
        """Map legacy product status"""
        return cls.PRODUCT_STATUS_MAP.get(legacy_status, 'draft')

    @classmethod
    def map_order_status(cls, legacy_status):
        """Map legacy order status"""
        return cls.ORDER_STATUS_MAP.get(legacy_status, 'pending')

    @classmethod
    def map_payment_status(cls, legacy_status):
        """Map legacy payment status"""
        return cls.PAYMENT_STATUS_MAP.get(legacy_status, 'pending')

    @classmethod
    def map_fulfillment_status(cls, legacy_status):
        """Map legacy fulfillment status"""
        return cls.FULFILLMENT_STATUS_MAP.get(legacy_status, 'unfulfilled')
```

#### Address Migration
```python
class AddressMapper:
    """Migrate address data"""

    @staticmethod
    def migrate_address(legacy_address):
        """Migrate legacy address to new format"""
        if not legacy_address:
            return {}

        return {
            'first_name': legacy_address.first_name,
            'last_name': legacy_address.last_name,
            'company': legacy_address.company,
            'street': legacy_address.address1,
            'street2': legacy_address.address2,
            'city': legacy_address.city,
            'state': legacy_address.state,
            'country': legacy_address.country,
            'postal_code': legacy_address.postal_code,
            'phone': legacy_address.phone
        }
```

### 8.4 Migration Commands

#### Management Command
```python
# ecommerce/management/commands/migrate_ecommerce.py
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from progress.bar import Bar

class Command(BaseCommand):
    help = 'Migrate ecommerce data from legacy system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--phase',
            type=int,
            choices=[1, 2, 3],
            help='Migration phase to run'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run migration without making changes'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Batch size for data processing'
        )

    def handle(self, *args, **options):
        phase = options.get('phase')
        dry_run = options.get('dry_run', False)
        batch_size = options.get('batch_size', 1000)

        if phase == 1:
            self.run_phase_1(dry_run)
        elif phase == 2:
            self.run_phase_2(dry_run, batch_size)
        elif phase == 3:
            self.run_phase_3(dry_run)
        else:
            self.run_full_migration(dry_run, batch_size)

    def run_phase_1(self, dry_run):
        """Run phase 1: Infrastructure setup"""
        self.stdout.write("Starting Phase 1: Infrastructure setup")

        if dry_run:
            self.stdout.write("DRY RUN: No changes will be made")

        # Create new models
        # Set up store scoping
        # Create migration utilities

        self.stdout.write(self.style.SUCCESS("Phase 1 completed"))

    def run_phase_2(self, dry_run, batch_size):
        """Run phase 2: Data migration"""
        self.stdout.write("Starting Phase 2: Data migration")

        if dry_run:
            self.stdout.write("DRY RUN: No changes will be made")

        # Migrate products
        self.migrate_products(dry_run, batch_size)

        # Migrate customers
        self.migrate_customers(dry_run, batch_size)

        # Migrate orders
        self.migrate_orders(dry_run, batch_size)

        # Migrate inventory
        self.migrate_inventory(dry_run, batch_size)

        self.stdout.write(self.style.SUCCESS("Phase 2 completed"))

    def run_phase_3(self, dry_run):
        """Run phase 3: Validation and cleanup"""
        self.stdout.write("Starting Phase 3: Validation and cleanup")

        if dry_run:
            self.stdout.write("DRY RUN: No changes will be made")

        # Validate data integrity
        errors = self.validate_migration()

        if errors:
            self.stdout.write(self.style.ERROR("Validation errors found:"))
            for error in errors:
                self.stdout.write(f"  - {error}")
        else:
            self.stdout.write(self.style.SUCCESS("No validation errors found"))

        if not dry_run and not errors:
            # Cleanup legacy data
            self.cleanup_legacy_data()

            # Update references
            self.update_references()

        self.stdout.write(self.style.SUCCESS("Phase 3 completed"))

    def migrate_products(self, dry_run, batch_size):
        """Migrate products in batches"""
        from ecommerce.migration import ProductMigrator

        migrator = ProductMigrator(dry_run=dry_run)

        legacy_products = LegacyProduct.objects.all()
        total = legacy_products.count()

        bar = Bar('Migrating products', max=total)

        for i in range(0, total, batch_size):
            batch = legacy_products[i:i + batch_size]
            migrator.migrate_batch(batch)
            bar.next(len(batch))

        bar.finish()
```

### 8.5 Rollback Strategy

#### Rollback Planning
```python
class MigrationRollback:
    """Rollback strategy for failed migration"""

    def __init__(self):
        self.backup_created = False
        self.rollback_points = []

    def create_backup(self):
        """Create full database backup before migration"""
        # 1. Backup legacy tables
        # 2. Create migration checkpoint
        # 3. Document current state

        self.backup_created = True
        return True

    def create_rollback_point(self, phase, description):
        """Create rollback point for each phase"""
        rollback_point = {
            'phase': phase,
            'description': description,
            'timestamp': timezone.now(),
            'tables_backed_up': [],
            'data_counts': {}
        }

        self.rollback_points.append(rollback_point)
        return rollback_point

    def rollback_to_phase(self, target_phase):
        """Rollback to specific phase"""
        if not self.backup_created:
            raise Exception("No backup available for rollback")

        # Find rollback point
        rollback_point = None
        for point in reversed(self.rollback_points):
            if point['phase'] <= target_phase:
                rollback_point = point
                break

        if not rollback_point:
            raise Exception(f"No rollback point found for phase {target_phase}")

        # Execute rollback
        self.execute_rollback(rollback_point)

        return True

    def execute_rollback(self, rollback_point):
        """Execute rollback to specific point"""
        # 1. Drop new tables
        # 2. Restore legacy tables
        # 3. Restore data counts
        # 4. Verify integrity

        pass
```

### 8.6 Testing Migration

#### Migration Test Suite
```python
# tests/test_migration.py
import pytest
from django.test import TestCase
from django.core.management import call_command
from ecommerce.migration import MigrationPhase1, MigrationPhase2, MigrationPhase3
from ecommerce.models import Product, Order, Customer

class MigrationTest(TestCase):
    def setUp(self):
        """Set up test legacy data"""
        self.create_legacy_data()

    def create_legacy_data(self):
        """Create test legacy data"""
        # Create legacy products
        # Create legacy customers
        # Create legacy orders
        pass

    def test_phase_1_migration(self):
        """Test phase 1 migration"""
        migrator = MigrationPhase1()
        migrator.create_new_models()
        migrator.setup_store_scoping()

        # Verify models were created
        assert Product.objects.count() == 0  # Should be empty initially
        assert Order.objects.count() == 0
        assert Customer.objects.count() == 0

    def test_phase_2_migration(self):
        """Test phase 2 data migration"""
        # Run phase 1 first
        phase1 = MigrationPhase1()
        phase1.create_new_models()
        phase1.setup_store_scoping()

        # Run phase 2
        phase2 = MigrationPhase2()
        phase2.migrate_products()
        phase2.migrate_customers()
        phase2.migrate_orders()

        # Verify data was migrated
        assert Product.objects.count() > 0
        assert Customer.objects.count() > 0
        assert Order.objects.count() > 0

    def test_data_integrity(self):
        """Test migrated data integrity"""
        # Run full migration
        self.run_full_migration()

        # Test product integrity
        for product in Product.objects.all():
            assert product.store is not None
            assert product.slug is not None
            assert product.variants.exists()

        # Test order integrity
        for order in Order.objects.all():
            assert order.customer is not None
            assert order.store is not None
            assert order.items.exists()

    def test_migration_command(self):
        """Test migration management command"""
        # Test dry run
        call_command('migrate_ecommerce', '--phase=1', '--dry-run')

        # Test actual migration
        call_command('migrate_ecommerce', '--phase=1')

        # Verify phase 1 completion
        assert Product.objects.count() == 0  # Models created but no data yet

    def run_full_migration(self):
        """Run complete migration for testing"""
        phase1 = MigrationPhase1()
        phase1.create_new_models()
        phase1.setup_store_scoping()

        phase2 = MigrationPhase2()
        phase2.migrate_products()
        phase2.migrate_customers()
        phase2.migrate_orders()

        phase3 = MigrationPhase3()
        errors = phase3.validate_data_integrity()

        assert len(errors) == 0, f"Migration validation errors: {errors}"
```

### 8.7 Performance Considerations

#### Large Dataset Handling
```python
class PerformanceOptimizedMigration:
    """Optimized migration for large datasets"""

    def __init__(self, batch_size=1000):
        self.batch_size = batch_size
        self.memory_limit = 1024 * 1024 * 1024  # 1GB

    def migrate_large_dataset(self):
        """Migrate large datasets efficiently"""
        # Use bulk_create for faster inserts
        # Use iterator() to reduce memory usage
        # Disable indexes during migration
        # Use transactions for batch operations

        with transaction.atomic():
            # Disable constraints temporarily
            self.disable_constraints()

            try:
                # Migrate in batches
                self.migrate_in_batches()

                # Rebuild indexes
                self.rebuild_indexes()

            finally:
                # Re-enable constraints
                self.enable_constraints()

    def migrate_in_batches(self):
        """Migrate data in batches to manage memory"""
        queryset = LegacyProduct.objects.all()

        batch = []
        for obj in queryset.iterator():
            batch.append(obj)

            if len(batch) >= self.batch_size:
                self.process_batch(batch)
                batch = []

        # Process remaining items
        if batch:
            self.process_batch(batch)

    def process_batch(self, batch):
        """Process a batch of objects"""
        # Transform data
        transformed = [self.transform_object(obj) for obj in batch]

        # Bulk create
        Product.objects.bulk_create(transformed, batch_size=self.batch_size)

        # Clear memory
        del batch
        del transformed
```

### 8.8 Monitoring and Logging

#### Migration Monitoring
```python
class MigrationMonitor:
    """Monitor migration progress and performance"""

    def __init__(self):
        self.start_time = timezone.now()
        self.metrics = {
            'records_processed': 0,
            'errors': 0,
            'warnings': 0,
            'memory_usage': 0,
            'processing_time': 0
        }

    def log_progress(self, phase, current, total, message=""):
        """Log migration progress"""
        percentage = (current / total) * 100 if total > 0 else 0

        log_message = (
            f"Migration Phase {phase}: {current}/{total} "
            f"({percentage:.1f}%) - {message}"
        )

        self.stdout.write(log_message)

        # Log to file
        with open('migration.log', 'a') as f:
            f.write(f"{timezone.now()}: {log_message}\n")

    def track_performance(self, operation, start_time, end_time):
        """Track operation performance"""
        duration = end_time - start_time
        self.metrics['processing_time'] += duration.total_seconds()

        performance_log = (
            f"Operation: {operation}, "
            f"Duration: {duration.total_seconds():.2f}s"
        )

        with open('migration_performance.log', 'a') as f:
            f.write(f"{timezone.now()}: {performance_log}\n")

    def generate_report(self):
        """Generate migration completion report"""
        end_time = timezone.now()
        total_duration = end_time - self.start_time

        report = {
            'start_time': self.start_time,
            'end_time': end_time,
            'total_duration': total_duration,
            'metrics': self.metrics,
            'success': self.metrics['errors'] == 0
        }

        with open('migration_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)

        return report
```

### 8.9 Post-Migration Tasks

#### Data Verification
```python
class PostMigrationTasks:
    """Tasks to complete after migration"""

    def verify_data_counts(self):
        """Verify data counts match legacy system"""
        legacy_counts = {
            'products': LegacyProduct.objects.count(),
            'customers': LegacyCustomer.objects.count(),
            'orders': LegacyOrder.objects.count()
        }

        new_counts = {
            'products': Product.objects.count(),
            'customers': Customer.objects.count(),
            'orders': Order.objects.count()
        }

        discrepancies = []
        for entity in legacy_counts:
            if legacy_counts[entity] != new_counts[entity]:
                discrepancies.append(
                    f"{entity}: legacy={legacy_counts[entity]}, "
                    f"new={new_counts[entity]}"
                )

        return discrepancies

    def update_sequences(self):
        """Update database sequences"""
        # Update primary key sequences
        # Update auto-increment values
        pass

    def create_indexes(self):
        """Create performance indexes"""
        # Create composite indexes
        # Create full-text search indexes
        pass

    def update_caches(self):
        """Update application caches"""
        # Clear Redis caches
        # Warm up frequently accessed data
        pass
```
# Ecommerce Improvement Suggestions

## 9. DFCMS Ecommerce Improvements

### 9.1 Current Issues Analysis

#### Data Model Issues
```python
# Current problems in dfcms ecommerce models

# 1. Missing Store Scoping
# Problem: Models don't have explicit store relationships
# Impact: Data isolation issues, multi-tenancy problems

# Current (Problematic):
class Product(models.Model):
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    # Missing store field

# Improved:
class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    # Store-scoped with proper isolation

# 2. Inconsistent Status Management
# Problem: Status fields use different values across models
# Impact: Confusing state management, difficult reporting

# Current (Inconsistent):
ORDER_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
]

PRODUCT_STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
]

# Improved (Consistent):
class StatusChoices:
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'
    DELETED = 'deleted'

# 3. Missing Business Logic Layer
# Problem: Business logic scattered across views and models
# Impact: Difficult to test, maintain, and reuse

# Current (Scattered):
# In views.py
def create_order(request):
    if request.method == 'POST':
        # Business logic mixed with view logic
        order = Order.objects.create(...)
        # Email sending logic here
        # Inventory update logic here
        # Payment processing logic here

# Improved (Centralized):
class OrderService:
    @staticmethod
    def create_order_from_cart(cart, billing_address, shipping_address):
        # Centralized business logic
        order = Order.objects.create(...)
        InventoryService.reserve_inventory(order)
        PaymentService.process_payment(order)
        EmailService.send_confirmation(order)
        return order
```

#### Performance Issues
```python
# Current performance problems

# 1. N+1 Query Problems
# Problem: Related objects fetched with multiple queries
# Impact: Slow page loads, high database load

# Current (Inefficient):
def get_product_list(request):
    products = Product.objects.all()
    result = []
    for product in products:
        # N+1 queries for each product's variants
        variants = product.variants.all()
        # N+1 queries for each product's images
        images = product.images.all()
        result.append({
            'product': product,
            'variants': variants,
            'images': images
        })

# Improved (Optimized):
def get_product_list(request):
    products = Product.objects.select_related('store').prefetch_related(
        'variants',
        'images',
        'categories'
    ).all()

    # Single query with all related data
    return products

# 2. Missing Database Indexes
# Problem: No indexes on frequently queried fields
# Impact: Slow query performance

# Current (Unindexed):
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    # No indexes defined

# Improved (Indexed):
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status', 'created_at']),
        ]

# 3. Inefficient Cart Operations
# Problem: Cart recalculates totals on every access
# Impact: Slow cart page loads

# Current (Inefficient):
class Cart(models.Model):
    def get_total(self):
        total = 0
        for item in self.items.all():
            total += item.quantity * item.unit_price
        return total

# Improved (Cached):
class Cart(models.Model):
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def get_total(self):
        return self.total

    def recalculate_totals(self):
        self.subtotal = sum(item.get_total() for item in self.items.all())
        self.tax = self.calculate_tax()
        self.shipping = self.calculate_shipping()
        self.total = self.subtotal + self.tax + self.shipping
        self.save()
```

### 9.2 Architecture Improvements

#### Service Layer Implementation
```python
# Proposed service layer architecture

# 1. Product Service
class ProductService:
    """Centralized product business logic"""

    @staticmethod
    def create_product(store, user, data):
        """Create product with validation and logging"""
        # Validate data
        ProductService.validate_product_data(data)

        # Create product
        product = Product.objects.create(
            store=store,
            title=data['title'],
            slug=ProductService.generate_unique_slug(store, data['title']),
            sku=data['sku'],
            created_by=user
        )

        # Create variants
        if 'variants' in data:
            ProductService.create_variants(product, data['variants'])

        # Setup inventory
        ProductService.setup_inventory(product)

        # Log creation
        log_event_async(
            user=user,
            store=store,
            action='product_created',
            object_type='product',
            object_id=product.id
        )

        return product

    @staticmethod
    def update_product_inventory(product, variant, quantity_change, reason):
        """Update inventory with audit trail"""
        inventory = Inventory.objects.get_or_create(
            store=product.store,
            product=product,
            variant=variant
        )[0]

        old_quantity = inventory.quantity
        inventory.quantity += quantity_change
        inventory.save()

        # Create transaction record
        InventoryTransaction.objects.create(
            inventory=inventory,
            type='adjustment',
            quantity=quantity_change,
            notes=reason
        )

        # Log change
        log_event_async(
            user=None,
            store=product.store,
            action='inventory_updated',
            object_type='inventory',
            object_id=inventory.id,
            details={
                'old_quantity': old_quantity,
                'new_quantity': inventory.quantity,
                'change': quantity_change,
                'reason': reason
            }
        )

# 2. Order Service
class OrderService:
    """Centralized order business logic"""

    @staticmethod
    def process_order_payment(order, payment_method, payment_data):
        """Process payment with fraud detection"""
        # Fraud check
        fraud_analysis = FraudDetectionService.analyze_order(order)
        if fraud_analysis['risk_score'] > 80:
            order.status = 'flagged'
            order.save()
            raise ValidationError("Order flagged for review")

        # Process payment
        payment = PaymentService.process_payment(
            order, payment_method, payment_data
        )

        # Update order status
        if payment.status == 'completed':
            order.payment_status = 'paid'
            order.status = 'confirmed'
            order.save()

            # Send confirmation
            EmailService.send_order_confirmation(order)

            # Update customer stats
            order.customer.update_statistics()

        return payment

# 3. Cart Service
class CartService:
    """Centralized cart business logic"""

    @staticmethod
    def add_item_with_validation(cart, product, variant, quantity):
        """Add item with inventory validation"""
        # Check inventory
        inventory = Inventory.objects.filter(
            store=cart.store,
            product=product,
            variant=variant
        ).first()

        if not inventory or inventory.available < quantity:
            raise ValidationError("Insufficient inventory")

        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity

        # Reserve inventory
        inventory.reserve(cart_item.quantity)

        # Recalculate cart totals
        cart.recalculate_totals()

        return cart_item
```

#### Event-Driven Architecture
```python
# Proposed event system for better decoupling

# 1. Event Definitions
class EcommerceEvents:
    PRODUCT_CREATED = 'product.created'
    PRODUCT_UPDATED = 'product.updated'
    PRODUCT_DELETED = 'product.deleted'

    ORDER_CREATED = 'order.created'
    ORDER_CONFIRMED = 'order.confirmed'
    ORDER_SHIPPED = 'order.shipped'
    ORDER_CANCELLED = 'order.cancelled'

    PAYMENT_COMPLETED = 'payment.completed'
    PAYMENT_FAILED = 'payment.failed'

    INVENTORY_LOW = 'inventory.low'
    INVENTORY_OUT_OF_STOCK = 'inventory.out_of_stock'

# 2. Event Dispatcher
class EventDispatcher:
    @staticmethod
    def dispatch(event_name, data):
        """Dispatch event to all registered handlers"""
        handlers = EventHandler.get_handlers(event_name)

        for handler in handlers:
            try:
                handler.handle(data)
            except Exception as e:
                # Log error but don't stop other handlers
                log_error(f"Event handler failed: {e}")

# 3. Event Handlers
class InventoryEventHandler:
    @staticmethod
    def handle_order_created(data):
        """Handle order created event"""
        order = data['order']

        # Reserve inventory
        for item in order.items.all():
            inventory = Inventory.objects.filter(
                product=item.product,
                variant=item.variant
            ).first()

            if inventory:
                inventory.reserve(item.quantity)

                # Check for low stock
                if inventory.available <= 5:
                    EventDispatcher.dispatch(
                        EcommerceEvents.INVENTORY_LOW,
                        {'inventory': inventory}
                    )

class EmailEventHandler:
    @staticmethod
    def handle_order_created(data):
        """Send order confirmation email"""
        order = data['order']
        send_order_confirmation_email.delay(order.id)

    @staticmethod
    def handle_inventory_low(data):
        """Send low stock alert"""
        inventory = data['inventory']
        send_low_stock_alert_email.delay(inventory.id)

# 4. Register handlers
EventHandler.register(EcommerceEvents.ORDER_CREATED, InventoryEventHandler)
EventHandler.register(EcommerceEvents.ORDER_CREATED, EmailEventHandler)
EventHandler.register(EcommerceEvents.INVENTORY_LOW, EmailEventHandler)
```

### 9.3 Feature Enhancements

#### Advanced Product Variants
```python
# Current limitations and improvements

# Current (Basic):
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory_quantity = models.IntegerField(default=0)

# Improved (Advanced):
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Inventory
    inventory_quantity = models.IntegerField(default=0)
    inventory_policy = models.CharField(
        max_length=20,
        choices=[
            ('deny', 'Deny'),
            ('continue', 'Continue'),
            ('backorder', 'Backorder')
        ],
        default='deny'
    )

    # Physical attributes
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Variant options (structured)
    option1 = models.CharField(max_length=100, blank=True)
    option2 = models.CharField(max_length=100, blank=True)
    option3 = models.CharField(max_length=100, blank=True)

    # Position for ordering
    position = models.IntegerField(default=0)

    # Metadata
    barcode = models.CharField(max_length=50, blank=True)
    requires_shipping = models.BooleanField(default=True)
    taxable = models.BooleanField(default=True)

    class Meta:
        ordering = ['position']
        indexes = [
            models.Index(fields=['product', 'position']),
            models.Index(fields=['sku']),
            models.Index(fields=['inventory_quantity']),
        ]

# Variant Option Management
class VariantOption(models.Model):
    """Structured variant options"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variant_options')
    name = models.CharField(max_length=50)  # e.g., "Size", "Color"
    position = models.IntegerField(default=0)

    class Meta:
        unique_together = ['product', 'name']
        ordering = ['position']

class VariantOptionValue(models.Model):
    """Values for variant options"""
    option = models.ForeignKey(VariantOption, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100)  # e.g., "Small", "Red"
    position = models.IntegerField(default=0)

    class Meta:
        unique_together = ['option', 'value']
        ordering = ['position']
```

#### Smart Collections
```python
# Current: Manual collections only
# Improved: Smart collections with rules

class Collection(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ForeignKey('media.MediaFile', on_delete=models.SET_NULL, null=True, blank=True)

    # Smart collection settings
    is_smart = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Sorting
    sort_order = models.CharField(
        max_length=20,
        choices=[
            ('manual', 'Manual'),
            ('price_low_high', 'Price: Low to High'),
            ('price_high_low', 'Price: High to Low'),
            ('created_at', 'Created Date'),
            ('title', 'Title'),
            ('best_selling', 'Best Selling')
        ],
        default='manual'
    )

    # Metadata
    created_by = models.ForeignKey(GlobalUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['store', 'slug']

class CollectionCondition(models.Model):
    """Rules for smart collections"""
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='conditions')

    # Condition definition
    field = models.CharField(
        max_length=50,
        choices=[
            ('title', 'Title'),
            ('type', 'Product Type'),
            ('vendor', 'Vendor'),
            ('price', 'Price'),
            ('compare_at_price', 'Compare at Price'),
            ('inventory', 'Inventory'),
            ('weight', 'Weight'),
            ('tag', 'Tag'),
            ('category', 'Category')
        ]
    )

    operator = models.CharField(
        max_length=20,
        choices=[
            ('equals', 'Equals'),
            ('not_equals', 'Does not equal'),
            ('contains', 'Contains'),
            ('not_contains', 'Does not contain'),
            ('starts_with', 'Starts with'),
            ('ends_with', 'Ends with'),
            ('greater_than', 'Greater than'),
            ('less_than', 'Less than'),
            ('between', 'Between'),
            ('in', 'In list'),
            ('not_in', 'Not in list')
        ]
    )

    value = models.JSONField()  # Flexible value storage
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ['position']

# Smart collection service
class SmartCollectionService:
    @staticmethod
    def get_products_for_collection(collection):
        """Get products matching smart collection rules"""
        if not collection.is_smart:
            return collection.products.all()

        queryset = Product.objects.filter(store=collection.store, status='published')

        for condition in collection.conditions.all():
            queryset = SmartCollectionService.apply_condition(queryset, condition)

        # Apply sorting
        queryset = SmartCollectionService.apply_sorting(queryset, collection.sort_order)

        return queryset.distinct()

    @staticmethod
    def apply_condition(queryset, condition):
        """Apply single condition to queryset"""
        field = condition.field
        operator = condition.operator
        value = condition.value

        if field == 'title':
            if operator == 'contains':
                return queryset.filter(title__icontains=value)
            elif operator == 'equals':
                return queryset.filter(title__iexact=value)
            # ... other operators

        elif field == 'price':
            if operator == 'greater_than':
                return queryset.filter(variants__price__gt=value)
            elif operator == 'less_than':
                return queryset.filter(variants__price__lt=value)
            elif operator == 'between':
                return queryset.filter(
                    variants__price__gte=value[0],
                    variants__price__lte=value[1]
                )

        elif field == 'category':
            if operator == 'equals':
                return queryset.filter(categories__id=value)
            elif operator == 'in':
                return queryset.filter(categories__id__in=value)

        return queryset
```

#### Advanced Discount System
```python
# Current: Basic coupons only
# Improved: Advanced discount engine

class DiscountRule(models.Model):
    """Advanced discount rules"""
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Rule configuration
    rule_type = models.CharField(
        max_length=20,
        choices=[
            ('cart_total', 'Cart Total'),
            ('product_specific', 'Product Specific'),
            ('category_specific', 'Category Specific'),
            ('customer_specific', 'Customer Specific'),
            ('buy_x_get_y', 'Buy X Get Y'),
            ('bundle', 'Bundle Discount')
        ]
    )

    # Conditions
    conditions = models.JSONField(default=dict)

    # Discount calculation
    discount_type = models.CharField(
        max_length=20,
        choices=[
            ('percentage', 'Percentage'),
            ('fixed_amount', 'Fixed Amount'),
            ('fixed_price', 'Fixed Price'),
            ('free_shipping', 'Free Shipping')
        ]
    )

    discount_value = models.DecimalField(max_digits=10, decimal_places=2)

    # Limits and restrictions
    usage_limit = models.IntegerField(null=True, blank=True)
    usage_limit_per_customer = models.IntegerField(null=True, blank=True)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Timing
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()

    # Status
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(GlobalUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class DiscountEngine:
    """Advanced discount calculation engine"""

    @staticmethod
    def calculate_discounts(cart, customer=None):
        """Calculate all applicable discounts for cart"""
        discounts = []
        total_discount = Decimal('0.00')

        # Get applicable rules
        rules = DiscountEngine.get_applicable_rules(cart.store, cart, customer)

        for rule in rules:
            discount = DiscountEngine.calculate_rule_discount(rule, cart, customer)
            if discount['amount'] > 0:
                discounts.append(discount)
                total_discount += discount['amount']

        return {
            'discounts': discounts,
            'total_discount': total_discount,
            'final_total': cart.get_total() - total_discount
        }

    @staticmethod
    def get_applicable_rules(store, cart, customer):
        """Get rules that apply to this cart"""
        rules = DiscountRule.objects.filter(
            store=store,
            is_active=True,
            starts_at__lte=timezone.now(),
            ends_at__gte=timezone.now()
        )

        applicable_rules = []

        for rule in rules:
            if DiscountEngine.rule_applies(rule, cart, customer):
                applicable_rules.append(rule)

        return applicable_rules

    @staticmethod
    def rule_applies(rule, cart, customer):
        """Check if rule applies to cart"""
        conditions = rule.conditions

        # Check minimum order amount
        if rule.minimum_order_amount > 0:
            if cart.get_subtotal() < rule.minimum_order_amount:
                return False

        # Check usage limits
        if rule.usage_limit:
            if rule.used_count >= rule.usage_limit:
                return False

        if rule.usage_limit_per_customer and customer:
            customer_usage = Order.objects.filter(
                customer=customer,
                discounts__rule=rule
            ).count()
            if customer_usage >= rule.usage_limit_per_customer:
                return False

        # Check specific conditions based on rule type
        if rule.rule_type == 'cart_total':
            return DiscountEngine.check_cart_total_conditions(rule, cart)
        elif rule.rule_type == 'product_specific':
            return DiscountEngine.check_product_conditions(rule, cart)
        elif rule.rule_type == 'customer_specific':
            return DiscountEngine.check_customer_conditions(rule, customer)

        return True

    @staticmethod
    def calculate_rule_discount(rule, cart, customer):
        """Calculate discount amount for a specific rule"""
        if rule.discount_type == 'percentage':
            discount_amount = cart.get_subtotal() * (rule.discount_value / 100)
        elif rule.discount_type == 'fixed_amount':
            discount_amount = min(rule.discount_value, cart.get_subtotal())
        elif rule.discount_type == 'free_shipping':
            discount_amount = cart.get_shipping()
        else:
            discount_amount = Decimal('0.00')

        return {
            'rule_id': rule.id,
            'rule_name': rule.name,
            'discount_type': rule.discount_type,
            'discount_value': rule.discount_value,
            'amount': discount_amount
        }
```

### 9.4 User Experience Improvements

#### Progressive Web App Features
```python
# PWA features for better mobile experience

# 1. Offline Cart Support
class OfflineCartService:
    """Service for offline cart functionality"""

    @staticmethod
    def sync_cart_when_online(user, offline_cart_data):
        """Sync offline cart when user comes online"""
        try:
            cart = CartService.get_cart_for_user(user)

            for item_data in offline_cart_data['items']:
                # Merge offline items with online cart
                CartService.add_item_with_validation(
                    cart,
                    item_data['product_id'],
                    item_data.get('variant_id'),
                    item_data['quantity']
                )

            return {'status': 'synced', 'cart_id': cart.id}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

# 2. Push Notifications for Order Updates
class PushNotificationService:
    """Push notifications for order status updates"""

    @staticmethod
    def send_order_update_notification(order, status):
        """Send push notification for order update"""
        if order.customer.user.push_notification_token:
            message = {
                'title': f'Order {order.order_number} Updated',
                'body': f'Your order status is now: {status}',
                'icon': '/static/icons/order-icon.png',
                'badge': '/static/icons/badge.png',
                'data': {
                    'order_id': order.id,
                    'status': status
                },
                'actions': [
                    {
                        'action': 'view',
                        'title': 'View Order'
                    }
                ]
            }

            send_push_notification.delay(
                order.customer.user.push_notification_token,
                message
            )

# 3. One-Click Reorder
class ReorderService:
    """Service for quick reordering"""

    @staticmethod
    def create_reorder(order, user):
        """Create new order from existing order"""
        new_order = Order.objects.create(
            store=order.store,
            customer=user.customer,
            billing_address=order.billing_address,
            shipping_address=order.shipping_address,
            status='draft'
        )

        # Copy order items
        for item in order.items.all():
            OrderItem.objects.create(
                order=new_order,
                product=item.product,
                variant=item.variant,
                title=item.title,
                sku=item.sku,
                quantity=item.quantity,
                unit_price=item.product.get_current_price(),
                total_price=item.product.get_current_price() * item.quantity
            )

        # Recalculate totals
        new_order.calculate_totals()
        new_order.save()

        return new_order
```

#### Advanced Search and Filtering
```python
# Enhanced search capabilities

class ProductSearchService:
    """Advanced product search with filters"""

    @staticmethod
    def search_products(store, query, filters=None, sort=None):
        """Advanced product search"""
        queryset = Product.objects.filter(
            store=store,
            status='published'
        )

        # Text search
        if query:
            queryset = queryset.filter(
                models.Q(title__icontains=query) |
                models.Q(description__icontains=query) |
                models.Q(sku__icontains=query) |
                models.Q(variants__sku__icontains=query) |
                models.Q(tags__contains=query)
            ).distinct()

        # Apply filters
        if filters:
            queryset = ProductSearchService.apply_filters(queryset, filters)

        # Apply sorting
        if sort:
            queryset = ProductSearchService.apply_sorting(queryset, sort)

        return queryset

    @staticmethod
    def apply_filters(queryset, filters):
        """Apply search filters"""
        # Category filter
        if 'category' in filters:
            queryset = queryset.filter(categories__slug=filters['category'])

        # Price range filter
        if 'price_min' in filters:
            queryset = queryset.filter(variants__price__gte=filters['price_min'])
        if 'price_max' in filters:
            queryset = queryset.filter(variants__price__lte=filters['price_max'])

        # In stock filter
        if 'in_stock' in filters and filters['in_stock']:
            queryset = queryset.filter(
                variants__inventory_quantity__gt=0
            )

        # Attributes filter
        if 'attributes' in filters:
            for attr, value in filters['attributes'].items():
                queryset = queryset.filter(
                    attributes__contains={attr: value}
                )

        return queryset.distinct()

    @staticmethod
    def get_search_suggestions(store, query):
        """Get search suggestions for autocomplete"""
        suggestions = []

        # Product title suggestions
        title_matches = Product.objects.filter(
            store=store,
            status='published',
            title__icontains=query
        ).values_list('title', flat=True)[:5]

        suggestions.extend(title_matches)

        # Category suggestions
        category_matches = ProductCategory.objects.filter(
            store=store,
            name__icontains=query
        ).values_list('name', flat=True)[:3]

        suggestions.extend(category_matches)

        return list(set(suggestions))[:10]
```

### 9.5 Analytics and Reporting

#### Advanced Analytics
```python
# Enhanced analytics and reporting

class EcommerceAnalytics:
    """Advanced ecommerce analytics"""

    @staticmethod
    def get_sales_report(store, start_date, end_date):
        """Generate comprehensive sales report"""
        orders = Order.objects.filter(
            store=store,
            created_at__range=[start_date, end_date]
        )

        report = {
            'summary': {
                'total_orders': orders.count(),
                'total_revenue': orders.aggregate(
                    total=models.Sum('total')
                )['total'] or Decimal('0.00'),
                'average_order_value': orders.aggregate(
                    avg=models.Avg('total')
                )['avg'] or Decimal('0.00'),
                'conversion_rate': EcommerceAnalytics.calculate_conversion_rate(
                    store, start_date, end_date
                )
            },
            'daily_sales': EcommerceAnalytics.get_daily_sales(orders),
            'top_products': EcommerceAnalytics.get_top_products(orders),
            'customer_analysis': EcommerceAnalytics.get_customer_analysis(orders),
            'revenue_by_category': EcommerceAnalytics.get_revenue_by_category(orders)
        }

        return report

    @staticmethod
    def get_customer_lifetime_value(store):
        """Calculate customer lifetime value"""
        customers = Customer.objects.filter(
            orders__store=store
        ).distinct()

        clv_data = []
        for customer in customers:
            orders = Order.objects.filter(customer=customer, store=store)
            total_spent = orders.aggregate(total=models.Sum('total'))['total'] or 0
            order_count = orders.count()
            first_order = orders.order_by('created_at').first()
            last_order = orders.order_by('-created_at').first()

            if first_order and last_order:
                days_active = (last_order.created_at - first_order.created_at).days
                avg_order_value = total_spent / order_count if order_count > 0 else 0

                clv_data.append({
                    'customer_id': customer.id,
                    'customer_name': customer.get_full_name(),
                    'total_spent': total_spent,
                    'order_count': order_count,
                    'avg_order_value': avg_order_value,
                    'days_active': days_active,
                    'clv_per_day': total_spent / days_active if days_active > 0 else 0
                })

        return sorted(clv_data, key=lambda x: x['total_spent'], reverse=True)

    @staticmethod
    def get_inventory_turnover(store):
        """Calculate inventory turnover ratio"""
        inventory = Inventory.objects.filter(store=store)

        turnover_data = []
        for item in inventory:
            # Calculate cost of goods sold
            sold_quantity = OrderItem.objects.filter(
                product=item.product,
                variant=item.variant,
                order__created_at__gte=timezone.now() - timedelta(days=365)
            ).aggregate(total=models.Sum('quantity'))['total'] or 0

            # Calculate turnover
            avg_inventory = (item.quantity + sold_quantity) / 2
            turnover_rate = sold_quantity / avg_inventory if avg_inventory > 0 else 0

            turnover_data.append({
                'product': item.product.title,
                'variant': item.variant.title if item.variant else 'Default',
                'current_inventory': item.quantity,
                'sold_last_year': sold_quantity,
                'turnover_rate': turnover_rate,
                'days_of_supply': 365 / turnover_rate if turnover_rate > 0 else 999
            })

        return sorted(turnover_data, key=lambda x: x['turnover_rate'], reverse=True)
```

### 9.6 Performance Optimizations

#### Caching Strategy
```python
# Comprehensive caching strategy

class EcommerceCache:
    """Ecommerce-specific caching"""

    CACHE_KEYS = {
        'product_list': 'product_list:{store_id}:{page}',
        'product_detail': 'product_detail:{product_id}',
        'category_tree': 'category_tree:{store_id}',
        'cart_totals': 'cart_totals:{cart_id}',
        'search_results': 'search:{store_id}:{query_hash}'
    }

    CACHE_TIMEOUTS = {
        'product_list': 300,  # 5 minutes
        'product_detail': 600,  # 10 minutes
        'category_tree': 3600,  # 1 hour
        'cart_totals': 60,  # 1 minute
        'search_results': 180  # 3 minutes
    }

    @staticmethod
    def get_product_list(store_id, page=1):
        """Get cached product list"""
        cache_key = EcommerceCache.CACHE_KEYS['product_list'].format(
            store_id=store_id, page=page
        )

        products = cache.get(cache_key)

        if not products:
            products = Product.objects.filter(
                store_id=store_id,
                status='published'
            ).select_related('store').prefetch_related(
                'variants', 'images', 'categories'
            )

            cache.set(
                cache_key,
                products,
                EcommerceCache.CACHE_TIMEOUTS['product_list']
            )

        return products

    @staticmethod
    def invalidate_product_cache(product):
        """Invalidate product-related caches"""
        # Invalidate product detail
        cache.delete(
            EcommerceCache.CACHE_KEYS['product_detail'].format(
                product_id=product.id
            )
        )

        # Invalidate product list
        for page in range(1, 50):  # Invalidate first 50 pages
            cache.delete(
                EcommerceCache.CACHE_KEYS['product_list'].format(
                    store_id=product.store_id, page=page
                )
            )

        # Invalidate category tree
        cache.delete(
            EcommerceCache.CACHE_KEYS['category_tree'].format(
                store_id=product.store_id
            )
        )
```

### 9.7 Security Enhancements

#### Advanced Fraud Detection
```python
# Enhanced fraud detection system

class FraudDetectionEngine:
    """Advanced fraud detection"""

    @staticmethod
    def analyze_transaction(order, payment_data):
        """Comprehensive fraud analysis"""
        risk_score = 0
        risk_factors = []

        # 1. Order value analysis
        if order.total > 1000:
            risk_score += 15
            risk_factors.append('high_value_order')

        # 2. Customer behavior analysis
        customer_risk = FraudDetectionEngine.analyze_customer_behavior(order.customer)
        risk_score += customer_risk['score']
        risk_factors.extend(customer_risk['factors'])

        # 3. Geographic analysis
        geo_risk = FraudDetectionEngine.analyze_geographic_risk(
            order.billing_address, order.shipping_address
        )
        risk_score += geo_risk['score']
        risk_factors.extend(geo_risk['factors'])

        # 4. Payment method analysis
        payment_risk = FraudDetectionEngine.analyze_payment_method(payment_data)
        risk_score += payment_risk['score']
        risk_factors.extend(payment_risk['factors'])

        # 5. Device fingerprinting
        device_risk = FraudDetectionEngine.analyze_device_fingerprint(
            payment_data.get('device_fingerprint')
        )
        risk_score += device_risk['score']
        risk_factors.extend(device_risk['factors'])

        return {
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'recommendation': FraudDetectionEngine.get_recommendation(risk_score),
            'requires_review': risk_score > 70
        }

    @staticmethod
    def analyze_customer_behavior(customer):
        """Analyze customer behavior patterns"""
        risk_score = 0
        factors = []

        # New customer risk
        if customer.order_count == 0:
            risk_score += 20
            factors.append('new_customer')

        # Rapid ordering
        recent_orders = Order.objects.filter(
            customer=customer,
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).count()

        if recent_orders > 3:
            risk_score += 25
            factors.append('rapid_ordering')

        # Unusual order size
        if customer.total_spent > 0:
            avg_order_value = customer.total_spent / customer.order_count
            current_order = Order.objects.filter(customer=customer).last()

            if current_order and current_order.total > avg_order_value * 3:
                risk_score += 15
                factors.append('unusual_order_size')

        return {'score': risk_score, 'factors': factors}
```

### 9.8 Implementation Priority

#### Phase 1: Critical Issues (Week 1-2)
1. **Add store scoping to all models**
2. **Implement service layer for business logic**
3. **Fix N+1 query problems**
4. **Add database indexes**
5. **Implement proper error handling**

#### Phase 2: Feature Enhancements (Week 3-4)
1. **Advanced product variants**
2. **Smart collections**
3. **Enhanced discount system**
4. **Improved search functionality**
5. **Basic analytics dashboard**

#### Phase 3: Advanced Features (Week 5-6)
1. **Fraud detection system**
2. **Advanced caching**
3. **PWA features**
4. **Comprehensive analytics**
5. **Performance optimizations**

#### Phase 4: Polish and Testing (Week 7-8)
1. **Comprehensive testing**
2. **Documentation**
3. **Performance tuning**
4. **Security audit**
5. **User acceptance testing**
# Ecommerce AI Guidelines

## 10. AI Development Guidelines

### 10.1 What AI Can Do

#### Code Generation and Refactoring
```python
# ✅ AI CAN generate boilerplate code for:
# - Model definitions with standard fields
# - Serializer classes
# - Basic ViewSet structures
# - Migration files
# - Test templates

# Example: AI can generate this standard model structure
class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['store', 'slug']
        indexes = [
            models.Index(fields=['store', 'status']),
            models.Index(fields=['sku']),
        ]
```

#### Documentation Generation
```python
# ✅ AI CAN generate comprehensive documentation:
# - API endpoint documentation
# - Model field descriptions
# - Service method documentation
# - Code comments and docstrings

# Example: AI can generate this docstring
def calculate_order_totals(order):
    """
    Calculate order totals including subtotal, tax, shipping, and final total.

    Args:
        order (Order): The order instance to calculate totals for

    Returns:
        dict: Dictionary containing calculated totals:
            - subtotal (Decimal): Sum of all order items
            - tax (Decimal): Calculated tax amount
            - shipping (Decimal): Shipping cost
            - total (Decimal): Final total including all charges

    Raises:
        ValidationError: If order items are invalid or missing

    Example:
        >>> order = Order.objects.get(id=1)
        >>> totals = calculate_order_totals(order)
        >>> print(totals['total'])
        Decimal('129.99')
    """
    pass
```

#### Test Case Generation
```python
# ✅ AI CAN generate test cases for:
# - Model validation tests
# - API endpoint tests
# - Service method tests
# - Edge case scenarios

# Example: AI can generate this test structure
class ProductModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name="Test Store")
        self.user = User.objects.create_user(email="test@example.com")

    def test_product_creation_with_valid_data(self):
        """Test creating product with all required fields"""
        product = Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            created_by=self.user
        )

        assert product.title == "Test Product"
        assert product.status == "draft"
        assert product.store == self.store

    def test_product_slug_uniqueness_per_store(self):
        """Test that product slugs are unique within each store"""
        # Test implementation
        pass
```

#### Configuration and Setup
```python
# ✅ AI CAN generate configuration files:
# - Django settings
# - URL configurations
# - Admin registrations
# - Celery task definitions

# Example: AI can generate this admin configuration
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'sku', 'status', 'store', 'created_at']
    list_filter = ['status', 'store', 'created_at']
    search_fields = ['title', 'sku', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'sku', 'status')
        }),
        ('Details', {
            'fields': ('description', 'featured_image')
        }),
        ('Metadata', {
            'fields': ('store', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
```

#### Code Optimization Suggestions
```python
# ✅ AI CAN suggest performance optimizations:
# - Query optimization
# - Caching strategies
# - Database indexing
# - Memory usage improvements

# Example: AI can suggest this optimization
# BEFORE (N+1 query problem):
def get_products_with_variants():
    products = Product.objects.all()
    result = []
    for product in products:
        variants = product.variants.all()  # N+1 query
        result.append({'product': product, 'variants': variants})
    return result

# AFTER (Optimized with prefetch_related):
def get_products_with_variants():
    products = Product.objects.prefetch_related('variants').all()
    return [{'product': p, 'variants': list(p.variants.all())} for p in products]
```

### 10.2 What AI Cannot Do

#### Business Logic Implementation
```python
# ❌ AI CANNOT implement complex business logic without explicit requirements:
# - Tax calculation rules (vary by jurisdiction)
# - Shipping rate calculations (complex carrier integrations)
# - Inventory management policies (business-specific rules)
# - Discount validation logic (complex rule combinations)

# Example: AI should NOT implement this without detailed business rules:
def calculate_tax(order):
    # This requires specific tax rules for each jurisdiction
    # AI cannot know the specific tax rates, exemptions, or rules
    # Must be implemented by developer with business requirements
    pass

# ✅ INSTEAD, AI can provide a template:
def calculate_tax(order):
    """
    Calculate tax based on order shipping address and items.

    TODO: Implement specific tax calculation logic based on:
    - Shipping address jurisdiction
    - Product taxability
    - Tax exemptions
    - Tax rates from tax service API
    """
    tax_service = TaxService()
    return tax_service.calculate_tax(order)
```

#### Security Implementation
```python
# ❌ AI CANNOT implement security-critical code:
# - Payment processing (PCI compliance required)
# - Authentication and authorization (security policies)
# - Data encryption (specific algorithms and keys)
# - Fraud detection rules (business-specific thresholds)

# Example: AI should NOT implement payment processing:
def process_payment(order, payment_data):
    # This requires PCI compliance and specific payment gateway integration
    # AI cannot handle secure credential management
    # Must be implemented by security-conscious developer
    pass

# ✅ INSTEAD, AI can provide a secure structure:
def process_payment(order, payment_data):
    """
    Process payment using secure payment gateway.

    SECURITY NOTES:
    - Never store raw card data
    - Use tokenization for payment methods
    - Implement proper error handling
    - Log all payment attempts
    - Validate all input data
    """
    payment_gateway = PaymentGateway()
    return payment_gateway.process_payment(order, payment_data)
```

#### Database Schema Design
```python
# ❌ AI CANNOT design optimal database schema without understanding:
# - Data volume and growth patterns
# - Query performance requirements
# - Specific business relationships
# - Data integrity constraints

# Example: AI should NOT design this without requirements:
class Order(models.Model):
    # AI might suggest this structure, but it may not be optimal
    # for specific business needs, performance, or data volume
    customer_data = models.JSONField()  # Might be better normalized
    items = models.JSONField()  # Should be separate model for querying
    pass

# ✅ INSTEAD, AI can suggest normalized structure:
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    # Separate OrderItem model for better querying and indexing
    pass

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
```

#### Integration with External Services
```python
# ❌ AI CANNOT implement external service integrations without:
# - API credentials and authentication
# - Specific endpoint URLs and parameters
# - Error handling requirements
# - Rate limiting and retry logic

# Example: AI should NOT implement this without API docs:
def sync_with_shipping_carrier(order):
    # This requires specific carrier API integration
    # AI cannot know API endpoints, authentication, or data formats
    pass

# ✅ INSTEAD, AI can provide integration template:
def sync_with_shipping_carrier(order):
    """
    Sync order with shipping carrier API.

    TODO: Implement specific carrier integration:
    - Add API endpoint configuration
    - Implement authentication
    - Add error handling and retry logic
    - Handle rate limiting
    - Map data fields correctly
    """
    carrier_api = ShippingCarrierAPI()
    return carrier_api.create_shipment(order)
```

### 10.3 AI Development Workflow

#### Step 1: Requirements Analysis
```python
# ✅ AI CAN help analyze requirements and suggest structure:

# Developer provides: "I need a product model with variants and inventory"
# AI suggests:
class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    track_inventory = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory_quantity = models.IntegerField(default=0)
    # ... other fields

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=0)
    reserved = models.IntegerField(default=0)
    available = models.IntegerField(default=0)
```

#### Step 2: Code Generation
```python
# ✅ AI CAN generate initial code implementation:

# Developer: "Generate serializers for these models"
# AI generates:
class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    inventory_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'sku', 'description', 'status',
            'variants', 'inventory_count', 'created_at'
        ]

    def get_inventory_count(self, obj):
        return sum(variant.inventory_quantity for variant in obj.variants.all())

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'title', 'sku', 'price', 'inventory_quantity']
```

#### Step 3: Review and Refine
```python
# ✅ AI CAN suggest improvements after review:

# Developer: "This serializer is slow, optimize it"
# AI suggests optimization:
class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    inventory_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'sku', 'description', 'status',
            'variants', 'inventory_count', 'created_at'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optimize query with prefetch_related
        if self.instance:
            self.instance = Product.objects.prefetch_related('variants').get(
                id=self.instance.id
            )

    def get_inventory_count(self, obj):
        # Use annotated field for better performance
        return getattr(obj, '_inventory_count', 0)
```

### 10.4 Best Practices for AI-Assisted Development

#### Code Quality Standards
```python
# ✅ AI-generated code should follow these standards:

# 1. Use descriptive variable names
# ❌ BAD:
def calc(o):
    t = sum(i.q * i.p for i in o.items)
    return t

# ✅ GOOD:
def calculate_order_subtotal(order):
    subtotal = sum(item.quantity * item.unit_price for item in order.items.all())
    return subtotal

# 2. Include proper error handling
# ❌ BAD:
def process_order(order):
    order.save()
    send_email(order.customer.email)

# ✅ GOOD:
def process_order(order):
    try:
        order.save()
        send_order_confirmation_email.delay(order.id)
    except ValidationError as e:
        logger.error(f"Order validation failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing order: {e}")
        order.status = 'error'
        order.save()
        raise

# 3. Add comprehensive docstrings
def reserve_inventory(variant, quantity):
    """
    Reserve inventory for a product variant.

    Args:
        variant (ProductVariant): The product variant to reserve inventory for
        quantity (int): The quantity to reserve

    Returns:
        bool: True if reservation successful, False otherwise

    Raises:
        ValidationError: If quantity is invalid or insufficient inventory

    Example:
        >>> variant = ProductVariant.objects.get(sku="SHIRT-RED-M")
        >>> success = reserve_inventory(variant, 2)
        >>> print(success)
        True
    """
    if quantity <= 0:
        raise ValidationError("Quantity must be positive")

    inventory = Inventory.objects.filter(variant=variant).first()
    if not inventory or inventory.available < quantity:
        return False

    inventory.reserved += quantity
    inventory.save()
    return True
```

#### Security Guidelines
```python
# ✅ AI should always generate secure code:

# 1. Validate all inputs
def create_product_from_api(request_data):
    # Validate required fields
    required_fields = ['title', 'sku', 'price']
    for field in required_fields:
        if field not in request_data:
            raise ValidationError(f"Missing required field: {field}")

    # Sanitize input
    title = bleach.clean(request_data['title'], tags=[], strip=True)
    sku = re.sub(r'[^A-Za-z0-9_-]', '', request_data['sku'])

    # Validate data types
    try:
        price = Decimal(str(request_data['price']))
    except (ValueError, TypeError):
        raise ValidationError("Invalid price format")

# 2. Use parameterized queries (Django ORM handles this)
# ❌ BAD (SQL injection risk):
# Product.objects.raw(f"SELECT * FROM product WHERE title LIKE '%{user_input}%'")

# ✅ GOOD (Django ORM protects against injection):
Product.objects.filter(title__icontains=user_input)

# 3. Never log sensitive data
def log_payment_attempt(payment_data):
    # ❌ BAD: Logs sensitive card data
    logger.info(f"Payment attempt: {payment_data}")

    # ✅ GOOD: Only logs non-sensitive data
    logger.info(f"Payment attempt: {payment_data['order_id']}, amount: {payment_data['amount']}")
```

#### Performance Guidelines
```python
# ✅ AI should generate performant code:

# 1. Use select_related and prefetch_related
def get_orders_with_customers():
    # ❌ BAD: N+1 queries
    orders = Order.objects.all()
    for order in orders:
        print(order.customer.email)  # Separate query for each order

    # ✅ GOOD: Single query with related data
    orders = Order.objects.select_related('customer').all()
    for order in orders:
        print(order.customer.email)

# 2. Use database indexes
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['customer', 'status']),  # For customer order queries
            models.Index(fields=['status', 'created_at']),  # For status-based queries
        ]

# 3. Use bulk operations for large datasets
def update_product_prices(price_updates):
    # ❌ BAD: Individual updates
    for product_id, new_price in price_updates.items():
        product = Product.objects.get(id=product_id)
        product.price = new_price
        product.save()

    # ✅ GOOD: Bulk update
    Product.objects.filter(id__in=price_updates.keys()).update(
        price=Case(*[When(id=pk, then=Value(price)) for pk, price in price_updates.items()])
    )
```

### 10.5 Code Review Checklist

#### Before Committing AI-Generated Code
```python
# ✅ Review checklist for AI-generated code:

# 1. [ ] Business Logic Verification
#    - Does the code implement correct business rules?
#    - Are edge cases handled properly?
#    - Is the logic consistent with requirements?

# 2. [ ] Security Review
#    - Are all inputs validated?
#    - Is sensitive data handled properly?
#    - Are there any injection vulnerabilities?

# 3. [ ] Performance Review
#    - Are database queries optimized?
#    - Are indexes properly used?
#    - Is caching implemented where needed?

# 4. [ ] Testing Coverage
#    - Are there tests for all methods?
#    - Are edge cases tested?
#    - Are integration tests included?

# 5. [ ] Documentation
#    - Are docstrings complete?
#    - Are complex algorithms explained?
#    - Are API endpoints documented?

# Example review process:
def review_ai_generated_code(code):
    """
    Review AI-generated code before committing.

    Args:
        code (str): The AI-generated code to review

    Returns:
        dict: Review results with issues and recommendations
    """
    issues = []

    # Check for security issues
    if 'eval(' in code or 'exec(' in code:
        issues.append("Potentially unsafe code execution detected")

    # Check for missing input validation
    if 'request.data' in code and 'validate' not in code:
        issues.append("Missing input validation")

    # Check for N+1 queries
    if '.objects.all()' in code and 'select_related' not in code:
        issues.append("Potential N+1 query problem")

    return {
        'issues': issues,
        'approved': len(issues) == 0
    }
```

### 10.6 Continuous Improvement

#### Learning from AI Mistakes
```python
# ✅ Document and learn from AI errors:

# Example: AI generated incorrect tax calculation
def calculate_tax_v1(order):
    # AI initially generated this (incorrect):
    return order.subtotal * 0.08  # Hardcoded tax rate

# Corrected version with proper business logic:
def calculate_tax_v2(order):
    """
    Calculate tax based on shipping address and product taxability.

    The AI initially suggested a hardcoded tax rate, but business requirements
    showed that tax rates vary by jurisdiction and product type.
    """
    tax_calculator = TaxCalculator()
    return tax_calculator.calculate_tax(order)

# Lesson learned: Always verify business logic assumptions with stakeholders
```

#### Feedback Loop
```python
# ✅ Create feedback mechanism for AI improvements:

class AICodeFeedback:
    """Track and learn from AI code generation feedback"""

    def __init__(self):
        self.feedback_log = []

    def log_feedback(self, prompt, generated_code, issues, corrections):
        """Log feedback for AI improvement"""
        feedback_entry = {
            'timestamp': timezone.now(),
            'prompt': prompt,
            'generated_code': generated_code,
            'issues': issues,
            'corrections': corrections,
            'lesson_learned': self.extract_lesson(issues, corrections)
        }

        self.feedback_log.append(feedback_entry)

    def extract_lesson(self, issues, corrections):
        """Extract learning points from feedback"""
        lessons = []

        for issue in issues:
            if 'security' in issue.lower():
                lessons.append("Always prioritize security in generated code")
            elif 'performance' in issue.lower():
                lessons.append("Consider database optimization in generated code")
            elif 'validation' in issue.lower():
                lessons.append("Include proper input validation")

        return lessons

    def generate_improvement_summary(self):
        """Generate summary of improvements needed"""
        issue_counts = {}
        for entry in self.feedback_log:
            for issue in entry['issues']:
                issue_type = issue.split(':')[0]
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

        return {
            'total_feedback': len(self.feedback_log),
            'common_issues': issue_counts,
            'improvement_areas': sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        }
```

### 10.7 Final Guidelines

#### Golden Rules for AI-Assisted Ecommerce Development
```python
# 1. ✅ ALWAYS verify business logic with stakeholders
# 2. ✅ ALWAYS prioritize security over convenience
# 3. ✅ ALWAYS test AI-generated code thoroughly
# 4. ✅ NEVER trust AI with sensitive data handling
# 5. ✅ NEVER deploy AI code without human review
# 6. ✅ ALWAYS document assumptions and limitations
# 7. ✅ ALWAYS consider performance implications
# 8. ✅ ALWAYS maintain code quality standards
# 9. ✅ NEVER use AI for critical security implementations
# 10. ✅ ALWAYS learn from AI mistakes and improve prompts

# Example of responsible AI usage:
def responsible_ai_usage_example():
    """
    Example of using AI responsibly for ecommerce development.

    Process:
    1. Use AI to generate boilerplate code and templates
    2. Review and understand all generated code
    3. Implement business logic manually based on requirements
    4. Add security measures and input validation
    5. Write comprehensive tests
    6. Document assumptions and limitations
    7. Get code review from team members
    8. Test thoroughly before deployment
    """
    pass
```
# Ecommerce Module Rules

## Overview

This directory contains comprehensive development rules for the ecommerce module in the cms-updated backend project. The ecommerce module provides complete product catalog management, shopping cart functionality, order processing, and customer management for multi-tenant stores.

## File Structure

```
ecommerce/
├── 01-overview.md          # Module overview and architecture
├── 02-models.md            # Core model definitions and relationships
├── 03-views.md             # API endpoints and ViewSets
├── 04-services.md          # Business logic and service layer
├── 05-integration.md       # Integration with other modules
├── 06-security.md          # Security and privacy rules
├── 07-testing.md           # Testing requirements and examples
├── 08-migration.md         # Migration strategy from legacy system
├── 09-improvements.md      # Improvement suggestions for DFCMS
├── 10-ai-guidelines.md     # AI development guidelines
└── README.md               # This file
```

## Key Principles

### Store-Scoped Architecture
- All models must have explicit `ForeignKey` to `stores.Store`
- Data isolation between stores is mandatory
- All ViewSets must inherit from `StoreScopedViewSet`

### V2-Only Implementation
- Clean implementation without legacy compatibility
- Modern Django patterns and best practices
- No backward compatibility concerns

### Service Layer Pattern
- Business logic centralized in `services.py`
- Models only contain data-related logic
- ViewSets handle HTTP concerns only

### Auto-Logging Integration
- All ecommerce activities logged to `logs` app
- Audit trails for all critical operations
- Event-driven architecture for extensibility

## Quick Start

### 1. Model Definitions
See `02-models.md` for complete model definitions including:
- Product and ProductVariant models
- Order and OrderItem models
- Cart and CartItem models
- Customer model linked to GlobalUser
- Collection and Coupon models
- Inventory management models

### 2. API Development
See `03-views.md` for API endpoint patterns:
- StoreScopedViewSet base class
- Product, Order, Cart ViewSets
- Public API endpoints
- Permission and filtering patterns

### 3. Business Logic
See `04-services.md` for service layer implementation:
- ProductService for product operations
- OrderService for order processing
- CartService for cart management
- InventoryService for stock management

### 4. Integration Points
See `05-integration.md` for module integrations:
- Media integration for product images
- Accounts integration for user management
- Stores integration for multi-tenancy
- Logs integration for audit trails
- Translations integration for i18n
- SMTP integration for email notifications

## Development Workflow

### 1. Model Development
```python
# Follow store-scoped pattern
class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    # ... other fields
```

### 2. Service Implementation
```python
# Centralize business logic
class ProductService:
    @staticmethod
    def create_product(store, user, data):
        # Business logic here
        pass
```

### 3. API Development
```python
# Inherit from StoreScopedViewSet
class ProductViewSet(StoreScopedViewSet):
    # API implementation
    pass
```

### 4. Testing
```python
# Comprehensive test coverage
class ProductModelTest(TestCase):
    def test_product_creation(self):
        # Test implementation
        pass
```

## Security Requirements

- Store isolation is mandatory
- Input validation on all endpoints
- Rate limiting on public APIs
- PCI compliance for payment processing
- GDPR compliance for customer data

See `06-security.md` for detailed security guidelines.

## Performance Requirements

- Optimized database queries with proper indexing
- Caching strategies for product data
- Efficient cart operations
- Scalable inventory management

See `07-testing.md` for performance testing requirements.

## Migration Strategy

For migrating from the existing DFCMS ecommerce module, see `08-migration.md` for:
- Legacy data analysis
- Migration phases
- Rollback strategy
- Testing procedures

## AI Development Guidelines

When using AI assistants for ecommerce development, see `10-ai-guidelines.md` for:
- What AI can and cannot do
- Security considerations
- Code quality standards
- Review checklists

## Improvements

For suggested improvements to the existing DFCMS ecommerce module, see `09-improvements.md` for:
- Current issues analysis
- Architecture improvements
- Feature enhancements
- Performance optimizations

## Compliance

This module follows all backend development rules defined in the main `rules.md` file and maintains consistency with other module rules files.

## Support

For questions about ecommerce module development:
1. Check the relevant section in this directory
2. Review the main backend rules
3. Consult with the development team
4. Check existing implementations for patterns

## Version History

- **v1.0**: Initial comprehensive rules documentation
- Based on analysis of existing DFCMS ecommerce module
- Incorporates modern Django best practices
- Includes security and performance considerations

<!-- ===============================================================================
 END ECOMMERCE.MD
 ================================================================================= -->
