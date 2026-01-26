# Core Rules v1.0

## Authority
- Owner: Primary Architecture Authority
- Enforced By: Django settings, middleware, base models
- Scope: GLOBAL - Overrides all app-level rules
- Authority Level: CONSTITUTIONAL

## 🎯 Purpose
This document defines GLOBAL, OVERRIDING RULES for the **core** module in CMS-Updated backend, providing the foundational configuration, middleware, and utilities for the entire application with simplified multi-tenant architecture. These rules are CONSTITUTIONAL and override all app-level rules.

---

## 🏗️ Structure
### **GLOBAL Directory Structure**
```
backend/
├── core/
│   ├── __init__.py
│   ├── manage.py
│   ├── wsgi.py
│   ├── asgi.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py          # Base settings - GLOBAL
│   │   ├── development.py   # Development settings - GLOBAL
│   │   ├── production.py    # Production settings - GLOBAL
│   │   └── testing.py      # Testing settings - GLOBAL
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── tenant.py       # Tenant middleware - GLOBAL
│   │   └── security.py     # Security middleware - GLOBAL
│   ├── urls/
│   │   ├── __init__.py
│   │   ├── v2.py          # V2 API URLs - GLOBAL
│   │   └── admin.py       # Admin URLs - GLOBAL
│   ├── libs/
│   │   ├── __init__.py
│   │   ├── email.py       # Email utilities - GLOBAL
│   │   ├── choices.py     # Common choices - GLOBAL
│   │   ├── utils.py       # General utilities - GLOBAL
│   │   └── validators.py  # Custom validators - GLOBAL
│   └── exceptions/
│       ├── __init__.py
│       └── custom.py       # Custom exceptions - GLOBAL
```

---

## 📦 Data Model
### **GLOBAL Base Model Requirements**
- ALL models MUST inherit from core base models
- ALL models MUST include store scoping where applicable
- ALL models MUST include created_at/updated_at timestamps
- ALL models MUST include proper database indexes
- ALL models MUST use soft delete where specified

### **GLOBAL Tenancy Rules**
- ALL data MUST be store-scoped by default
- ALL queries MUST include store filtering
- ALL foreign keys MUST reference store-scoped models
- NO global data access without explicit authorization

---

## ⚙️ Services
### **GLOBAL Email Service**
```python
# core/libs/email.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """
    GLOBAL centralized email service for sending emails.
    ALL email operations MUST use this service.
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
        ALL template emails MUST use this method.
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
        ALL welcome emails MUST use this method.
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

### **GLOBAL Common Choices**
```python
# core/libs/choices.py
from django.utils.translation import gettext_lazy as _

class StatusChoices:
    """GLOBAL status choices - MUST be used by all modules"""
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
    """GLOBAL order status choices - MUST be used by all e-commerce modules"""
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
    """GLOBAL payment status choices - MUST be used by all payment modules"""
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

### **GLOBAL Utilities**
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
    ALL unique ID generation MUST use this function.
    """
    return uuid.uuid4().hex[:length].upper()

def clean_filename(filename):
    """
    Clean filename for safe storage.
    ALL filename cleaning MUST use this function.
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
    ALL IP address retrieval MUST use this function.
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
    ALL file size validation MUST use this function.
    """
    if isinstance(file, InMemoryUploadedFile):
        size_mb = file.size / (1024 * 1024)
        if size_mb > max_size_mb:
            raise ValueError(f"File size {size_mb:.2f}MB exceeds maximum {max_size_mb}MB")
    return True
```

---

## 🔐 Security
### **GLOBAL Security Rules**
- ALL requests MUST pass through security middleware
- ALL authentication MUST use JWT tokens
- ALL API endpoints MUST require authentication by default
- ALL data access MUST be store-scoped
- ALL sensitive data MUST be encrypted at rest
- ALL file uploads MUST be validated and sanitized
- ALL CORS policies MUST be explicitly configured
- ALL security headers MUST be enabled in production

### **GLOBAL Authentication Rules**
- JWT tokens MUST be used for API authentication
- Session authentication MUST be used for admin interface
- Token refresh MUST be implemented
- Token blacklisting MUST be enabled after rotation
- All tokens MUST have expiration times

### **GLOBAL Authorization Rules**
- Store isolation MUST be enforced at database level
- User permissions MUST be store-scoped
- Cross-store access MUST be explicitly forbidden
- Admin access MUST require elevated permissions

---

## 🧪 Testing
### **GLOBAL Testing Requirements**
- ALL tests MUST use test database configuration
- ALL tests MUST clean up data after execution
- ALL tests MUST be store-isolated
- ALL tests MUST mock external services
- ALL tests MUST achieve minimum coverage requirements

---

## 🚫 Forbidden Patterns
### **GLOBAL Forbidden Patterns**
- MUST NOT bypass tenant middleware
- MUST NOT access data without store context
- MUST NOT use direct database queries without proper scoping
- MUST NOT hardcode configuration values
- MUST NOT disable security middleware
- MUST NOT use deprecated Django features
- MUST NOT create global state in views
- MUST NOT ignore authentication requirements
- MUST NOT use eval() or exec() in production code
- MUST NOT store sensitive data in session

---

## 🔗 Cross-Module Dependencies
### **GLOBAL Integration Requirements**
- ALL modules MUST import from core.libs
- ALL modules MUST use core base models
- ALL modules MUST respect tenant boundaries
- ALL modules MUST use core utilities
- ALL modules MUST implement core interfaces

---

## 📝 Notes
### **GLOBAL Configuration**
#### Base Settings
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
# GLOBAL SECURITY SETTINGS - CONSTITUTIONAL
# =============================================================================
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable is required")

DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '*').split(',')

# =============================================================================
# GLOBAL APPLICATION DEFINITION - CONSTITUTIONAL
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
    
    # Core apps - GLOBAL
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

# =============================================================================
# GLOBAL MIDDLEWARE - CONSTITUTIONAL ORDER
# =============================================================================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'core.middleware.tenant.TenantMiddleware',  # BEFORE authentication - GLOBAL
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.security.SecurityMiddleware',  # FINAL security layer - GLOBAL
]

ROOT_URLCONF = 'core.urls.v2'

# =============================================================================
# GLOBAL DATABASE - CONSTITUTIONAL
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
# GLOBAL TENANCY - CONSTITUTIONAL
# =============================================================================
# Note: We use explicit ForeignKey relationships, not automatic tenant filtering
STORE_MODEL = 'stores.Store'

# =============================================================================
# GLOBAL LOGGING - CONSTITUTIONAL
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
```

---

**Version**: 1.0  
**Last Updated**: 2026-01-26  
**Next Review**: 2026-02-25
