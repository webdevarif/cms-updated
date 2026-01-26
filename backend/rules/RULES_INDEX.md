# Rules_Index Rules v1.0

## 🎯 Purpose
This document defines the development rules for the **core** module in CMS-Updated backend, providing the foundational configuration, middleware, and utilities for the entire application with simplified multi-tenant architecture.
---

## 🏗️ Structure
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

## 🔧 Implementation
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

## 🔒 Permissions
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

## 🧪 Testing
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

## ⚙️ Services
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

## 🔗 Dependencies
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

## 📋 Migration
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

## ✅ Benefits
- ✅ Transparent and easy to debug
- ✅ No magic/hidden behavior
- ✅ Explicit relationships in queries
- ✅ Easier to understand for new developers
---

---
**Version**: 1.0  
**Last Updated**: 2026-01-26
**Next Review**: 2026-02-25
