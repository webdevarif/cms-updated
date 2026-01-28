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
