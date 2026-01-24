"""
Admin configuration for queue module.
"""
from django.contrib import admin
from .models import QueueTask


@admin.register(QueueTask)
class QueueTaskAdmin(admin.ModelAdmin):
    """Admin for QueueTask"""
    list_display = ['task_name', 'task_id', 'status', 'retry_count', 'created_at']
    list_filter = ['status']
    search_fields = ['task_name', 'task_id']
    readonly_fields = ['created_at', 'started_at', 'completed_at']
