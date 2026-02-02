"""
Serializers for analytics app v2 API.
"""

from rest_framework import serializers

from ..models.events import EventLog, SearchLog


class EventLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventLog
        fields = [
            "id",
            "event_type",
            "event_name",
            "properties",
            "user",
            "session_id",
            "ip_address",
            "user_agent",
            "request_id",
            "duration_ms",
            "created_at",
        ]


class SearchLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchLog
        fields = [
            "id",
            "query",
            "results_count",
            "success",
            "search_type",
            "user",
            "session_id",
            "ip_address",
            "duration_ms",
            "created_at",
        ]
