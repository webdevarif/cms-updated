"""
Typography model.
"""
from django.db import models


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
