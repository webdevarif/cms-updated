"""
Dashboard translations serializers - full admin CRUD with bulk operations.
"""
from rest_framework import serializers

from ..models import Language, Translation, TranslationKey


class LanguageSerializer(serializers.ModelSerializer):
    """Dashboard language management"""

    class Meta:
        model = Language
        fields = [
            "id",
            "code",
            "name",
            "name_native",
            "is_active",
            "is_rtl",
            "flag_icon",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TranslationKeySerializer(serializers.ModelSerializer):
    """Dashboard translation key management"""

    class Meta:
        model = TranslationKey
        fields = [
            "id",
            "key",
            "description",
            "category",
            "is_active",
            "variables",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TranslationDashboardSerializer(serializers.ModelSerializer):
    """Dashboard translation serializer - full admin access"""

    language_code = serializers.CharField(source="language.code", read_only=True)
    language_name = serializers.CharField(source="language.name", read_only=True)
    key_name = serializers.CharField(source="translation_key.key", read_only=True)
    key_description = serializers.CharField(source="translation_key.description", read_only=True)
    store_name = serializers.CharField(source="store.name", read_only=True)

    class Meta:
        model = Translation
        fields = [
            "id",
            "store",
            "store_name",
            "language",
            "language_code",
            "language_name",
            "translation_key",
            "key_name",
            "key_description",
            "value",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "language_code",
            "language_name",
            "key_name",
            "key_description",
            "store_name",
            "created_at",
            "updated_at",
        ]
