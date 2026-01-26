"""
Base settings for Digital Farmers CMS.

These settings are common to all environments.
"""
from pathlib import Path
import os
from datetime import timedelta
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
# PRODUCTION SECURITY SETTINGS
# =============================================================================
# HTTPS and SSL settings (only in production)
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

# Security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Session security
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF security
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Frontend URL for email links
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

# =============================================================================
# AUTHENTICATION CONFIGURATION
# =============================================================================
# AUTH_USER_MODEL = 'accounts.User'  # Temporarily commented out for migration
AUTH_USER_MODEL = 'auth.User'  # Use default for now

# =============================================================================
# APPLICATION DEFINITION
# =============================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',  # PostgreSQL search support
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'django_ratelimit',  # Rate limiting for production
    'elasticsearch_dsl',  # Elasticsearch/OpenSearch integration
    
    # Core apps
    'core',
    
    # Feature apps
    'apps.accounts',  # Migrated to internal layered structure
    'apps.stores',  # Migrated to internal layered structure
    'apps.logs',  # Migrated to internal layered structure
    'apps.smtp',
    'apps.mediafile',
    'apps.notifications',
    'apps.entities',
    'apps.queue',
    'apps.cache',
    'apps.forms',  # Migrated to internal layered structure
    'apps.search',  # Re-enabled after migration
    'apps.translations',
    'apps.ecommerce',  # Migrated to internal layered structure
    'apps.giftcards',  # Migrated to internal layered structure
    'apps.metafields',  # Migrated to internal layered structure
    'apps.themes',  # Migrated to internal layered structure
    'apps.webhooks',  # Migrated to internal layered structure
    'apps.test',
    'apps.posts',
]

MIDDLEWARE = [
    'sentry_sdk.integrations.django.middleware.SentryMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'core.middleware.tenant.TenantMiddleware',  # Before authentication
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.security.SecurityMiddleware',
    'apps.logs.middleware.LoggingMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# =============================================================================
# DATABASE
# =============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# =============================================================================
# STATIC FILES
# =============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# =============================================================================
# REST FRAMEWORK
# =============================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '50/hour',         # Public layer - stricter limits
        'user': '500/hour',        # Customer layer - moderate limits
        'admin': '2000/hour',      # Dashboard layer - generous limits
        'translation': '50/hour',  # For translation API
        'webhook': '200/hour',     # For webhook API
        'webhook_delivery': '500/hour',  # For webhook delivery endpoints
        'search': '100/hour',      # For search endpoints (stricter)
        'public_api': '150/hour',  # For general public API access
        'customer_api': '300/hour', # For customer-specific APIs
        'admin_api': '1000/hour',  # For admin dashboard APIs
    },
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
}

# =============================================================================
# JWT CONFIGURATION
# =============================================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# =============================================================================
# CORS
# =============================================================================
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:8000').split(',')

# =============================================================================
# ELASTICSEARCH - TEMPORARILY DISABLED
# =============================================================================
# ELASTICSEARCH_HOSTS = ['http://localhost:9200']
# ELASTICSEARCH_TIMEOUT = 30

# =============================================================================
# CELERY - TEMPORARILY DISABLED
# =============================================================================
# CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
# CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# =============================================================================
# CACHING - TEMPORARILY DISABLED
# =============================================================================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# =============================================================================
# SECURITY - HTML Sanitization
# =============================================================================
BLEACH_ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol',
    'strong', 'ul', 'p', 'br', 'span', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'table', 'thead', 'tbody', 'tr', 'th', 'td'
]

BLEACH_ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target'],
    'abbr': ['title'],
    'acronym': ['title'],
    '*': ['class', 'id'],
    'td': ['colspan', 'rowspan'],
    'th': ['colspan', 'rowspan', 'scope'],
}

BLEACH_STRIP_TAGS = True

# =============================================================================
# LOGGING
# =============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# =============================================================================
# ELASTICSEARCH / OPENSEARCH CONFIGURATION
# =============================================================================
ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST', 'localhost')
ELASTICSEARCH_PORT = int(os.getenv('ELASTICSEARCH_PORT', '9200'))
ELASTICSEARCH_INDEX_PREFIX = os.getenv('ELASTICSEARCH_INDEX_PREFIX', 'dfcms')
ELASTICSEARCH_TIMEOUT = int(os.getenv('ELASTICSEARCH_TIMEOUT', '30'))

# Optional authentication
ELASTICSEARCH_USERNAME = os.getenv('ELASTICSEARCH_USERNAME', '')
ELASTICSEARCH_PASSWORD = os.getenv('ELASTICSEARCH_PASSWORD', '')
ELASTICSEARCH_CLOUD_ID = os.getenv('ELASTICSEARCH_CLOUD_ID', '')
ELASTICSEARCH_API_KEY = os.getenv('ELASTICSEARCH_API_KEY', '')

# Elasticsearch connection settings
ELASTICSEARCH_SETTINGS = {
    'hosts': [{
        'host': ELASTICSEARCH_HOST,
        'port': ELASTICSEARCH_PORT,
    }],
    'timeout': ELASTICSEARCH_TIMEOUT,
    'max_retries': 3,
    'retry_on_timeout': True,
}

# Add authentication if provided
if ELASTICSEARCH_USERNAME and ELASTICSEARCH_PASSWORD:
    ELASTICSEARCH_SETTINGS['http_auth'] = (ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD)
elif ELASTICSEARCH_API_KEY:
    ELASTICSEARCH_SETTINGS['api_key'] = ELASTICSEARCH_API_KEY
# =============================================================================
# DRF-SPECTACULAR - API Documentation
# =============================================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'Digital Farmers CMS API',
    'DESCRIPTION': 'Comprehensive API for Digital Farmers Content Management System',
    'VERSION': '2.0.0',
    'SERVE_INCLUDE_SCHEMA': False,  # Disable schema serving in production
    'SWAGGER_UI_DIST': 'SIDECAR',  # Use CDN for Swagger UI
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    # Schema generation settings
    'SCHEMA_PATH_PREFIX': '/api/v2',
    'SCHEMA_PATH_PREFIX_TRIM': True,
    # Authentication
    'SECURITY': [
        {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"'
            }
        }
    ],
    'SECURITY_REQUIREMENTS': [
        {
            'Bearer': []
        }
    ],
    # Component settings
    'COMPONENT_SPLIT_REQUEST': True,
    'COMPONENT_SPLIT_PATCH': True,
    'SORT_OPERATIONS': False,  # Keep operations in definition order
    'SORT_OPERATION_PARAMETERS': False,
    # Tags and grouping
    'TAGS': [
        {'name': 'Authentication', 'description': 'User authentication and authorization'},
        {'name': 'Content Management', 'description': 'Posts, pages, and content operations'},
        {'name': 'E-commerce', 'description': 'Products, orders, and store management'},
        {'name': 'Search', 'description': 'Full-text search and indexing'},
        {'name': 'Themes', 'description': 'Theme management and customization'},
        {'name': 'Notifications', 'description': 'User notifications and messaging'},
        {'name': 'Analytics', 'description': 'Reporting and business intelligence'},
        {'name': 'System', 'description': 'System management and utilities'},
    ],
    'EXTERNAL_DOCS': {
        'description': 'Find more info here',
        'url': 'https://docs.digitalfarmers.com',
    },
    # Extensions
    'EXTENSIONS_ROOT': {
        'x-logo': {
            'url': 'https://digitalfarmers.com/logo.png',
            'altText': 'Digital Farmers CMS'
        }
    },
    # Custom settings for our multi-tenant architecture
    'SERVERS': [
        {
            'url': '{protocol}://{domain}',
            'description': 'Store-specific API server',
            'variables': {
                'protocol': {
                    'default': 'https',
                    'enum': ['http', 'https'],
                    'description': 'Protocol for API calls'
                },
                'domain': {
                    'default': 'api.digitalfarmers.com',
                    'description': 'API domain for your store'
                }
            }
        }
    ],
    # Enums and constants
    'ENUM_NAME_OVERRIDES': {
        'StatusEnum': 'apps.posts.models.Post.STATUS_CHOICES',
        'OrderStatusEnum': 'apps.ecommerce.models.orders.Order.STATUS_CHOICES',
        'PaymentStatusEnum': 'apps.ecommerce.models.payments.Payment.STATUS_CHOICES',
    },
    # Response examples
    'ENUM_ADD_EXCLUDE': [
        'django.db.models.enums.Choices',
    ],
}

# =============================================================================
# SENTRY MONITORING - PRODUCTION ERROR TRACKING
# =============================================================================
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

# Sentry DSN - set via environment variable in production
SENTRY_DSN = os.getenv('SENTRY_DSN')

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            RedisIntegration(),
            CeleryIntegration(),
        ],
        # Performance monitoring
        traces_sample_rate=0.1,  # Capture 10% of transactions
        profiles_sample_rate=0.1,  # Capture 10% of profiles
        
        # Environment configuration
        environment=os.getenv('SENTRY_ENVIRONMENT', 'development'),
        release=os.getenv('SENTRY_RELEASE', '1.0.0'),
        
        # Error tracking configuration
        send_default_pii=False,  # Don't send personally identifiable information
        attach_stacktrace=True,
        
        # Before send hook for filtering sensitive data
        before_send=lambda event, hint: event,
        
        # Custom tags
        tags={
            'service': 'cms-backend',
            'version': '2.0.0',
        },
    )

