"""
Queue infrastructure models.
"""
from django.db import models


class TaskLog(models.Model):
    """
    Task execution log for monitoring (per queue.md)
    """
    
    # Store scoping
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    
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
    
    class Meta:
        db_table = 'queue_task_log'
        indexes = [
            models.Index(fields=['store', 'status', 'created_at']),
            models.Index(fields=['store', 'task_name', 'created_at']),
            models.Index(fields=['task_name', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.task_name} - {self.status}"
