"""
Customer search serializers - authenticated search results.
"""
from rest_framework import serializers


class SearchResultSerializer(serializers.Serializer):
    """Search results serializer for customer layer"""

    total = serializers.IntegerField()
    results = serializers.ListField(child=serializers.DictField())
    facets = serializers.DictField()
    query = serializers.CharField()
    limit = serializers.IntegerField()
    offset = serializers.IntegerField()
    duration_ms = serializers.IntegerField()


class SearchSuggestionSerializer(serializers.Serializer):
    """Search suggestions serializer for customer layer"""

    suggestions = serializers.ListField(child=serializers.DictField())


class SearchHistorySerializer(serializers.Serializer):
    """Search history serializer"""

    history = serializers.ListField(child=serializers.DictField())
    limit = serializers.IntegerField()
    offset = serializers.IntegerField()
