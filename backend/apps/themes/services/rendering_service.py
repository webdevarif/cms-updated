"""
Liquid-like template rendering service for themes.
Provides template rendering with variable substitution and control structures.
"""
import json
import logging
import re

from django.conf import settings
from django.template import Context, Template, TemplateSyntaxError
from django.template.loader import get_template

logger = logging.getLogger(__name__)


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
            rendered_content = template.render(context)

            return rendered_content

        except Exception as e:
            logger.error(f"Template rendering error: {str(e)}")
            # Return original content with error indication for debugging
            return f"<!-- Template rendering error: {str(e)} -->{template_content}"

    @staticmethod
    def _liquid_to_django(liquid_content):
        """
        Convert Liquid template syntax to Django template syntax.

        Args:
            liquid_content (str): Content with Liquid syntax

        Returns:
            str: Content with Django template syntax
        """
        django_content = liquid_content

        # Convert Liquid comments to Django comments
        django_content = LiquidTemplateRenderer.COMMENT_PATTERN.sub(r"{# \1 #}", django_content)

        # Convert Liquid if/else/endif to Django syntax
        django_content = LiquidTemplateRenderer.ENDIF_PATTERN.sub(r"{% endif %}", django_content)
        django_content = LiquidTemplateRenderer.ELSE_PATTERN.sub(r"{% else %}", django_content)
        django_content = LiquidTemplateRenderer.IF_PATTERN.sub(r"{% if \1 %}", django_content)

        # Convert Liquid for/endfor to Django syntax
        django_content = LiquidTemplateRenderer.ENDFOR_PATTERN.sub(r"{% endfor %}", django_content)
        django_content = LiquidTemplateRenderer.FOR_PATTERN.sub(
            r"{% for \1 in \2 %}", django_content
        )

        return django_content

    @staticmethod
    def validate_template_syntax(template_content):
        """
        Validate Liquid template syntax by converting to Django and checking.

        Args:
            template_content (str): Template content to validate

        Returns:
            tuple: (is_valid: bool, errors: list)
        """
        try:
            django_content = LiquidTemplateRenderer._liquid_to_django(template_content)
            Template(django_content)
            return True, []
        except TemplateSyntaxError as e:
            return False, [str(e)]
        except Exception as e:
            return False, [f"Validation error: {str(e)}"]

    @staticmethod
    def extract_variables(template_content):
        """
        Extract all variables used in the template.

        Args:
            template_content (str): Template content

        Returns:
            set: Set of variable names used in the template
        """
        variables = set()

        # Find all variable patterns
        matches = LiquidTemplateRenderer.VARIABLE_PATTERN.findall(template_content)

        for match in matches:
            # Extract variable name (before any filters)
            var_name = match.split("|")[0].strip()
            if var_name:
                variables.add(var_name)

        return variables


class ThemeRenderingService:
    """
    High-level theme rendering service using LiquidTemplateRenderer.
    Handles complete page rendering with layouts, templates, and assets.
    """

    @staticmethod
    def render_template(template_obj, context, store=None):
        """
        Render a theme template with context data.

        Args:
            template_obj: Template model instance
            context (dict): Context data for rendering
            store: Store instance for store-specific context

        Returns:
            str: Rendered HTML content
        """
        # Add store-specific context if available
        if store:
            context.update(
                {
                    "store": {
                        "id": store.id,
                        "name": store.name,
                        "slug": store.slug,
                        "domain": getattr(store, "domain", ""),
                    }
                }
            )

        # Add global context
        context.update(
            {
                "settings": {
                    "site_name": getattr(settings, "SITE_NAME", "My Store"),
                    "site_url": getattr(settings, "SITE_URL", "http://localhost"),
                }
            }
        )

        return LiquidTemplateRenderer.render_template(template_obj.content, context)

    @staticmethod
    def render_page(theme, page_data, store=None, request=None):
        """
        Render a complete page using theme layout and content.

        Args:
            theme: Theme model instance
            page_data (dict): Page content data
            store: Store instance
            request: HTTP request object

        Returns:
            dict: Rendered page data with HTML, CSS, JS, meta tags
        """
        try:
            # Get layout for the theme
            layout = theme.layouts.filter(is_default=True, is_active=True).first()
            if not layout:
                layout = theme.layouts.filter(is_active=True).first()

            if not layout:
                # Fallback to basic HTML structure
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>{page_data.get('title', 'Page')}</title>
                    {page_data.get('meta_tags', '')}
                </head>
                <body>
                    {page_data.get('content', '')}
                </body>
                </html>
                """
            else:
                # Render layout with page data
                layout_context = {
                    "page": page_data,
                    "theme": {
                        "id": theme.id,
                        "name": theme.name,
                        "version": theme.version,
                    },
                }

                if store:
                    layout_context["store"] = {
                        "id": store.id,
                        "name": store.name,
                        "slug": store.slug,
                    }

                if request:
                    layout_context["request"] = {
                        "path": request.path,
                        "user": request.user if request.user.is_authenticated else None,
                    }

                html_content = LiquidTemplateRenderer.render_template(
                    layout.content, layout_context
                )

            # Get theme assets
            css_files, js_files = ThemeRenderingService.get_theme_asset_urls(theme)

            # Generate meta tags
            meta_tags = ThemeRenderingService.generate_meta_tags(page_data)

            return {
                "html": html_content,
                "css_files": css_files,
                "js_files": js_files,
                "meta_tags": meta_tags,
            }

        except Exception as e:
            logger.error(f"Page rendering error: {str(e)}")
            # Return basic HTML as fallback
            return {
                "html": f"""
                <!DOCTYPE html>
                <html>
                <head><title>Error</title></head>
                <body><h1>Rendering Error</h1><p>{str(e)}</p></body>
                </html>
                """,
                "css_files": [],
                "js_files": [],
                "meta_tags": "",
            }

    @staticmethod
    def get_theme_assets(theme):
        """
        Get all assets (CSS, JS, images) for a theme.

        Args:
            theme: Theme model instance

        Returns:
            dict: Asset URLs organized by type
        """
        assets = {
            "css_files": [],
            "js_files": [],
            "images": [],
            "fonts": [],
        }

        # Get CSS files from style classes
        css_files = theme.style_classes.filter(is_active=True).values_list("css_file", flat=True)
        assets["css_files"].extend([f for f in css_files if f])

        # Get JS files (if theme has custom JS)
        # This would be extended based on theme model structure

        # Get images and fonts from theme assets
        # This would be extended based on theme asset management

        return assets

    @staticmethod
    def get_theme_asset_urls(theme):
        """
        Get CSS and JS asset URLs for a theme.

        Args:
            theme: Theme model instance

        Returns:
            tuple: (css_urls: list, js_urls: list)
        """
        css_urls = []
        js_urls = []

        # Build asset URLs based on theme structure
        theme_base_url = f"/themes/{theme.slug}/"

        # Add theme-specific CSS
        css_urls.append(f"{theme_base_url}theme.css")

        # Add theme-specific JS
        js_urls.append(f"{theme_base_url}theme.js")

        # Add typography CSS if available
        if theme.typography.filter(is_active=True).exists():
            css_urls.append(f"{theme_base_url}typography.css")

        return css_urls, js_urls

    @staticmethod
    def generate_meta_tags(page_data):
        """
        Generate HTML meta tags for a page.

        Args:
            page_data (dict): Page data containing meta information

        Returns:
            str: HTML meta tags
        """
        meta_tags = []

        # Title
        if page_data.get("title"):
            meta_tags.append(f'<title>{page_data["title"]}</title>')

        # Description
        if page_data.get("description"):
            meta_tags.append(f'<meta name="description" content="{page_data["description"]}">')

        # Keywords
        if page_data.get("keywords"):
            meta_tags.append(f'<meta name="keywords" content="{page_data["keywords"]}">')

        # Open Graph tags
        if page_data.get("og_title"):
            meta_tags.append(f'<meta property="og:title" content="{page_data["og_title"]}">')
        if page_data.get("og_description"):
            meta_tags.append(
                f'<meta property="og:description" content="{page_data["og_description"]}">'
            )
        if page_data.get("og_image"):
            meta_tags.append(f'<meta property="og:image" content="{page_data["og_image"]}">')

        return "\n".join(meta_tags)

    @staticmethod
    def validate_template_syntax(template_content):
        """
        Validate template syntax.

        Args:
            template_content (str): Template content to validate

        Returns:
            tuple: (is_valid: bool, errors: list)
        """
        return LiquidTemplateRenderer.validate_template_syntax(template_content)
