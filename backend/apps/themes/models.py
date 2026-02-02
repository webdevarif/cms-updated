"""
Consolidated theme models for Digital Farmers CMS.
"""

from django.db import models

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
        "colors": {  # Light
            "background": "#fefce8",
            "headings": "#7c2d12",
            "text": "#713f12",
            "links": "#c2410c",
            "hover_links": "#9a3412",
            "borders": "#fbbf24",
            "shadow": "rgba(0, 0, 0, 0.08)",
            "primary_button": {
                "background": "#c2410c",
                "text": "#ffffff",
                "hover_background": "#9a3412",
                "hover_text": "#ffffff",
                "hover_border": "#9a3412",
                "border": "#c2410c",
            },
            "secondary_button": {
                "background": "#fef3c7",
                "text": "#7c2d12",
                "hover_background": "#fde68a",
                "hover_text": "#7c2d12",
                "hover_border": "#f59e0b",
                "border": "#f59e0b",
            },
            "inputs": {
                "background": "#ffffff",
                "text": "#7c2d12",
                "border": "#f59e0b",
                "hover_background": "#fef3c7",
                "hover_border": "#d97706",
                "focus_border": "#c2410c",
            },
            "variants": {
                "background": "#ffffff",
                "text": "#713f12",
                "border": "#fbbf24",
                "hover_background": "#fef3c7",
                "hover_text": "#7c2d12",
                "hover_border": "#f59e0b",
            },
        },
        "dark_colors": {  # Dark
            "background": "#1c1917",
            "headings": "#fed7aa",
            "text": "#fcd34d",
            "links": "#fb923c",
            "hover_links": "#f97316",
            "borders": "#78350f",
            "shadow": "rgba(0, 0, 0, 0.5)",
            "primary_button": {
                "background": "#c2410c",
                "text": "#ffffff",
                "hover_background": "#9a3412",
                "hover_text": "#ffffff",
                "hover_border": "#9a3412",
                "border": "#c2410c",
            },
            "secondary_button": {
                "background": "#451a03",
                "text": "#fed7aa",
                "hover_background": "#78350f",
                "hover_text": "#ffffff",
                "hover_border": "#92400e",
                "border": "#78350f",
            },
            "inputs": {
                "background": "#292524",
                "text": "#fed7aa",
                "border": "#78350f",
                "hover_background": "#451a03",
                "hover_border": "#92400e",
                "focus_border": "#fb923c",
            },
            "variants": {
                "background": "#292524",
                "text": "#fcd34d",
                "border": "#78350f",
                "hover_background": "#451a03",
                "hover_text": "#fed7aa",
                "hover_border": "#92400e",
            },
        },
    },
]


def get_default_color_schemes():
    """Return all built-in color schemes."""
    return DEFAULT_COLOR_SCHEMES


def get_default_colors_for_key(key: str, mode: str = "light") -> dict:
    """Return the colors (light or dark) for a given scheme key."""
    for scheme in DEFAULT_COLOR_SCHEMES:
        if scheme["key"] == key:
            return scheme["dark_colors"] if mode == "dark" else scheme["colors"]
    # Fallback to the first/default scheme
    default = DEFAULT_COLOR_SCHEMES[0]
    return default["dark_colors" if mode == "dark" else "colors"]


class Theme(models.Model):
    """
    Main theme model for each store.
    Each store can have multiple themes, but only one active theme.
    """

    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="Default Theme")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "themes_theme"
        ordering = ["-is_active", "name"]
        unique_together = [["store", "name"]]

    def __str__(self):
        return f"{self.store.name} - {self.name}"

    def activate(self):
        """Activate this theme and deactivate others"""
        Theme.objects.filter(store=self.store).update(is_active=False)
        self.is_active = True
        self.save(update_fields=["is_active"])

    def get_active_color_scheme(self):
        """Get the default color scheme for this theme"""
        return self.color_schemes.filter(is_default=True).first()

    def get_color_scheme(self, key=None):
        """Get a specific color scheme by key"""
        if key:
            return self.color_schemes.filter(key=key).first()
        return self.get_active_color_scheme()


class ColorScheme(models.Model):
    """
    Color scheme with light/dark mode support.
    Each theme can have multiple color schemes.
    """

    theme = models.ForeignKey(
        "themes.Theme", on_delete=models.CASCADE, related_name="color_schemes"
    )
    name = models.CharField(max_length=100)
    key = models.SlugField(max_length=100)
    is_default = models.BooleanField(default=False)

    # Light mode colors
    colors = models.JSONField(default=dict, help_text="Light mode colors", blank=True)

    # Dark mode colors (optional)
    dark_colors = models.JSONField(default=dict, blank=True, help_text="Dark mode colors")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "themes_color_scheme"
        unique_together = [["theme", "key"]]
        ordering = ["name"]

    def __str__(self):
        return f"{self.theme.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.colors:
            self.colors = self.get_default_colors("light")
        if not self.dark_colors:
            self.dark_colors = self.get_default_colors("dark")
        super().save(*args, **kwargs)

    @staticmethod
    def get_default_colors(mode="light"):
        """Return default color scheme based on mode (light/dark)"""
        return get_default_colors_for_key("default", mode)


class Layout(models.Model):
    """
    Defines global structure including header, footer, and content slots.
    Each theme can have multiple layouts, with one default layout.
    """

    theme = models.ForeignKey("themes.Theme", on_delete=models.CASCADE, related_name="layouts")
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE)

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
        if self.is_default and self.theme:
            Layout.objects.filter(theme=self.theme, is_default=True).exclude(pk=self.pk).update(
                is_default=False
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class StyleClass(models.Model):
    """
    Reusable style classes with light/dark mode support and version-specific overrides.
    """

    theme = models.ForeignKey(
        "themes.Theme", on_delete=models.CASCADE, related_name="style_classes"
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)

    # Default CSS properties (base styles)
    default_css = models.JSONField(
        default=dict, help_text="Default CSS properties for this style class"
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

    def get_css(self, mode="light"):
        """Get CSS for specific mode"""
        css = self.default_css.copy()

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

    theme = models.ForeignKey("themes.Theme", on_delete=models.CASCADE, related_name="templates")

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

    def render(self, context=None):
        """Render template with context"""
        if self.content_type == "html":
            from django.template import Template as DjangoTemplate

            template = DjangoTemplate(self.content)
            return template.render(context or {})
        else:
            # Handle JSON templates
            import json

            return json.loads(self.content) if self.content else {}


class Typography(models.Model):
    """
    Typography settings for themes with comprehensive controls.
    Supports responsive typography and font loading.
    """

    theme = models.OneToOneField(
        "themes.Theme", on_delete=models.CASCADE, related_name="typography"
    )

    # Base font settings
    base_font_size = models.PositiveSmallIntegerField(
        default=16, help_text="Base font size in pixels (16px is recommended)"
    )
    font_smoothing = models.CharField(
        max_length=50,
        default="antialiased",
        choices=[
            ("antialiased", "Smooth (antialiased)"),
            ("subpixel-antialiased", "Crisp (subpixel)"),
            ("auto", "System Default"),
        ],
    )

    # Font families
    font_family_sans_serif = models.CharField(
        max_length=100,
        default='system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
        help_text="Sans-serif font family stack",
    )
    font_family_serif = models.CharField(
        max_length=100,
        default='Georgia, "Times New Roman", Times, serif',
        help_text="Serif font family stack",
    )
    font_family_monospace = models.CharField(
        max_length=100,
        default='SFMono-Regular, Consolas, "Liberation Mono", Menlo, Monaco, Courier New, monospace',
        help_text="Monospace font family stack",
    )

    # Heading font sizes
    h1_font_size = models.PositiveSmallIntegerField(default=48)
    h2_font_size = models.PositiveSmallIntegerField(default=36)
    h3_font_size = models.PositiveSmallIntegerField(default=28)
    h4_font_size = models.PositiveSmallIntegerField(default=24)
    h5_font_size = models.PositiveSmallIntegerField(default=20)
    h6_font_size = models.PositiveSmallIntegerField(default=16)

    # Line heights
    heading_line_height = models.DecimalField(max_digits=3, decimal_places=2, default=1.2)
    body_line_height = models.DecimalField(max_digits=3, decimal_places=2, default=1.5)

    # Letter spacing
    letter_spacing = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    # Font weights
    font_weight_light = models.PositiveSmallIntegerField(default=300)
    font_weight_normal = models.PositiveSmallIntegerField(default=400)
    font_weight_medium = models.PositiveSmallIntegerField(default=500)
    font_weight_bold = models.PositiveSmallIntegerField(default=700)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "themes_typography"

    def __str__(self):
        return f"{self.theme.name} Typography"
