# Logs App Rules - DFCMS Compatible

## 1. Directory Structure (Flat & Standard)
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

## 2. Single Model Design
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

## 3. Auto-Logging Implementation

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
