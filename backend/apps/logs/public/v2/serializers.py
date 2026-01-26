"""
Public logs serializers.
"""
from rest_framework import serializers
from apps.logs.models.models import LogEntry


class LogEntryPublicSerializer(serializers.ModelSerializer):
    """Public log entry serializer - limited fields"""
    
    class Meta:
        model = LogEntry
        fields = [
            'id', 'level', 'message', 'module', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SystemStatusSerializer(serializers.Serializer):
    """System status serializer"""
    status = serializers.CharField()
    message = serializers.CharField()
    timestamp = serializers.DateTimeField()
    log_count = serializers.IntegerField()
    error_count = serializers.IntegerField()
    warning_count = serializers.IntegerField()
