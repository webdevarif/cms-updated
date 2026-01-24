# Themes App Rules v1.0

## 🎯 Purpose

This document defines the development rules for the **themes** app in CMS-Updated backend, providing a simplified yet powerful theming system that supports multiple color schemes, typography settings, and custom styles while maintaining a clean architecture.

---

## 🏗️ Themes App Structure

### **Fixed Directory Structure**
```
apps/
└── themes/
    ├── v2/                     # Version 2 (Current Only)
    │   ├── serializers/       # API serializers
    │   ├── services/          # Business logic
    │   ├── templates/         # Default theme templates
    │   ├── templatetags/      # Template tags and filters
    │   ├── tests/             # Unit and integration tests
    │   ├── urls.py           # URL routing
    │   └── views/            # API views
    ├── models/                # Database models
    │   ├── __init__.py
    │   ├── theme.py
    │   ├── color_scheme.py
    │   ├── typography.py
    │   ├── style_class.py
    │   └── template.py
    ├── admin.py
    ├── apps.py
    └── migrations/
```

---

## 🧩 Core Models

### **1. Theme Model**
```python
class Theme(TenantModel):
    """
    Main theme model for each store.
    Each store can have multiple themes, but only one active theme.
    """
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="Default Theme")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_active', 'name']
        unique_together = [['store', 'name']]
```

### **2. Color Scheme**
```python
class ColorScheme(models.Model):
    """
    Color scheme with light/dark mode support.
    Each theme can have multiple color schemes.
    """
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='color_schemes')
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
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
        unique_together = [['theme', 'key']]
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.colors:
            self.colors = self.get_default_colors('light')
        if not self.dark_colors:
            self.dark_colors = self.get_default_colors('dark')
        super().save(*args, **kwargs)

    @staticmethod
    def get_default_colors(mode='light'):
        """Return default color scheme based on mode (light/dark)"""
        base = {
            'background': '#ffffff' if mode == 'light' else '#111827',
            'foreground': '#111827' if mode == 'light' else '#f3f4f6',
            'muted': '#6b7280' if mode == 'light' else '#9ca3af',
            'muted_foreground': '#374151' if mode == 'light' else '#d1d5db',
            
            # Primary colors
            'primary': '#3b82f6',
            'primary_foreground': '#ffffff',
            'primary_hover': '#2563eb',
            
            # Secondary colors
            'secondary': '#f3f4f6' if mode == 'light' else '#1f2937',
            'secondary_foreground': '#111827' if mode == 'light' else '#f9fafb',
            'secondary_hover': '#e5e7eb' if mode == 'light' else '#374151',
            
            # Accent colors
            'accent': '#f59e0b',
            'accent_foreground': '#ffffff',
            'accent_hover': '#d97706',
            
            # Destructive colors
            'destructive': '#ef4444',
            'destructive_foreground': '#ffffff',
            'destructive_hover': '#dc2626',
            
            # Success colors
            'success': '#10b981',
            'success_foreground': '#ffffff',
            'success_hover': '#059669',
            
            # Warning colors
            'warning': '#f59e0b',
            'warning_foreground': '#ffffff',
            'warning_hover': '#d97706',
            
            # Info colors
            'info': '#3b82f6',
            'info_foreground': '#ffffff',
            'info_hover': '#2563eb',
            
            # Border colors
            'border': '#e5e7eb' if mode == 'light' else '#374151',
            'input': '#d1d5db' if mode == 'light' else '#4b5563',
            'ring': '#93c5fd',
            
            # Card colors
            'card': '#ffffff' if mode == 'light' else '#1f2937',
            'card_foreground': '#111827' if mode == 'light' else '#f9fafb',
            
            # Popover colors
            'popover': '#ffffff' if mode == 'light' else '#1f2937',
            'popover_foreground': '#111827' if mode == 'light' else '#f9fafb',
            
            # Tooltip colors
            'tooltip': '#111827' if mode == 'light' else '#f3f4f6',
            'tooltip_foreground': '#f9fafb' if mode == 'light' else '#111827',
            
            # Overlay colors
            'overlay': 'rgba(0, 0, 0, 0.5)',
            
            # Shadow colors
            'shadow': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
            
            # Button variants
            'button_primary': {
                'background': '#3b82f6',
                'foreground': '#ffffff',
                'hover': '#2563eb',
                'border': '#3b82f6',
            },
            'button_secondary': {
                'background': '#f3f4f6' if mode == 'light' else '#374151',
                'foreground': '#111827' if mode == 'light' else '#f9fafb',
                'hover': '#e5e7eb' if mode == 'light' else '#4b5563',
                'border': '#e5e7eb' if mode == 'light' else '#4b5563',
            },
            'button_outline': {
                'background': 'transparent',
                'foreground': '#3b82f6',
                'hover': '#f3f4f6' if mode == 'light' else '#1f2937',
                'border': '#d1d5db',
            },
            'button_ghost': {
                'background': 'transparent',
                'foreground': '#3b82f6',
                'hover': '#f3f4f6' if mode == 'light' else '#1f2937',
                'border': 'transparent',
            },
            'button_link': {
                'background': 'transparent',
                'foreground': '#3b82f6',
                'hover': 'transparent',
                'border': 'transparent',
                'underline': True,
            },
            
            # Form elements
            'input_background': '#ffffff' if mode == 'light' else '#1f2937',
            'input_foreground': '#111827' if mode == 'light' else '#f9fafb',
            'input_placeholder': '#9ca3af',
            'input_border': '#d1d5db',
            'input_ring': '#93c5fd',
            
            # Checkbox/radio
            'checkbox_background': '#ffffff' if mode == 'light' else '#1f2937',
            'checkbox_foreground': '#3b82f6',
            'checkbox_border': '#d1d5db',
            
            # Toggle
            'toggle_background': '#e5e7eb' if mode == 'light' else '#374151',
            'toggle_foreground': '#3b82f6',
            
            # Badge variants
            'badge_primary': {
                'background': '#dbeafe',
                'foreground': '#1e40af',
            },
            'badge_secondary': {
                'background': '#e5e7eb' if mode == 'light' else '#374151',
                'foreground': '#111827' if mode == 'light' else '#f9fafb',
            },
            'badge_destructive': {
                'background': '#fee2e2',
                'foreground': '#b91c1c',
            },
            'badge_outline': {
                'background': 'transparent',
                'foreground': '#111827' if mode == 'light' else '#f9fafb',
                'border': '#e5e7eb' if mode == 'light' else '#374151',
            },
        }
        
        return base
```

### **3. Typography**
```python
class Typography(models.Model):
    """
    Typography settings for themes with comprehensive controls.
    Supports responsive typography and font loading.
    """
    theme = models.OneToOneField(Theme, on_delete=models.CASCADE, related_name='typography')
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
        verbose_name_plural = "Typography"
        ordering = ['-created_at']
    
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
```

### **4. Style Class**
```python
class StyleClass(models.Model):
    """
    Reusable style classes with light/dark mode support and version-specific overrides.
    """
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='style_classes')
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    
    # Default CSS properties (base styles)
    default_css = models.JSONField(
        default=dict,
        help_text="Default CSS properties for this style class"
    )
    
    # Light/Dark mode overrides
    light_css = models.JSONField(
        default=dict,
        blank=True,
        help_text="Light mode CSS overrides (merges with default_css)"
    )
    dark_css = models.JSONField(
        default=dict,
        blank=True,
        help_text="Dark mode CSS overrides (merges with default_css)"
    )
    
    # Version-specific overrides (for different template versions)
    version_css = models.JSONField(
        default=dict,
        blank=True,
        help_text="Version-specific CSS overrides (e.g., {'v1': {...}, 'v2': {...}})"
    )
    
    # Media queries for responsive design
    media_queries = models.JSONField(
        default=dict,
        blank=True,
        help_text="Responsive styles (e.g., {'sm': {...}, 'md': {...}, 'lg': {...}})"
    )
    
    # Pseudo-class styles
    pseudo_classes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Pseudo-class styles (e.g., {'hover': {...}, 'focus': {...}, 'active': {...}})"
    )
    
    # Animation properties
    animations = models.JSONField(
        default=dict,
        blank=True,
        help_text="Animation properties (e.g., {'transition': 'all 0.3s ease', 'animation': 'fadeIn 0.5s'})"
    )
    
    # Custom CSS (raw CSS for complex styles)
    custom_css = models.TextField(
        blank=True,
        help_text="Raw CSS for complex styles that can't be expressed in JSON"
    )
    
    # Version-specific custom CSS
    version_custom_css = models.JSONField(
        default=dict,
        blank=True,
        help_text="Version-specific raw CSS (e.g., {'v1': '...', 'v2': '...'})"
    )
    
    # CSS variables for this class
    css_variables = models.JSONField(
        default=dict,
        blank=True,
        help_text="CSS variables specific to this class"
    )
    
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False, help_text="System style classes cannot be deleted")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['theme', 'slug']]
        ordering = ['name']
    
    def get_css_for_version(self, version='default', mode='light'):
        """
        Get CSS properties for a specific version and mode
        """
        # Start with default CSS
        css = self.default_css.copy()
        
        # Apply mode-specific overrides
        if mode == 'dark' and self.dark_css:
            css.update(self.dark_css)
        elif mode == 'light' and self.light_css:
            css.update(self.light_css)
        
        # Apply version-specific overrides
        if version != 'default' and self.version_css.get(version):
            css.update(self.version_css[version])
        
        return css
    
    def get_custom_css_for_version(self, version='default'):
        """
        Get custom CSS for a specific version
        """
        if version != 'default' and self.version_custom_css.get(version):
            return self.version_custom_css[version]
        return self.custom_css
    
    def get_media_query_css(self, version='default', mode='light'):
        """
        Get media query CSS for responsive design
        """
        result = {}
        for breakpoint, styles in self.media_queries.items():
            # Apply version and mode overrides to media query styles
            css = styles.copy()
            if mode == 'dark' and self.dark_css:
                css.update(self.dark_css)
            if version != 'default' and self.version_css.get(version):
                css.update(self.version_css[version])
            result[breakpoint] = css
        return result
    
    def get_pseudo_class_css(self, pseudo_class, version='default', mode='light'):
        """
        Get pseudo-class CSS (hover, focus, active, etc.)
        """
        css = self.pseudo_classes.get(pseudo_class, {}).copy()
        
        # Apply mode-specific overrides
        if mode == 'dark' and self.dark_css:
            css.update(self.dark_css)
        elif mode == 'light' and self.light_css:
            css.update(self.light_css)
        
        # Apply version-specific overrides
        if version != 'default' and self.version_css.get(version):
            css.update(self.version_css[version])
        
        return css
    
    def generate_css_class(self, version='default', mode='light'):
        """
        Generate complete CSS class with all properties
        """
        css_rules = []
        
        # Main class
        main_css = self.get_css_for_version(version, mode)
        if main_css:
            main_props = '; '.join([f"{k}: {v}" for k, v in main_css.items()])
            css_rules.append(f".{self.slug} {{ {main_props}; }}")
        
        # Media queries
        media_css = self.get_media_query_css(version, mode)
        for breakpoint, styles in media_css.items():
            if styles:
                props = '; '.join([f"{k}: {v}" for k, v in styles.items()])
                css_rules.append(f"@media (min-width: {breakpoint}) {{ .{self.slug} {{ {props}; }} }}")
        
        # Pseudo-classes
        for pseudo in ['hover', 'focus', 'active', 'disabled']:
            pseudo_css = self.get_pseudo_class_css(pseudo, version, mode)
            if pseudo_css:
                props = '; '.join([f"{k}: {v}" for k, v in pseudo_css.items()])
                css_rules.append(f".{self.slug}:{pseudo} {{ {props}; }}")
        
        # Custom CSS
        custom_css = self.get_custom_css_for_version(version)
        if custom_css:
            css_rules.append(custom_css)
        
        # CSS variables
        if self.css_variables:
            var_props = '; '.join([f"{k}: {v}" for k, v in self.css_variables.items()])
            css_rules.append(f".{self.slug} {{ {var_props}; }}")
        
        return '\n'.join(css_rules)
    
    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
```

### **5. Layout**
```python
class Layout(models.Model):
    """
    Defines global structure including header, footer, and content slots.
    Each theme can have multiple layouts, with one default layout.
    """
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='layouts')
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    key = models.SlugField(max_length=100)
    description = models.TextField(blank=True)

    # Header & footer templates
    header_template = models.ForeignKey(
        'Template',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_as_header'
    )
    footer_template = models.ForeignKey(
        'Template',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_as_footer'
    )

    # Layout settings
    is_default = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Content slots (for dynamic content injection)
    content_slots = models.JSONField(
        default=dict,
        blank=True,
        help_text="Defines content slots and their default content"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['theme', 'key']]
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.theme.name})"

    def clean(self):
        # Ensure only one default layout per theme
        if self.is_default and self.theme:
            Layout.objects.filter(
                theme=self.theme, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
```

### **6. Template**
```python
class Template(models.Model):
    """
    Defines reusable template components with a specific role in the layout system.
    Templates are body-only by default, with specialized roles for headers and footers.
    """
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='templates')
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    
    TEMPLATE_ROLES = [
        ('body', 'Body'),        # Main content (default)
        ('header', 'Header'),    # Header component
        ('footer', 'Footer'),    # Footer component
        ('partial', 'Partial'),  # Reusable partials
        ('section', 'Section'),  # Page sections
    ]
    
    name = models.CharField(max_length=100)
    key = models.SlugField(max_length=100)
    template_role = models.CharField(
        max_length=20,
        choices=TEMPLATE_ROLES,
        default='body',
        help_text="Defines the template's role in the layout system"
    )
    description = models.TextField(blank=True)
    
    # Template content (body-only for header/footer roles)
    content = models.TextField(
        help_text="HTML template with variables (Django template syntax)"
    )
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    key = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    
    # Template content
    content = models.TextField(
        help_text="HTML template with variables (Django template syntax)"
    )
    
    # Advanced customization tab
    custom_css = models.TextField(
        blank=True,
        help_text="Custom CSS for this template"
    )
    custom_js = models.TextField(
        blank=True,
        help_text="Custom JavaScript for this template"
    )
    
    # Version-specific customizations
    version_css = models.JSONField(
        default=dict,
        blank=True,
        help_text="Version-specific CSS (e.g., {'v1': '...', 'v2': '...'})"
    )
    version_js = models.JSONField(
        default=dict,
        blank=True,
        help_text="Version-specific JavaScript (e.g., {'v1': '...', 'v2': '...'})"
    )
    
    # Template metadata
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Default meta title for pages using this template"
    )
    meta_description = models.TextField(
        blank=True,
        help_text="Default meta description for pages using this template"
    )
    meta_keywords = models.CharField(
        max_length=500,
        blank=True,
        help_text="Default meta keywords for pages using this template"
    )
    
    # Template settings
    is_default = models.BooleanField(
        default=False,
        help_text="Default template for this type and role"
    )
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(
        default=False,
        help_text="System templates cannot be deleted"
    )
    
    # Layout association (for body templates)
    layout = models.ForeignKey(
        'Layout',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Default layout for this template (body templates only)",
        related_name='templates_using_this_layout'
    )
    
    # Template variables (for documentation)
    variables = models.JSONField(
        default=dict,
        blank=True,
        help_text="Available variables in this template"
    )
    
    # Template dependencies
    requires = models.JSONField(
        default=list,
        blank=True,
        help_text="Required components or templates"
    )
    
    # Preview settings
    preview_image = models.URLField(
        blank=True,
        help_text="Preview image for template selection"
    )
    preview_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Sample data for template preview"
    )
    
    # Performance settings
    cache_duration = models.PositiveIntegerField(
        default=300,
        help_text="Cache duration in seconds"
    )
    minify_html = models.BooleanField(
        default=False,
        help_text="Minify HTML output"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['theme', 'key']]
        ordering = ['template_type', 'name']
        indexes = [
            models.Index(fields=['theme', 'template_type']),
            models.Index(fields=['is_default', 'is_active']),
        ]
    
    def get_css_for_version(self, version='default'):
        """
        Get CSS for a specific version
        """
        if version != 'default' and self.version_css.get(version):
            return self.version_css[version]
        return self.custom_css
    
    def get_js_for_version(self, version='default'):
        """
        Get JavaScript for a specific version
        """
        if version != 'default' and self.version_js.get(version):
            return self.version_js[version]
        return self.custom_js
    
    def render_content(self, context=None):
        """
        Render template content with context.
        For header/footer templates, ensures no <html> or <body> tags.
        """
        from django.template import Template, Context
        from django.template.exceptions import TemplateSyntaxError
        
        content = Template(self.content).render(Context(context or {}))
            'template_name': self.name,
            'template_key': self.key,
        })
        
        # Render the template
        django_template = DjangoTemplate(self.content)
        return django_template.render(DjangoContext(template_context))
    
    def get_variables_list(self):
        """
        Extract variables from template content
        """
        import re
        variables = set()
        
        # Find Django template variables
        pattern = r'\{\{\s*([^}]+)\s*\}\}'
        matches = re.findall(pattern, self.content)
        
        for match in matches:
            # Clean up the variable name
            var = match.strip().split('.')[0].strip()
            if var and not var.startswith('|') and not var.startswith('if'):
                variables.add(var)
        
        return sorted(list(variables))
    
    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        
        # Extract variables from content
        if not self.variables:
            self.variables = self.get_variables_list()
        
        super().save(*args, **kwargs)

---

## API Endpoints

### **Public API (v2)**
```
GET    /api/v2/themes/current/           # Get current theme
GET    /api/v2/themes/current/scheme/    # Get active color scheme
GET    /api/v2/templates/{type}/{slug}/  # Get template by type and slug
```

### **Dashboard API (v2)**
```
# Themes
GET    /api/v2/dashboard/themes/                 # List themes
POST   /api/v2/dashboard/themes/                 # Create theme
GET    /api/v2/dashboard/themes/{id}/            # Get theme
PUT    /api/v2/dashboard/themes/{id}/            # Update theme
DELETE /api/v2/dashboard/themes/{id}/            # Delete theme
POST   /api/v2/dashboard/themes/{id}/activate/   # Activate theme

# Color Schemes
GET    /api/v2/dashboard/themes/{id}/schemes/    # List color schemes
POST   /api/v2/dashboard/themes/{id}/schemes/    # Create color scheme

# Templates
GET    /api/v2/dashboard/templates/              # List templates
POST   /api/v2/dashboard/templates/              # Create template
GET    /api/v2/dashboard/templates/{id}/         # Get template
PUT    /api/v2/dashboard/templates/{id}/         # Update template
DELETE /api/v2/dashboard/templates/{id}/         # Delete template
```

---

## 🔒 Permissions

### **Public Access**
- Read-only access to active theme and templates
- No authentication required

### **Store Staff**
- Full CRUD on own store's themes
- Can activate/deactivate themes
- Can manage color schemes and templates

### **Super Admin**
- Full access to all themes across stores
- Can manage global theme settings

---

## 🧪 Testing Strategy

### **Unit Tests**
- Model validation and methods
- Service layer logic
- Template rendering

### **Integration Tests**
- API endpoints
- Theme activation flow
- Template inheritance

### **Performance Tests**
- Theme compilation
- Template rendering speed
- Asset loading

---

## 🚀 Deployment

### **Environment Variables**
```bash
# Theme Settings
DEFAULT_THEME="default"
THEME_CACHE_TIMEOUT=3600  # 1 hour
ENABLE_THEME_PREVIEW=true
```

### **Required Services**
- Redis (for theme caching)
- Storage (for theme assets)

### **Migrations**
```bash
python manage.py makemigrations themes
python manage.py migrate themes
```

---

## 📝 Implementation Notes

1. **Caching Strategy**
   - Cache compiled themes
   - Invalidate on theme update
   - Use cache tags for selective invalidation

2. **Template Variables**
   - Use Django template syntax
   - Predefined variables: `{{ store }}`, `{{ page }}`, `{{ request }}`
   - Custom variables via context processors

3. **Asset Management**
   - Store assets in theme-specific directories
   - Version assets for cache busting
   - Support CDN integration

4. **Theme Editor**
   - Live preview
   - Undo/redo functionality
   - Version history

---

## 🔄 Versioning

- Current version: v2 (only version)
- No backward compatibility with v1
- All new features go into v2

---

## 📚 References

1. [Shopify Theme Architecture](https://shopify.dev/themes/architecture)
2. [Django Templates](https://docs.djangoproject.com/en/stable/topics/templates/)
3. [Tailwind CSS Configuration](https://tailwindcss.com/docs/configuration)

---

## ✅ Checklist

### **Phase 1: Core Functionality**
- [ ] Theme model and API
- [ ] Color scheme management
- [ ] Basic template rendering

### **Phase 2: Advanced Features**
- [ ] Typography system
- [ ] Style classes
- [ ] Template inheritance

### **Phase 3: Editor & Tools**
- [ ] Theme editor UI
- [ ] Asset management
- [ ] Preview system

### **Phase 4: Optimization**
- [ ] Caching layer
- [ ] Performance tuning
- [ ] Documentation

---

## 📅 Timeline

- **Week 1-2**: Core models and API
- **Week 3-4**: Template system
- **Week 5-6**: Editor UI
- **Week 7-8**: Testing and optimization

---

## 🧩 Layout System

### Core Concepts

1. **Templates are body-only by default**
   - No `<html>`, `<head>`, or `<body>` tags in templates
   - Each template has a specific role (body, header, footer, etc.)

2. **Layouts define page structure**
   - Composed of header, footer, and content slots
   - Multiple layouts per theme, with one default
   - Pages can override their layout

3. **Separation of concerns**
   - Layout = Structure (header + footer + slots)
   - Template = Content (body only)
   - Page = Template + Layout

### Implementation Rules

1. **Template Roles**
   ```python
   # Allowed template roles
   TEMPLATE_ROLES = [
       ('body', 'Body'),        # Main content (default)
       ('header', 'Header'),    # Header component
       ('footer', 'Footer'),    # Footer component
       ('partial', 'Partial'),  # Reusable partials
       ('section', 'Section'),  # Page sections
   ]
   ```

2. **Layout Resolution**
   ```python
   def get_page_layout(page):
       """Resolve layout for a page with fallbacks"""
       # 1. Page-specific layout
       if page.layout:
           return page.layout
           
       # 2. Template's default layout
       if page.template and page.template.layout:
           return page.template.layout
           
       # 3. Theme's default layout
       return Layout.objects.filter(
           theme=page.theme,
           is_default=True
       ).first()
   ```

3. **Rendering Flow**
   ```python
   def render_page(page, context):
       """Render a complete page with layout"""
       layout = get_page_layout(page)
       
       # Start with empty HTML
       html = []
       
       # Add header if layout has one
       if layout and layout.header_template:
           html.append(layout.header_template.render_content(context))
       
       # Add main content
       html.append(page.template.render_content(context))
       
       # Add footer if layout has one
       if layout and layout.footer_template:
           html.append(layout.footer_template.render_content(context))
           
       return '\n'.join(html)
   ```

## 🚨 Known Limitations

1. No visual editor (code-only templates)
2. Limited to single-level template inheritance
3. No built-in theme marketplace

---

## 🔮 Future Enhancements

1. Visual theme editor
2. Theme marketplace
3. A/B testing for themes
4. Theme versioning and rollback
5. Multi-language support

---

Last Updated: January 23, 2026
