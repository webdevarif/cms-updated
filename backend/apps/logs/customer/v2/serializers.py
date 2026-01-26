"""
Customer logs serializers.
"""
from rest_framework import serializers
from apps.logs.models.models import LogEntry


class LogEntryCustomerSerializer(serializers.ModelSerializer):
    """Customer log entry serializer"""
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    class Meta:
        model = LogEntry
        fields = [
            'id', 'level', 'level_display', 'message', 'module', 
            'extra_data', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LogStatisticsSerializer(serializers.Serializer):
    """Log statistics serializer"""
    total_logs = serializers.IntegerField()
    logs_by_level = serializers.DictField()
    logs_by_module = serializers.DictField()
    recent_logs = LogEntryCustomerSerializer(many=True)
    error_rate = serializers.FloatField()
    warning_rate = serializers.FloatField()
