# Queue Infrastructure Rules v1.0

## Authority
- Owner: Infrastructure Lead
- Enforced By: QueueService, TaskMonitoringService, management commands
- Scope: Shared Infrastructure
- Authority Level: INFRASTRUCTURE STANDARD

## 🎯 Purpose
This document defines SHARED INFRASTRUCTURE rules for the **queue** system in CMS-Updated backend, implementing a unified task queue management system with Celery for asynchronous processing across all modules.

---

## 🏗️ Structure
### **Infrastructure Directory Structure**
```
apps/
├── queue/
│   ├── __init__.py
│   ├── services.py          # Infrastructure service layer
│   ├── tasks.py             # Infrastructure task templates
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

## 📦 Data Model
### **Infrastructure Task Categories**
```python
# Infrastructure-provided task categories
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

## ⚙️ Services
### **Infrastructure QueueService**
```python
# apps/queue/services.py
from celery import current_app
from celery.result import AsyncResult
import logging

logger = logging.getLogger(__name__)

class QueueService:
    """Infrastructure queue management service"""

    @staticmethod
    def enqueue_task(task_name, args=None, kwargs=None, countdown=0, eta=None):
        """
        Enqueue a task for async execution
        INFRASTRUCTURE PROVIDES: Task queuing mechanism
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
        INFRASTRUCTURE PROVIDES: Task status tracking
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
        INFRASTRUCTURE PROVIDES: Task revocation
        """
        current_app.control.revoke(task_id, terminate=terminate)
        logger.info(f"Revoked task: {task_id}")
        return True

    @staticmethod
    def retry_task(task_id, countdown=60):
        """
        Retry a failed task
        INFRASTRUCTURE PROVIDES: Task retry mechanism
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
        INFRASTRUCTURE PROVIDES: Active task monitoring
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
        INFRASTRUCTURE PROVIDES: Scheduled task monitoring
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
        INFRASTRUCTURE PROVIDES: Worker performance monitoring
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

### **Infrastructure TaskMonitoringService**
```python
# apps/queue/services.py (continued)

class TaskMonitoringService:
    """Infrastructure task monitoring service"""

    @staticmethod
    def get_task_stats(hours=24):
        """
        Get task statistics for time period
        INFRASTRUCTURE PROVIDES: Task performance analytics
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
        INFRASTRUCTURE PROVIDES: Performance bottleneck identification
        """
        from .models import TaskLog

        return TaskLog.objects.filter(
            duration_ms__gt=threshold_ms
        ).order_by('-duration_ms')

    @staticmethod
    def get_failing_tasks(limit=50):
        """
        Get frequently failing tasks
        INFRASTRUCTURE PROVIDES: Failure pattern analysis
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
        INFRASTRUCTURE PROVIDES: Task execution logging
        APPLICATION MUST: Call this method for task monitoring
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

## 🔐 Security
### **Infrastructure Security Requirements**
- INFRASTRUCTURE MUST validate task payloads and arguments
- INFRASTRUCTURE MUST sanitize inputs before task execution
- INFRASTRUCTURE MUST enforce rate limits on task creation
- INFRASTRUCTURE MUST log task execution for audit trails

### **Application Security Responsibilities**
- APPLICATION MUST ensure tasks don't expose sensitive data
- APPLICATION MUST validate task permissions before execution
- APPLICATION MUST implement proper error handling
- APPLICATION MUST NOT include secrets in task arguments

---

## 🧪 Testing
### **Infrastructure Testing Requirements**
- **Services**: 100% code coverage
- **Tasks**: 100% code coverage
- **Integration**: Critical path testing
- **Performance**: Task execution time validation

### **Infrastructure Test Examples**
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

## 🚫 Forbidden Patterns
### **Infrastructure Forbidden Patterns**
- MUST NOT execute tasks without proper validation
- MUST NOT allow unlimited task retries
- MUST NOT bypass task monitoring
- MUST NOT ignore task timeout limits

### **Application Forbidden Patterns**
- MUST NOT include sensitive data in task arguments
- MUST NOT create tasks without proper error handling
- MUST NOT ignore task failure notifications
- MUST NOT use blocking operations in tasks

---

## 🔗 Cross-Module Dependencies
### **Infrastructure Interface Requirements**
- ALL modules MUST import from apps.queue.services
- ALL modules MUST use QueueService for task operations
- ALL modules MUST use TaskMonitoringService for logging
- ALL modules MUST follow task naming conventions

### **Application Integration Examples**
```python
# APPLICATION RESPONSIBILITY: Use infrastructure services
from celery import shared_task
from apps.queue.services import TaskMonitoringService

@shared_task(bind=True, max_retries=3)
def example_task(self, data_id):
    """
    APPLICATION MUST: Implement task logic
    APPLICATION MUST: Use infrastructure monitoring
    """
    try:
        # Application business logic here
        result = process_data(data_id)

        # APPLICATION MUST: Log task completion
        TaskMonitoringService.log_task(
            task_id=self.request.id,
            task_name='example_task',
            status='success',
            result={'data_id': data_id}
        )

        return result

    except Exception as exc:
        # APPLICATION MUST: Log task failure
        TaskMonitoringService.log_task(
            task_id=self.request.id,
            task_name='example_task',
            status='failed',
            error=str(exc)
        )

        # APPLICATION MUST: Implement retry logic
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

---

## 📝 Notes
### **Infrastructure Management Commands**
#### List Tasks
```bash
# List active tasks
python manage.py list_tasks --status=active

# List scheduled tasks
python manage.py list_tasks --status=scheduled

# List failed tasks
python manage.py list_tasks --status=failed
```

#### Retry Failed Tasks
```bash
# Retry all failed tasks
python manage.py retry_failed_tasks

# Retry specific task
python manage.py retry_failed_tasks --task-id=abc123
```

#### Purge Tasks
```bash
# Purge all tasks
python manage.py purge_tasks

# Purge tasks by queue
python manage.py purge_tasks --queue=email
```

---

**Version**: 1.0
**Last Updated**: 2026-01-26
**Next Review**: 2026-02-25
