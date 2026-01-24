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
