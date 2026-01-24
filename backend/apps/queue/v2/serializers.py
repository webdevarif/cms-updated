"""
Serializers for queue module.
"""
from rest_framework import serializers
from ..models import QueueTask


class QueueTaskSerializer(serializers.ModelSerializer):
    """Serializer for QueueTask"""
    
    class Meta:
        model = QueueTask
        fields = [
            'id', 'store', 'task_id', 'task_name', 'payload', 'status',
            'retry_count', 'max_retries', 'error_message', 'error_traceback',
            'created_at', 'started_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'started_at', 'completed_at']
