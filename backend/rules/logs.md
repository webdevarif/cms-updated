# Logs Rules v1.0

## 🎯 Purpose
[Purpose content to be added]

## 🏗️ Structure
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

## 🔧 Implementation
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

## 🔒 Permissions
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

## 🧪 Testing
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

## ⚙️ Services
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

## 🔗 Dependencies
- accounts.md for user scoping and authentication events
- cache.md for log aggregation and caching strategies
- media.md for file download logging

## 📋 Migration
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

## ✅ Benefits
- All logging is async via Celery
- Database indexes on frequently queried fields
- Automatic cleanup of old logs
- Batch operations for migrations

---
**Version**: 1.0  
**Last Updated**: 2026-01-26
**Next Review**: 2026-02-25
