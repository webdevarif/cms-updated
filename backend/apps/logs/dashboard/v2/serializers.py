"""
Dashboard logs serializers.
"""
from rest_framework import serializers
from apps.logs.models.models import LogEntry


class LogEntryDashboardSerializer(serializers.ModelSerializer):
    """Dashboard log entry serializer"""
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = LogEntry
        fields = [
            'id', 'store', 'user', 'user_email', 'level', 'level_display',
            'message', 'module', 'extra_data', 'is_sensitive',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LogEntryCreateSerializer(serializers.ModelSerializer):
    """Log entry creation serializer"""
    
    class Meta:
        model = LogEntry
        fields = [
            'level', 'message', 'module', 'extra_data', 'is_sensitive'
        ]


class LogStatisticsSerializer(serializers.Serializer):
    """Log statistics serializer"""
    total_logs = serializers.IntegerField()
    logs_by_level = serializers.DictField()
    logs_by_module = serializers.DictField()
    recent_logs = LogEntryDashboardSerializer(many=True)
    error_rate = serializers.FloatField()
    warning_rate = serializers.FloatField()
    avg_logs_per_day = serializers.FloatField()


class LogClearSerializer(serializers.Serializer):
    """Log clearing serializer"""
    days = serializers.IntegerField(min_value=1, max_value=365)
    confirm = serializers.BooleanField(required=True)
