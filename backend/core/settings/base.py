"""
Base settings for Digital Farmers CMS.

These settings are common to all environments.
"""
import logging
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# Sentry imports (conditionally loaded)
try:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
except ImportError:
    sentry_sdk = None
    DjangoIntegration = None
    CeleryIntegration = None
    RedisIntegration = None
    LoggingIntegration = None

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BASE_DIR.parent

# Load environment variables
load_dotenv()

# =============================================================================
# SECURITY SETTINGS
# =============================================================================
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable is required")

DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

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
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Session security
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# CSRF security
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

# Frontend URL for email links
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# =============================================================================
# AUTHENTICATION CONFIGURATION
# =============================================================================
# AUTH_USER_MODEL = 'accounts.User'  # Temporarily commented out for migration
AUTH_USER_MODEL = "auth.User"  # Use default for now

# =============================================================================
# APPLICATION DEFINITION
# =============================================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",  # PostgreSQL search support
    # Third-party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "drf_spectacular_sidecar",  # Swagger UI static files
    "django_ratelimit",  # Rate limiting for production
    "elasticsearch_dsl",  # Elasticsearch/OpenSearch integration
    # Core apps
    "core",
    # Feature apps
    "apps.accounts",  # Migrated to internal layered structure
    "apps.stores",  # Migrated to internal layered structure
    "apps.logs",  # Migrated to internal layered structure
    "apps.smtp",
    "apps.mediafile",
    "apps.notifications",
    "apps.entities",
    "apps.queue",
    "apps.forms",  # Migrated to internal layered structure
    "apps.search",  # Re-enabled after migration
    "apps.translations",
    "apps.ecommerce",  # Re-enabled
    "apps.giftcards",  # Re-enabled
    "apps.metafields",  # Re-enabled
    "apps.themes",  # Re-enabled
    "apps.webhooks",  # Re-enabled
    "apps.test",  # Re-enabled - investigate actual admin template error
    "apps.posts",
    "django_celery_beat",  # Added for Celery Beat scheduling
    "background_task",  # Added for django-background-tasks
]

MIDDLEWARE = [
    # "sentry_sdk.integrations.django.SentryMiddleware",  # Temporarily disabled
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "core.middleware.tenant.TenantMiddleware",  # Before authentication
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.security.SecurityMiddleware",
    "apps.logs.middleware.LoggingMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# =============================================================================
# DATABASE
# =============================================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# =============================================================================
# STATIC FILES
# =============================================================================
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Static files finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Additional static files directories (if needed)
STATICFILES_DIRS = [
    # os.path.join(BASE_DIR, "static"),  # Uncomment if you have project-level static files
]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "media")

# =============================================================================
# REST FRAMEWORK
# =============================================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "50/hour",  # Public layer - stricter limits
        "user": "500/hour",  # Customer layer - moderate limits
        "admin": "2000/hour",  # Dashboard layer - generous limits
        "translation": "50/hour",  # For translation API
        "webhook": "200/hour",  # For webhook API
        "webhook_delivery": "500/hour",  # For webhook delivery endpoints
        "search": "100/hour",  # For search endpoints (stricter)
        "public_api": "150/hour",  # For general public API access
        "customer_api": "300/hour",  # For customer-specific APIs
        "admin_api": "1000/hour",  # For admin dashboard APIs
    },
    "USER_AUTHENTICATION_RULE": (
        "rest_framework_simplejwt.authentication.default_user_authentication_rule"
    ),
}

# =============================================================================
# JWT CONFIGURATION
# =============================================================================
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# =============================================================================
# CORS
# =============================================================================
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:8000"
).split(",")

# =============================================================================
# ELASTICSEARCH - TEMPORARILY DISABLED
# =============================================================================
# ELASTICSEARCH_HOSTS = ['http://localhost:9200']
# ELASTICSEARCH_TIMEOUT = 30

# =============================================================================
# CELERY - ENABLED FOR BACKGROUND TASKS
# =============================================================================
from celery.schedules import crontab

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Celery Beat Scheduler Configuration
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BEAT_TIMEZONE = "UTC"

# Celery Configuration
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True

# Beat Settings
CELERY_BEAT_SCHEDULE = {
    "example-periodic-task": {
        "task": "apps.search.tasks.rebuild_search_index",
        "schedule": crontab(minute=0, hour=3),  # Daily at 3 AM UTC
    },
}

# =============================================================================
# DJANGO BACKGROUND TASKS CONFIGURATION
# =============================================================================
BACKGROUND_TASKS = {
    "QUEUES": {
        "default": 3,  # Number of concurrent tasks
        "test": 2,  # Separate queue for test tasks
        "search": 1,  # Separate queue for search tasks
        "reports": 1,  # Separate queue for report tasks
    },
    "MAX_RUN_TIME": 3600,  # Maximum run time in seconds (1 hour)
    "MAX_ATTEMPTS": 3,  # Maximum retry attempts
    "RUN_EVERY_TASK_TYPE": False,  # Don't run every task type automatically
    "BACKGROUND_TASKS_ASYNC_METHODS": ["POST"],  # HTTP methods allowed for async tasks
    "BACKGROUND_TASKS_ASYNC_URL": "/background-tasks/",  # URL for async task execution
    "BACKGROUND_TASKS_URLS": [],  # Additional URLs to allow
}

# =============================================================================
# CACHING - TEMPORARILY DISABLED
# =============================================================================
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# =============================================================================
# SECURITY - HTML Sanitization
# =============================================================================
BLEACH_ALLOWED_TAGS = [
    "a",
    "abbr",
    "acronym",
    "b",
    "blockquote",
    "code",
    "em",
    "i",
    "li",
    "ol",
    "strong",
    "ul",
    "p",
    "br",
    "span",
    "div",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
]

BLEACH_ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target"],
    "abbr": ["title"],
    "acronym": ["title"],
    "*": ["class", "id"],
    "td": ["colspan", "rowspan"],
    "th": ["colspan", "rowspan", "scope"],
}

BLEACH_STRIP_TAGS = True

# =============================================================================
# LOGGING
# =============================================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

# =============================================================================
# ELASTICSEARCH / OPENSEARCH CONFIGURATION
# =============================================================================
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
ELASTICSEARCH_PORT = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
ELASTICSEARCH_INDEX_PREFIX = os.getenv("ELASTICSEARCH_INDEX_PREFIX", "dfcms")
ELASTICSEARCH_TIMEOUT = int(os.getenv("ELASTICSEARCH_TIMEOUT", "30"))

# Optional authentication
ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", "")
ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "")
ELASTICSEARCH_CLOUD_ID = os.getenv("ELASTICSEARCH_CLOUD_ID", "")
ELASTICSEARCH_API_KEY = os.getenv("ELASTICSEARCH_API_KEY", "")

# Elasticsearch connection settings
ELASTICSEARCH_SETTINGS = {
    "hosts": [
        {
            "host": ELASTICSEARCH_HOST,
            "port": ELASTICSEARCH_PORT,
        }
    ],
    "timeout": ELASTICSEARCH_TIMEOUT,
    "max_retries": 3,
    "retry_on_timeout": True,
}

# Add authentication if provided
if ELASTICSEARCH_USERNAME and ELASTICSEARCH_PASSWORD:
    ELASTICSEARCH_SETTINGS["http_auth"] = (ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD)
elif ELASTICSEARCH_API_KEY:
    ELASTICSEARCH_SETTINGS["api_key"] = ELASTICSEARCH_API_KEY
# =============================================================================
# DRF-SPECTACULAR - API Documentation
# =============================================================================
SPECTACULAR_SETTINGS = {
    "TITLE": "Digital Farmers CMS API",
    "DESCRIPTION": "Comprehensive API for Digital Farmers Content Management System",
    "VERSION": "2.0.0",
    "SERVE_INCLUDE_SCHEMA": False,  # Disable schema serving in production
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    # Schema generation settings
    "SCHEMA_PATH_PREFIX": "/v2/api",
    "SCHEMA_PATH_PREFIX_TRIM": True,
    # Disable all preprocessing hooks to avoid import issues
    "PREPROCESSING_HOOKS": [],
    "POSTPROCESSING_HOOKS": [],
    # Authentication
    "SECURITY": [
        {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": (
                    "JWT Authorization header using the Bearer scheme. "
                    'Example: "Authorization: Bearer {token}"'
                ),
            }
        }
    ],
    "SECURITY_REQUIREMENTS": [{"Bearer": []}],
    # Component settings
    "COMPONENT_SPLIT_REQUEST": True,
    "COMPONENT_SPLIT_PATCH": True,
    "SORT_OPERATIONS": False,  # Keep operations in definition order
    "SORT_OPERATION_PARAMETERS": False,
    # Tags and grouping
    "TAGS": [
        {"name": "Authentication", "description": "User authentication and authorization"},
        {"name": "Content Management", "description": "Posts, pages, and content operations"},
        {"name": "E-commerce", "description": "Products, orders, and store management"},
        {"name": "Search", "description": "Full-text search and indexing"},
        {"name": "Themes", "description": "Theme management and customization"},
        {"name": "Notifications", "description": "User notifications and messaging"},
        {"name": "Analytics", "description": "Reporting and business intelligence"},
        {"name": "System", "description": "System management and utilities"},
    ],
    "EXTERNAL_DOCS": {
        "description": "Find more info here",
        "url": "https://docs.digitalfarmers.com",
    },
    # Extensions
    "EXTENSIONS_ROOT": {
        "x-logo": {"url": "https://digitalfarmers.com/logo.png", "altText": "Digital Farmers CMS"}
    },
    # Custom settings for our multi-tenant architecture
    "SERVERS": [
        {
            "url": "{protocol}://{domain}",
            "description": "Store-specific API server",
            "variables": {
                "protocol": {
                    "default": "https",
                    "enum": ["http", "https"],
                    "description": "Protocol for API calls",
                },
                "domain": {
                    "default": "api.digitalfarmers.com",
                    "description": "API domain for your store",
                },
            },
        }
    ],
    # Enums and constants
    "ENUM_NAME_OVERRIDES": {
        "StatusEnum": "apps.posts.models.Post.STATUS_CHOICES",
        "OrderStatusEnum": "apps.ecommerce.models.orders.Order.STATUS_CHOICES",
        "PaymentStatusEnum": ("apps.ecommerce.models.payments.Payment.STATUS_CHOICES"),
    },
    # Response examples
    "ENUM_ADD_EXCLUDE": [
        "django.db.models.enums.Choices",
    ],
}

# =============================================================================
# SENTRY MONITORING - PRODUCTION ERROR TRACKING
# =============================================================================
SENTRY_DSN = os.getenv("SENTRY_DSN")


def _filter_sentry_event(event, hint):
    """
    Filter Sentry events before sending.

    This function allows you to modify or filter events before they are sent to Sentry.
    You can use it to:
    - Add custom tags
    - Filter out certain errors
    - Modify event data
    """
    # Skip certain expected errors in development
    if os.getenv("SENTRY_ENVIRONMENT", "development") == "development":
        # Filter out 404 errors in development
        if event.get("exception", {}).get("values", []):
            for value in event["exception"]["values"]:
                if "404" in str(value.get("value", "")):
                    return None

    # Add custom tags
    if "tags" not in event:
        event["tags"] = {}

    event["tags"].update(
        {
            "django_version": "4.2",
            "python_version": "3.14",
            "environment": os.getenv("SENTRY_ENVIRONMENT", "development"),
        }
    )

    # Add custom context
    if "contexts" not in event:
        event["contexts"] = {}

    event["contexts"]["app"] = {
        "app_name": "Digital Farmers CMS",
        "version": os.getenv("SENTRY_RELEASE", "1.0.0"),
    }

    return event


if SENTRY_DSN and sentry_sdk and DjangoIntegration:
    # Configure integrations
    integrations = [
        DjangoIntegration(
            transaction_style="url",
            middleware_spans=True,
            signals_spans=True,
            tracing=True,
        ),
        CeleryIntegration(
            monitor_beat_tasks=True,
            propagate_traces=True,
            tracing=True,
        ),
        RedisIntegration(
            redis_monitoring_enabled=True,
            tracing=True,
        ),
        LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR,
        ),
    ]

    # Initialize Sentry with full monitoring
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=integrations,
        # Performance monitoring
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
        # Environment and release
        environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
        release=os.getenv("SENTRY_RELEASE", "1.0.0"),
        # Privacy settings
        send_default_pii=False,
        send_request_pii=False,
        send_user_pii=False,
        # Error reporting settings
        attach_stacktrace=True,
        max_breadcrumbs=100,
        # Debug mode (disable in production)
        debug=os.getenv("SENTRY_DEBUG", "False").lower() == "true",
        # Before send callback for filtering
        before_send=lambda event, hint: _filter_sentry_event(event, hint),
    )
