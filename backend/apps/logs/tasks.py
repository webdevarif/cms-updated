"""
Celery tasks for logs app.
"""
from celery import shared_task
from .models import LogEntry


@shared_task
def log_event_async(log_data):
    """Async logging to avoid blocking requests"""
    try:
        from core.services.base import BaseTenantCRUDService
        # Set the model class for LogEntry
        BaseTenantCRUDService.model_class = LogEntry
        BaseTenantCRUDService.create(**log_data)
    except Exception as e:
        # Fallback to sync logging if async fails
        BaseTenantCRUDService.create(**log_data)
        # Log the error
        print(f"Async logging failed: {e}")


@shared_task
def cleanup_old_logs(days=90):
    """Clean up old logs to prevent table bloat"""
    from datetime import timedelta
    from django.utils import timezone
    
    cutoff = timezone.now() - timedelta(days=days)
    from core.services.base import BaseTenantCRUDService
    # Set the model class for LogEntry
    BaseTenantCRUDService.model_class = LogEntry
    deleted_count = BaseTenantCRUDService.filter(created_at__lt=cutoff).delete()[0]
    return f"Deleted {deleted_count} old log entries"
