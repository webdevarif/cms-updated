"""
Theme services for Digital Farmers CMS.
Handles theme initialization and default color scheme creation.
"""

from django.db import transaction

from .models import DEFAULT_COLOR_SCHEMES, ColorScheme, Theme


@transaction.atomic
def create_default_theme(store, name="Default Theme", key="default"):
    """
    Create a default theme for a store with default color schemes.

    Args:
        store: Store instance to create theme for
        name: Theme name (default: "Default Theme")
        key: Theme key (default: "default")

    Returns:
        Theme instance
    """
    # Create the theme
    theme = Theme.objects.create(
        store=store, name=name, key=key, is_default=True, description="Default theme for the store"
    )

    # Create default color schemes
    for scheme_data in DEFAULT_COLOR_SCHEMES:
        ColorScheme.objects.create(
            theme=theme,
            key=scheme_data["key"],
            name=scheme_data["name"],
            is_default=scheme_data["is_default"],
            colors=scheme_data["colors"].copy(),
            dark_colors=scheme_data["dark_colors"].copy(),
        )

    return theme


@transaction.atomic
def initialize_theme_color_schemes(theme):
    """
    Initialize color schemes for an existing theme based on DEFAULT_COLOR_SCHEMES.

    Args:
        theme: Theme instance to initialize color schemes for

    Returns:
        List of created ColorScheme instances
    """
    created_schemes = []

    for scheme_data in DEFAULT_COLOR_SCHEMES:
        scheme, created = ColorScheme.objects.get_or_create(
            theme=theme,
            key=scheme_data["key"],
            defaults={
                "name": scheme_data["name"],
                "is_default": scheme_data["is_default"],
                "colors": scheme_data["colors"].copy(),
                "dark_colors": scheme_data["dark_colors"].copy(),
            },
        )
        if created:
            created_schemes.append(scheme)

    return created_schemes


def get_theme_colors(theme, scheme_key="default", mode="light"):
    """
    Get colors for a specific theme and color scheme.

    Args:
        theme: Theme instance
        scheme_key: Color scheme key (default: "default")
        mode: "light" or "dark" (default: "light")

    Returns:
        Dict of colors or None if not found
    """
    try:
        color_scheme = theme.color_schemes.get(key=scheme_key)
        return color_scheme.dark_colors if mode == "dark" else color_scheme.colors
    except ColorScheme.DoesNotExist:
        # Fallback to first available scheme
        first_scheme = theme.color_schemes.first()
        if first_scheme:
            return first_scheme.dark_colors if mode == "dark" else first_scheme.colors
        return None


def get_default_color_scheme(theme):
    """
    Get the default color scheme for a theme.

    Args:
        theme: Theme instance

    Returns:
        ColorScheme instance or None
    """
    try:
        return theme.color_schemes.get(is_default=True)
    except ColorScheme.DoesNotExist:
        return theme.color_schemes.first()


def ensure_theme_has_defaults(theme):
    """
    Ensure a theme has all default color schemes from DEFAULT_COLOR_SCHEMES.
    Creates missing schemes if needed.

    Args:
        theme: Theme instance

    Returns:
        List of newly created ColorScheme instances
    """
    existing_keys = set(theme.color_schemes.values_list("key", flat=True))
    default_keys = set(scheme["key"] for scheme in DEFAULT_COLOR_SCHEMES)
    missing_keys = default_keys - existing_keys

    created_schemes = []
    for scheme_data in DEFAULT_COLOR_SCHEMES:
        if scheme_data["key"] in missing_keys:
            scheme = ColorScheme.objects.create(
                theme=theme,
                key=scheme_data["key"],
                name=scheme_data["name"],
                is_default=scheme_data["is_default"],
                colors=scheme_data["colors"].copy(),
                dark_colors=scheme_data["dark_colors"].copy(),
            )
            created_schemes.append(scheme)

    return created_schemes
