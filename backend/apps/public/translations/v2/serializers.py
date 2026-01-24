"""
Serializers for translations module.
"""
from rest_framework import serializers
from ..models import Language, TranslationKey, Translation


class LanguageSerializer(serializers.ModelSerializer):
    """Serializer for Language"""
    
    class Meta:
        model = Language
        fields = [
            'id', 'code', 'name', 'is_active', 'is_default',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TranslationKeySerializer(serializers.ModelSerializer):
    """Serializer for TranslationKey"""
    
    class Meta:
        model = TranslationKey
        fields = [
            'id', 'key', 'namespace', 'description', 'content_type',
            'plural_form', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TranslationSerializer(serializers.ModelSerializer):
    """Serializer for Translation"""
    language = LanguageSerializer(read_only=True)
    key = TranslationKeySerializer(read_only=True)
    
    class Meta:
        model = Translation
        fields = [
            'id', 'key', 'language', 'store', 'text',
            'is_auto_translated', 'needs_review',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
