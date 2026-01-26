"""
Dashboard search serializers - full admin CRUD with analytics.
"""
from rest_framework import serializers
from apps.search.models.infrastructure import SearchIndex, SearchQuery


class SearchResultSerializer(serializers.Serializer):
    """Search results serializer for dashboard layer"""

    total = serializers.IntegerField()
    results = serializers.ListField(child=serializers.DictField())
    facets = serializers.DictField()
    query = serializers.CharField()
    limit = serializers.IntegerField()
    offset = serializers.IntegerField()
    duration_ms = serializers.IntegerField()
    filters = serializers.DictField()


class SearchSuggestionSerializer(serializers.Serializer):
    """Search suggestions serializer for dashboard layer"""

    suggestions = serializers.ListField(child=serializers.DictField())


class SearchAnalyticsSerializer(serializers.Serializer):
    """Search analytics serializer"""

    total_queries = serializers.IntegerField()
    unique_queries = serializers.IntegerField()
    top_queries = serializers.ListField(child=serializers.DictField())
    no_results_queries = serializers.ListField(child=serializers.DictField())
    avg_results_per_query = serializers.FloatField()


class SearchIndexSerializer(serializers.ModelSerializer):
    """Search index serializer"""

    class Meta:
        model = SearchIndex
        fields = [
            'id', 'store', 'name', 'is_active', 'content_types',
            'facets', 'settings', 'last_reindexed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SearchQuerySerializer(serializers.ModelSerializer):
    """Search query log serializer"""

    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = SearchQuery
        fields = [
            'id', 'store', 'user', 'user_email', 'query', 'search_type',
            'results_count', 'filters', 'duration_ms', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
