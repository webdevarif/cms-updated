"""
Serializers for themes app.
"""

from rest_framework import serializers

from .models import ColorScheme, Layout, StyleClass, Template, Theme


class ColorSchemeSerializer(serializers.ModelSerializer):
    """Serializer for ColorScheme model."""

    class Meta:
        model = ColorScheme
        fields = [
            "id",
            "theme",
            "key",
            "name",
            "is_default",
            "colors",
            "dark_colors",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LayoutSerializer(serializers.ModelSerializer):
    """Serializer for Layout model."""

    class Meta:
        model = Layout
        fields = [
            "id",
            "theme",
            "store",
            "name",
            "key",
            "description",
            "header_template",
            "footer_template",
            "content_slots",
            "is_default",
            "is_system",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StyleClassSerializer(serializers.ModelSerializer):
    """Serializer for StyleClass model."""

    class Meta:
        model = StyleClass
        fields = [
            "id",
            "theme",
            "name",
            "slug",
            "description",
            "default_css",
            "light_css",
            "dark_css",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TemplateSerializer(serializers.ModelSerializer):
    """Serializer for Template model."""

    class Meta:
        model = Template
        fields = [
            "id",
            "theme",
            "name",
            "key",
            "template_role",
            "content",
            "content_type",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ThemeSerializer(serializers.ModelSerializer):
    """Serializer for Theme model with nested data."""

    color_schemes = ColorSchemeSerializer(many=True, read_only=True)
    layouts = LayoutSerializer(many=True, read_only=True)
    style_classes = StyleClassSerializer(many=True, read_only=True)
    templates = TemplateSerializer(many=True, read_only=True)

    class Meta:
        model = Theme
        fields = [
            "id",
            "store",
            "name",
            "key",
            "description",
            "is_default",
            "typography",
            "color_schemes",
            "layouts",
            "style_classes",
            "templates",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
