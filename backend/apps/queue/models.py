"""
Queue models.
"""
from django.db import models


class QueueTask(models.Model):
    """
    Store-scoped queue task (legacy - kept for backward compatibility)
    """
    # Store scoping
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    
    # Task identification
    task_id = models.CharField(max_length=255, unique=True, db_index=True)
    task_name = models.CharField(max_length=255)
    
    # Task data
    payload = models.JSONField(default=dict, help_text="Task payload data")
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Retry information
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    # Error information
    error_message = models.TextField(blank=True)
    error_traceback = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'queue_task'
        indexes = [
            models.Index(fields=['store', 'status']),
            models.Index(fields=['store', 'created_at']),
            models.Index(fields=['task_id']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.task_name} ({self.task_id})"


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
