"""
Services for queue module.
"""
from celery import current_app
from celery.result import AsyncResult
from django.db import models
import logging

logger = logging.getLogger(__name__)

# Task categories as per queue.md
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


class QueueService:
    """Shared queue management service"""
    
    @staticmethod
    def enqueue_task(task_name, args=None, kwargs=None, countdown=0, eta=None):
        """Enqueue a task for async execution"""
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
        """Get task status"""
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
        """Revoke a task"""
        current_app.control.revoke(task_id, terminate=terminate)
        logger.info(f"Revoked task: {task_id}")
        return True
    
    @staticmethod
    def retry_task(task_id, countdown=60):
        """Retry a failed task"""
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
        """Get list of active tasks"""
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
        """Get list of scheduled tasks"""
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
        """Get worker statistics"""
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


class TaskMonitoringService:
    """Task monitoring service"""
    
    @staticmethod
    def get_task_stats(hours=24):
        """Get task statistics for time period"""
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
        """Get slow tasks"""
        from .models import TaskLog
        
        return TaskLog.objects.filter(
            duration_ms__gt=threshold_ms
        ).order_by('-duration_ms')
    
    @staticmethod
    def get_failing_tasks(limit=50):
        """Get frequently failing tasks"""
        from .models import TaskLog
        from django.db.models import Count
        
        return TaskLog.objects.filter(
            status='failed'
        ).values('task_name').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]
    
    @staticmethod
    def log_task(task_id, task_name, status, result=None, duration_ms=None, error=None):
        """Log task execution"""
        from .models import TaskLog
        
        TaskLog.objects.create(
            task_id=task_id,
            task_name=task_name,
            status=status,
            result=result,
            duration_ms=duration_ms,
            error_message=error
        )
