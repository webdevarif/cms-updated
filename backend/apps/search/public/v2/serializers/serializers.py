"""
Public search serializers - read-only search results.
"""
from rest_framework import serializers


class SearchResultSerializer(serializers.Serializer):
    """Search results serializer"""

    total = serializers.IntegerField()
    results = serializers.ListField(child=serializers.DictField())
    facets = serializers.DictField()
    query = serializers.CharField()
    limit = serializers.IntegerField()
    offset = serializers.IntegerField()
    duration_ms = serializers.IntegerField()


class SearchSuggestionSerializer(serializers.Serializer):
    """Search suggestions serializer"""

    suggestions = serializers.ListField(child=serializers.DictField())
