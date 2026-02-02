"""
Consolidated theme services for Digital Farmers CMS.
"""

import json
import logging
import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.template import Context, Template, TemplateSyntaxError
from django.template.loader import get_template

from .models import ColorScheme, Template, Theme, get_default_color_schemes

logger = logging.getLogger(__name__)


class ThemeService:
    """Theme management service"""

    @staticmethod
    def get_default_color_schemes():
        """Get all built-in color schemes"""
        return get_default_color_schemes()

    @staticmethod
    def create_theme(store, name, **kwargs):
        """Create a new theme"""
        return Theme.objects.create(store=store, name=name, **kwargs)

    @staticmethod
    def apply_theme(store, theme):
        """Apply theme to store"""
        if isinstance(theme, Theme):
            theme.activate()
        elif isinstance(theme, str):
            theme = Theme.objects.get(id=theme, store=store)
            theme.activate()

    @staticmethod
    def get_active_theme(store):
        """Get active theme for store"""
        return Theme.objects.filter(store=store, is_active=True).first()

    @staticmethod
    def get_theme_settings(theme):
        """Get all theme settings (colors, typography, etc.)"""
        settings = {}

        # Get color scheme
        color_scheme = theme.get_color_scheme()
        if color_scheme:
            settings["colors"] = color_scheme.colors
            settings["dark_colors"] = color_scheme.dark_colors

        # Get typography
        if hasattr(theme, "typography"):
            typography = theme.typography
            settings["typography"] = {
                "base_font_size": typography.base_font_size,
                "font_smoothing": typography.font_smoothing,
                "font_family_sans_serif": typography.font_family_sans_serif,
                "font_family_serif": typography.font_family_serif,
                "font_family_monospace": typography.font_family_monospace,
                "h1_font_size": typography.h1_font_size,
                "h2_font_size": typography.h2_font_size,
                "h3_font_size": typography.h3_font_size,
                "h4_font_size": typography.h4_font_size,
                "h5_font_size": typography.h5_font_size,
                "h6_font_size": typography.h6_font_size,
                "heading_line_height": typography.heading_line_height,
                "body_line_height": typography.body_line_height,
                "letter_spacing": typography.letter_spacing,
                "font_weight_light": typography.font_weight_light,
                "font_weight_normal": typography.font_weight_normal,
                "font_weight_medium": typography.font_weight_medium,
                "font_weight_bold": typography.font_weight_bold,
            }

        # Get style classes
        style_classes = theme.style_classes.all()
        settings["style_classes"] = {}
        for sc in style_classes:
            settings["style_classes"][sc.slug] = {
                "light": sc.get_css("light"),
                "dark": sc.get_css("dark"),
            }

        # Get templates
        templates = theme.templates.filter(is_active=True)
        settings["templates"] = {t.key: t.render() for t in templates}

        return settings

    @staticmethod
    def get_color_scheme(theme, key=None):
        """Get color scheme from theme"""
        if isinstance(theme, Theme):
            return theme.get_color_scheme(key)
        return None

    @staticmethod
    def get_typography(theme):
        """Get typography from theme"""
        if hasattr(theme, "typography"):
            return theme.typography
        return None

    @staticmethod
    def get_style_class(theme, slug, mode="light"):
        """Get style class CSS from theme"""
        if hasattr(theme, "style_classes"):
            style_class = theme.style_classes.filter(slug=slug).first()
            if style_class:
                return style_class.get_css(mode)
        return None


class LiquidTemplateRenderer:
    """
    Liquid-like template renderer that supports:
    - Variable substitution: {{ variable }}
    - Control structures: {% if %}, {% for %}, {% endif %}, {% endfor %}
    - Filters: {{ variable | filter }}
    - Comments: {# comment #}
    """

    # Liquid-style variable pattern: {{ variable }} or {{ variable | filter }}
    VARIABLE_PATTERN = re.compile(r"\{\{\s*([^}]+?)\s*\}\}")

    # Liquid-style tag patterns
    IF_PATTERN = re.compile(r"\{\%\s*if\s+(.+?)\s*\%\}")
    ELSE_PATTERN = re.compile(r"\{\%\s*else\s*\%\}")
    ENDIF_PATTERN = re.compile(r"\{\%\s*endif\s*\%\}")
    FOR_PATTERN = re.compile(r"\{\%\s*for\s+(.+?)\s+in\s+(.+?)\s*\%\}")
    ENDFOR_PATTERN = re.compile(r"\{\%\s*endfor\s*\%\}")
    COMMENT_PATTERN = re.compile(r"\{\#\s*(.+?)\s*\#\}")

    @staticmethod
    def render_template(template_content, context_data):
        """
        Render Liquid-like template with provided context data.

        Args:
            template_content (str): Template content with Liquid syntax
            context_data (dict): Context variables for rendering

        Returns:
            str: Rendered HTML content
        """
        try:
            # Convert Liquid syntax to Django template syntax
            django_template_content = LiquidTemplateRenderer._liquid_to_django(template_content)

            # Create Django template and render
            template = Template(django_template_content)
            context = Context(context_data)

            return template.render(context)

        except TemplateSyntaxError as e:
            logger.error(f"Template syntax error: {e}")
            return f"Template Error: {str(e)}"
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            return f"Rendering Error: {str(e)}"

    @staticmethod
    def _liquid_to_django(liquid_content):
        """
        Convert Liquid syntax to Django template syntax.

        Args:
            liquid_content (str): Liquid template content

        Returns:
            str: Django template content
        """
        content = liquid_content

        # Remove comments
        content = LiquidTemplateRenderer.COMMENT_PATTERN.sub("", content)

        # Convert for loops
        def replace_for(match):
            variable, iterable = match.groups()
            return f"{{% for {variable} in {iterable} %}}"

        content = LiquidTemplateRenderer.FOR_PATTERN.sub(replace_for, content)

        # Convert if/else/endif (already compatible with Django)
        # No changes needed for these patterns

        # Convert variables with filters
        def replace_variable(match):
            var_expression = match.group(1).strip()
            return f"{{{{ {var_expression} }}}}"

        content = LiquidTemplateRenderer.VARIABLE_PATTERN.sub(replace_variable, content)

        return content

    @staticmethod
    def render_liquid_template(template_content, context=None):
        """
        Legacy method for backward compatibility.
        """
        return LiquidTemplateRenderer.render_template(template_content, context or {})

    @staticmethod
    def validate_liquid_syntax(template_content):
        """
        Validate Liquid template syntax.

        Args:
            template_content (str): Template content to validate

        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Try to convert and render with empty context
            django_content = LiquidTemplateRenderer._liquid_to_django(template_content)
            template = Template(django_content)
            template.render(Context({}))
            return True, None
        except TemplateSyntaxError as e:
            return False, f"Syntax error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
