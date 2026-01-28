# Theme services module
# Add theme-related business logic here

from apps.themes.models import ColorScheme, Template, Theme


class ThemeService:
    """Theme management service"""

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
