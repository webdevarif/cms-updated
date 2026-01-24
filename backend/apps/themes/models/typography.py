"""
Typography model.
"""
from django.db import models


class Typography(models.Model):
    """
    Typography settings for themes with comprehensive controls.
    Supports responsive typography and font loading.
    """
    theme = models.OneToOneField('themes.Theme', on_delete=models.CASCADE, related_name='typography')
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    
    # Base font settings
    base_font_size = models.PositiveSmallIntegerField(
        default=16,
        help_text="Base font size in pixels (16px is recommended)"
    )
    font_smoothing = models.CharField(
        max_length=50,
        default='antialiased',
        choices=[
            ('antialiased', 'Smooth (antialiased)'),
            ('subpixel-antialiased', 'Crisp (subpixel)'),
            ('auto', 'System Default')
        ]
    )
    
    # Font families
    font_primary = models.CharField(
        max_length=255,
        default="Inter, system-ui, -apple-system, sans-serif",
        help_text="Primary font family (used for headings and UI)"
    )
    font_secondary = models.CharField(
        max_length=255,
        default="Inter, system-ui, -apple-system, sans-serif",
        help_text="Secondary font family (used for body text)"
    )
    font_accent = models.CharField(
        max_length=255,
        default="'Inter Variable', sans-serif",
        help_text="Accent font family (used for special elements)"
    )
    font_mono = models.CharField(
        max_length=255,
        default="'JetBrains Mono', 'Fira Code', monospace",
        help_text="Monospace font family"
    )
    
    # Font weights
    font_weight_light = models.PositiveIntegerField(default=300)
    font_weight_normal = models.PositiveIntegerField(default=400)
    font_weight_medium = models.PositiveIntegerField(default=500)
    font_weight_semibold = models.PositiveIntegerField(default=600)
    font_weight_bold = models.PositiveIntegerField(default=700)
    
    # Line heights
    line_height_none = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    line_height_tight = models.DecimalField(max_digits=3, decimal_places=2, default=1.25)
    line_height_snug = models.DecimalField(max_digits=3, decimal_places=2, default=1.375)
    line_height_normal = models.DecimalField(max_digits=3, decimal_places=2, default=1.5)
    line_height_relaxed = models.DecimalField(max_digits=3, decimal_places=2, default=1.625)
    line_height_loose = models.DecimalField(max_digits=3, decimal_places=2, default=2.0)
    
    # Letter spacing
    letter_spacing_tighter = models.DecimalField(max_digits=4, decimal_places=3, default=-0.05)
    letter_spacing_tight = models.DecimalField(max_digits=4, decimal_places=3, default=-0.025)
    letter_spacing_normal = models.DecimalField(max_digits=4, decimal_places=3, default=0)
    letter_spacing_wide = models.DecimalField(max_digits=4, decimal_places=3, default=0.025)
    letter_spacing_wider = models.DecimalField(max_digits=4, decimal_places=3, default=0.05)
    letter_spacing_widest = models.DecimalField(max_digits=4, decimal_places=3, default=0.1)
    
    # Headings configuration
    headings = models.JSONField(
        default=dict,
        help_text="Advanced heading configurations (h1-h6)"
    )
    
    # Paragraph styles
    paragraph_margin = models.JSONField(
        default=dict,
        help_text="Margin settings for paragraphs"
    )
    
    # Text transforms
    text_transform_headings = models.CharField(
        max_length=20,
        default='none',
        choices=[
            ('none', 'None'),
            ('uppercase', 'Uppercase'),
            ('lowercase', 'Lowercase'),
            ('capitalize', 'Capitalize')
        ]
    )
    
    # Font loading strategy
    font_display = models.CharField(
        max_length=20,
        default='swap',
        choices=[
            ('auto', 'Auto'),
            ('block', 'Block'),
            ('swap', 'Swap'),
            ('fallback', 'Fallback'),
            ('optional', 'Optional')
        ],
        help_text="Controls how fonts are displayed while loading"
    )
    
    # Text rendering
    text_rendering = models.CharField(
        max_length=50,
        default='optimizeLegibility',
        choices=[
            ('auto', 'Auto'),
            ('optimizeSpeed', 'Optimize Speed'),
            ('optimizeLegibility', 'Optimize Legibility'),
            ('geometricPrecision', 'Geometric Precision')
        ]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'themes_typography'
        verbose_name_plural = "Typography"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.theme.name} Typography"
    
    def save(self, *args, **kwargs):
        if not self.headings:
            self.headings = self.get_default_headings()
        if not self.paragraph_margin:
            self.paragraph_margin = self.get_default_paragraph_margins()
        super().save(*args, **kwargs)
    
    def get_default_headings(self):
        """Generate default heading configurations"""
        return {
            'h1': {
                'font_size': {'base': '2.5rem', 'md': '3rem', 'lg': '3.5rem'},
                'line_height': 1.2,
                'letter_spacing': '-0.025em',
                'font_weight': self.font_weight_bold,
                'margin_top': '0',
                'margin_bottom': '1rem',
                'text_transform': self.text_transform_headings,
            },
            'h2': {
                'font_size': {'base': '2rem', 'md': '2.25rem', 'lg': '2.5rem'},
                'line_height': 1.25,
                'letter_spacing': '-0.025em',
                'font_weight': self.font_weight_semibold,
                'margin_top': '1.5rem',
                'margin_bottom': '1rem',
                'text_transform': self.text_transform_headings,
            },
            'h3': {
                'font_size': {'base': '1.75rem', 'md': '1.875rem', 'lg': '2rem'},
                'line_height': 1.3,
                'letter_spacing': '-0.025em',
                'font_weight': self.font_weight_semibold,
                'margin_top': '1.5rem',
                'margin_bottom': '1rem',
                'text_transform': self.text_transform_headings,
            },
            'h4': {
                'font_size': {'base': '1.5rem', 'md': '1.5rem', 'lg': '1.75rem'},
                'line_height': 1.35,
                'letter_spacing': '-0.02em',
                'font_weight': self.font_weight_semibold,
                'margin_top': '1.5rem',
                'margin_bottom': '1rem',
                'text_transform': self.text_transform_headings,
            },
            'h5': {
                'font_size': {'base': '1.25rem', 'md': '1.25rem', 'lg': '1.5rem'},
                'line_height': 1.4,
                'letter_spacing': '-0.015em',
                'font_weight': self.font_weight_semibold,
                'margin_top': '1.25rem',
                'margin_bottom': '0.75rem',
                'text_transform': self.text_transform_headings,
            },
            'h6': {
                'font_size': {'base': '1rem', 'md': '1rem', 'lg': '1.125rem'},
                'line_height': 1.5,
                'letter_spacing': '0em',
                'font_weight': self.font_weight_semibold,
                'margin_top': '1rem',
                'margin_bottom': '0.5rem',
                'text_transform': self.text_transform_headings,
            }
        }
    
    def get_default_paragraph_margins(self):
        """Generate default paragraph margins"""
        return {
            'margin_top': '0',
            'margin_bottom': '1rem',
            'first_child': {'margin_top': '0'},
            'last_child': {'margin_bottom': '0'}
        }
    
    def get_font_face_rules(self):
        """Generate @font-face rules for selected fonts"""
        return f"""
        /* Primary Font */
        @font-face {{
            font-family: 'Primary Font';
            src: local('{self.font_primary.split(",")[0].strip(" '")}'),
                 url('/fonts/primary.woff2') format('woff2'),
                 url('/fonts/primary.woff') format('woff');
            font-weight: 100 900;
            font-style: normal;
            font-display: {self.font_display};
        }}
        
        /* Secondary Font */
        @font-face {{
            font-family: 'Secondary Font';
            src: local('{self.font_secondary.split(",")[0].strip(" '")}'),
                 url('/fonts/secondary.woff2') format('woff2'),
                 url('/fonts/secondary.woff') format('woff');
            font-weight: 100 900;
            font-style: normal;
            font-display: {self.font_display};
        }}
        """
    
    def get_css_variables(self):
        """Generate CSS variables for typography"""
        return {
            '--font-sans': self.font_primary,
            '--font-serif': 'ui-serif, Georgia, Cambria, "Times New Roman", Times, serif',
            '--font-mono': self.font_mono,
            '--font-accent': self.font_accent,
            
            '--text-base': f'{self.base_font_size}px',
            '--text-scale-ratio': '1.2',
            
            '--font-weight-light': str(self.font_weight_light),
            '--font-weight-normal': str(self.font_weight_normal),
            '--font-weight-medium': str(self.font_weight_medium),
            '--font-weight-semibold': str(self.font_weight_semibold),
            '--font-weight-bold': str(self.font_weight_bold),
            
            '--line-height-none': str(self.line_height_none),
            '--line-height-tight': str(self.line_height_tight),
            '--line-height-snug': str(self.line_height_snug),
            '--line-height-normal': str(self.line_height_normal),
            '--line-height-relaxed': str(self.line_height_relaxed),
            '--line-height-loose': str(self.line_height_loose),
            
            '--letter-spacing-tighter': f'{self.letter_spacing_tighter}em',
            '--letter-spacing-tight': f'{self.letter_spacing_tight}em',
            '--letter-spacing-normal': f'{self.letter_spacing_normal}em',
            '--letter-spacing-wide': f'{self.letter_spacing_wide}em',
            '--letter-spacing-wider': f'{self.letter_spacing_wider}em',
            '--letter-spacing-widest': f'{self.letter_spacing_widest}em',
            
            '--text-rendering': self.text_rendering,
            '--font-smoothing': self.font_smoothing,
        }
