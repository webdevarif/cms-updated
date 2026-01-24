"""
Serializers for logs API v2.
"""
from rest_framework import serializers
from ..models import LogEntry


class LogEntrySerializer(serializers.ModelSerializer):
    """Serializer for LogEntry"""
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    log_level_display = serializers.CharField(source='get_log_level_display', read_only=True)
    user_info = serializers.SerializerMethodField()
    
    class Meta:
        model = LogEntry
        fields = [
            'id', 'event_type', 'event_type_display', 'log_level', 'log_level_display',
            'message', 'user', 'session_id', 'ip_address', 'user_agent', 'request_id',
            'metadata', 'user_info', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_user_info(self, obj):
        """Get user information"""
        if obj.user:
            return {
                'id': obj.user.id,
                'email': obj.user.email,
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name
            }
        return None


class LogEntryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating log entries"""
    
    class Meta:
        model = LogEntry
        fields = [
            'event_type', 'log_level', 'message', 'session_id', 'ip_address',
            'user_agent', 'request_id', 'metadata'
        ]


class LogAnalyticsSerializer(serializers.Serializer):
    """Serializer for log analytics"""
    total_visits = serializers.IntegerField()
    unique_visitors = serializers.IntegerField()
    bounce_rate = serializers.FloatField()
    top_pages = serializers.ListField(child=serializers.DictField())
    security_events = serializers.IntegerField()
    suspicious_activities = serializers.ListField(child=serializers.DictField())
