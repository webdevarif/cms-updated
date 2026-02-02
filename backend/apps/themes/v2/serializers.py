"""
Serializers for themes app v2.
"""

from apps.themes.models import ColorScheme, Layout, StyleClass, Template, Theme, Typography
from rest_framework import serializers


class ThemeSerializer(serializers.ModelSerializer):
    """Theme serializer"""

    class Meta:
        model = Theme
        fields = ["id", "store", "name", "is_active", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class ColorSchemeSerializer(serializers.ModelSerializer):
    """Color scheme serializer"""

    class Meta:
        model = ColorScheme
        fields = [
            "id",
            "theme",
            "name",
            "key",
            "is_default",
            "colors",
            "dark_colors",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class TypographySerializer(serializers.ModelSerializer):
    """Typography serializer"""

    class Meta:
        model = Typography
        fields = [
            "id",
            "theme",
            "base_font_size",
            "font_smoothing",
            "font_family_sans_serif",
            "font_family_serif",
            "font_family_monospace",
            "h1_font_size",
            "h2_font_size",
            "h3_font_size",
            "h4_font_size",
            "h5_font_size",
            "h6_font_size",
            "heading_line_height",
            "body_line_height",
            "letter_spacing",
            "font_weight_light",
            "font_weight_normal",
            "font_weight_medium",
            "font_weight_bold",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class StyleClassSerializer(serializers.ModelSerializer):
    """Style class serializer"""

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
        read_only_fields = ["created_at", "updated_at"]


class LayoutSerializer(serializers.ModelSerializer):
    """Layout serializer"""

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
            "is_default",
            "is_system",
            "is_active",
            "content_slots",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class TemplateSerializer(serializers.ModelSerializer):
    """Template serializer"""

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
        read_only_fields = ["created_at", "updated_at"]
