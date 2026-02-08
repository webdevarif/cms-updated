"""
Simple theme system for Digital Farmers CMS.
"""

import json

from apps.stores.models import Store

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

DEFAULT_COLOR_SCHEMES = [
    {
        "key": "default",
        "name": "Default",
        "is_default": True,
        "colors": {  # Light mode
            "background": "#ffffff",
            "headings": "#1f2937",
            "text": "#4b5563",
            "links": "#3b82f6",
            "hover_links": "#2563eb",
            "borders": "#e5e7eb",
            "shadow": "rgba(0, 0, 0, 0.1)",
            "primary_button": {
                "background": "#3b82f6",
                "text": "#ffffff",
                "hover_background": "#2563eb",
                "hover_text": "#ffffff",
                "hover_border": "#2563eb",
                "border": "#3b82f6",
            },
            "secondary_button": {
                "background": "#f3f4f6",
                "text": "#1f2937",
                "hover_background": "#e5e7eb",
                "hover_text": "#1f2937",
                "hover_border": "#d1d5db",
                "border": "#d1d5db",
            },
            "inputs": {
                "background": "#ffffff",
                "text": "#1f2937",
                "border": "#d1d5db",
                "hover_background": "#f9fafb",
                "hover_border": "#9ca3af",
                "focus_border": "#3b82f6",
            },
            "variants": {
                "background": "#ffffff",
                "text": "#1f2937",
                "border": "#e5e7eb",
                "hover_background": "#f3f4f6",
                "hover_text": "#1f2937",
                "hover_border": "#d1d5db",
            },
        },
        "dark_colors": {  # Dark mode
            "background": "#111827",
            "headings": "#f3f4f6",
            "text": "#d1d5db",
            "links": "#60a5fa",
            "hover_links": "#3b82f6",
            "borders": "#374151",
            "shadow": "rgba(0, 0, 0, 0.4)",
            "primary_button": {
                "background": "#3b82f6",
                "text": "#ffffff",
                "hover_background": "#2563eb",
                "hover_text": "#ffffff",
                "hover_border": "#2563eb",
                "border": "#3b82f6",
            },
            "secondary_button": {
                "background": "#374151",
                "text": "#f3f4f6",
                "hover_background": "#4b5563",
                "hover_text": "#ffffff",
                "hover_border": "#6b7280",
                "border": "#4b5563",
            },
            "inputs": {
                "background": "#1f2937",
                "text": "#f3f4f6",
                "border": "#4b5563",
                "hover_background": "#374151",
                "hover_border": "#6b7280",
                "focus_border": "#60a5fa",
            },
            "variants": {
                "background": "#1f2937",
                "text": "#f3f4f6",
                "border": "#4b5563",
                "hover_background": "#374151",
                "hover_text": "#ffffff",
                "hover_border": "#6b7280",
            },
        },
    },
    {
        "key": "schema-1",
        "name": "Schema 1",
        "is_default": False,
        "colors": {
            "background": "#fafafa",
            "headings": "#111827",
            "text": "#374151",
            "links": "#059669",
            "hover_links": "#047857",
            "borders": "#d1d5db",
            "shadow": "rgba(0, 0, 0, 0.1)",
            "primary_button": {
                "background": "#059669",
                "text": "#ffffff",
                "hover_background": "#047857",
                "hover_text": "#ffffff",
                "hover_border": "#047857",
                "border": "#059669",
            },
            "secondary_button": {
                "background": "#f3f4f6",
                "text": "#111827",
                "hover_background": "#e5e7eb",
                "hover_text": "#111827",
                "hover_border": "#d1d5db",
                "border": "#d1d5db",
            },
            "inputs": {
                "background": "#ffffff",
                "text": "#111827",
                "border": "#d1d5db",
                "hover_background": "#f9fafb",
                "hover_border": "#9ca3af",
                "focus_border": "#059669",
            },
            "variants": {
                "background": "#ffffff",
                "text": "#111827",
                "border": "#e5e7eb",
                "hover_background": "#f3f4f6",
                "hover_text": "#111827",
                "hover_border": "#d1d5db",
            },
        },
        "dark_colors": {
            "background": "#0f172a",
            "headings": "#f1f5f9",
            "text": "#cbd5e1",
            "links": "#10b981",
            "hover_links": "#059669",
            "borders": "#334155",
            "shadow": "rgba(0, 0, 0, 0.4)",
            "primary_button": {
                "background": "#10b981",
                "text": "#ffffff",
                "hover_background": "#059669",
                "hover_text": "#ffffff",
                "hover_border": "#059669",
                "border": "#10b981",
            },
            "secondary_button": {
                "background": "#1e293b",
                "text": "#f1f5f9",
                "hover_background": "#334155",
                "hover_text": "#ffffff",
                "hover_border": "#475569",
                "border": "#334155",
            },
            "inputs": {
                "background": "#1e293b",
                "text": "#f1f5f9",
                "border": "#475569",
                "hover_background": "#334155",
                "hover_border": "#64748b",
                "focus_border": "#10b981",
            },
            "variants": {
                "background": "#1e293b",
                "text": "#f1f5f9",
                "border": "#334155",
                "hover_background": "#334155",
                "hover_text": "#ffffff",
                "hover_border": "#475569",
            },
        },
    },
]


def get_default_colors():
    """Return default colors for ColorScheme.colors field."""
    return DEFAULT_COLOR_SCHEMES[0]["colors"].copy()


def get_default_dark_colors():
    """Return default dark colors for ColorScheme.dark_colors field."""
    return DEFAULT_COLOR_SCHEMES[0]["dark_colors"].copy()


def get_default_typography():
    """Return default typography settings for Theme.typography field."""
    return {
        "headings": {
            "font_family": "Inter, sans-serif",
            "weights": {
                "h1": "700",
                "h2": "600",
                "h3": "600",
                "h4": "600",
                "h5": "500",
                "h6": "500",
            },
            "sizes": {
                "h1": "2.25rem",
                "h2": "1.875rem",
                "h3": "1.5rem",
                "h4": "1.25rem",
                "h5": "1.125rem",
                "h6": "1rem",
            },
            "line_heights": {
                "h1": "1.2",
                "h2": "1.3",
                "h3": "1.4",
                "h4": "1.5",
                "h5": "1.5",
                "h6": "1.6",
            },
        },
        "body": {
            "font_family": "Inter, sans-serif",
            "size": "1rem",
            "line_height": "1.6",
            "weight": "400",
        },
        "buttons": {
            "font_family": "Inter, sans-serif",
            "weight": "500",
            "size": "0.875rem",
            "letter_spacing": "0.025em",
        },
        "inputs": {"font_family": "Inter, sans-serif", "size": "0.875rem", "weight": "400"},
    }


class Theme(models.Model):
    """
    Main theme model for each store.
    Each store can have multiple themes, but only one active theme.
    """

    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="themes")
    name = models.CharField(max_length=100, default="Default Theme")
    key = models.SlugField(max_length=100, help_text="Unique key for this theme")
    description = models.TextField(blank=True, help_text="Optional description of the theme")
    is_default = models.BooleanField(
        default=False, help_text="Whether this is the default theme for the store"
    )
    typography = models.JSONField(
        default=get_default_typography, help_text="Typography settings as JSON"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "themes_theme"
        ordering = ["-is_default", "name"]
        unique_together = [["store", "key"], ["store", "name"]]

    def __str__(self):
        return f"{self.store.name} - {self.name}"

    def save(self, *args, **kwargs):
        # Ensure only one default theme per store
        if self.is_default:
            Theme.objects.filter(store=self.store, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class ColorScheme(models.Model):
    """
    Color schemes linked to a theme.
    Each theme can have multiple color schemes (light/dark variants).
    """

    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name="color_schemes")
    key = models.SlugField(max_length=100, help_text="Unique key for this color scheme")
    name = models.CharField(max_length=100, help_text="Display name for this color scheme")
    is_default = models.BooleanField(
        default=False, help_text="Whether this is the default color scheme"
    )
    colors = models.JSONField(default=get_default_colors, help_text="Light mode colors as JSON")
    dark_colors = models.JSONField(
        default=get_default_dark_colors, help_text="Dark mode colors as JSON"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "themes_color_scheme"
        ordering = ["-is_default", "name"]
        unique_together = [["theme", "key"], ["theme", "name"]]

    def __str__(self):
        return f"{self.theme.name} - {self.name}"

    def save(self, *args, **kwargs):
        # Ensure only one default color scheme per theme
        if self.is_default:
            ColorScheme.objects.filter(theme=self.theme, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Layout(models.Model):
    """
    Defines global structure including header, footer, and content slots.
    Each theme can have multiple layouts, with one default layout.
    """

    theme = models.ForeignKey(
        "themes.Theme",
        on_delete=models.CASCADE,
        related_name="layouts",
    )
    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.CASCADE,
    )

    name = models.CharField(max_length=100)
    key = models.SlugField(max_length=100)
    description = models.TextField(blank=True)

    # Header & footer templates
    header_template = models.ForeignKey(
        "themes.Template",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="used_as_header",
    )
    footer_template = models.ForeignKey(
        "themes.Template",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="used_as_footer",
    )

    # Layout settings
    is_default = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Content slots (for dynamic content injection)
    content_slots = models.JSONField(
        default=dict,
        blank=True,
        help_text="Defines content slots and their default content",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "themes_layout"
        unique_together = [["theme", "key"]]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.theme.name})"

    def clean(self):
        # Ensure only one default layout per theme
        if self.is_default and self.theme_id:
            Layout.objects.filter(
                theme=self.theme,
                is_default=True,
            ).exclude(
                pk=self.pk
            ).update(is_default=False)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class StyleClass(models.Model):
    """
    Reusable style classes with light/dark mode support and version-specific overrides.
    """

    theme = models.ForeignKey(
        "themes.Theme",
        on_delete=models.CASCADE,
        related_name="style_classes",
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)

    # Default CSS properties (base styles)
    default_css = models.JSONField(
        default=dict,
        help_text="Default CSS properties for this style class",
    )

    # Light/Dark mode overrides
    light_css = models.JSONField(
        default=dict,
        blank=True,
        help_text="Light mode CSS overrides (merges with default_css)",
    )
    dark_css = models.JSONField(
        default=dict,
        blank=True,
        help_text="Dark mode CSS overrides (merges with default_css)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "themes_style_class"
        unique_together = [["theme", "slug"]]
        ordering = ["name"]

    def __str__(self):
        return f"{self.theme.name} - {self.name}"

    def get_css(self, mode: str = "light") -> dict:
        """Get CSS for specific mode by merging base and overrides."""
        css = dict(self.default_css or {})
        if mode == "light" and self.light_css:
            css.update(self.light_css)
        elif mode == "dark" and self.dark_css:
            css.update(self.dark_css)
        return css


class Template(models.Model):
    """
    Defines reusable template components with a specific role in the layout system.
    Templates are body-only by default, with specialized roles for headers and footers.
    """

    theme = models.ForeignKey(
        "themes.Theme",
        on_delete=models.CASCADE,
        related_name="templates",
    )

    TEMPLATE_ROLES = [
        ("body", "Body"),  # Main content (default)
        ("header", "Header"),  # Header component
        ("footer", "Footer"),  # Footer component
        ("partial", "Partial"),  # Reusable partials
        ("section", "Section"),  # Page sections
    ]

    name = models.CharField(max_length=100)
    key = models.SlugField(max_length=100)
    template_role = models.CharField(
        max_length=20,
        choices=TEMPLATE_ROLES,
        default="body",
        help_text="Defines the template's role in the layout system",
    )
    template_type = models.CharField(
        max_length=100,
        default="any",
        help_text="Intended content type for this body template (PostType key or 'any' for generic)",
    )
    content = models.TextField(help_text="Template content (HTML or JSON)")
    content_type = models.CharField(
        max_length=10,
        choices=[
            ("html", "HTML"),
            ("json", "JSON"),
        ],
        default="html",
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "themes_template"
        unique_together = [["theme", "key"]]
        ordering = ["name"]

    def __str__(self):
        return f"{self.theme.name} - {self.name} ({self.template_role})"

    def clean(self):
        """Validate template_type format"""
        from django.core.exceptions import ValidationError
        from django.utils.text import slugify

        # template_type should be a slug or "any"
        if self.template_type != "any":
            # Check if it matches slug format
            slugified = slugify(self.template_type)
            if self.template_type != slugified:
                raise ValidationError(
                    {
                        "template_type": f"'{self.template_type}' is not a valid slug format. Use lowercase letters, numbers, and hyphens only, or 'any' for generic templates."
                    }
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def render(self, context=None):
        """Render template with context."""
        if self.content_type == "html":
            from django.template import Context
            from django.template import Template as DjangoTemplate

            tpl = DjangoTemplate(self.content)
            return tpl.render(Context(context or {}))
        else:
            import json

            return json.loads(self.content) if self.content else {}
