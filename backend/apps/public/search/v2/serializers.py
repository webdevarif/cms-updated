"""
Serializers for search module.
"""
from rest_framework import serializers
from ..models import SearchIndex, SearchDocument


class SearchIndexSerializer(serializers.ModelSerializer):
    """Serializer for SearchIndex"""
    
    class Meta:
        model = SearchIndex
        fields = [
            'id', 'store', 'name', 'index_name', 'content_types', 'fields',
            'facets', 'is_active', 'last_reindexed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_reindexed_at']


class SearchDocumentSerializer(serializers.ModelSerializer):
    """Serializer for SearchDocument"""
    
    class Meta:
        model = SearchDocument
        fields = [
            'id', 'store', 'search_index', 'content_type', 'object_id',
            'title', 'content', 'metadata', 'is_indexed',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SearchResultsSerializer(serializers.Serializer):
    """Serializer for search results"""
    total = serializers.IntegerField()
    results = serializers.ListField(child=serializers.DictField())
    facets = serializers.DictField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    duration_ms = serializers.IntegerField()


class FacetsSerializer(serializers.Serializer):
    """Serializer for facets"""
    field = serializers.CharField()
    label = serializers.CharField()
    type = serializers.CharField()
    options = serializers.ListField(child=serializers.DictField())


class SuggestionsSerializer(serializers.Serializer):
    """Serializer for search suggestions"""
    text = serializers.CharField()
    score = serializers.FloatField()
