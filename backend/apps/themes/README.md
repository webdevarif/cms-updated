# Themes App

## Overview
The themes app provides a complete theming system for stores with support for color schemes, typography, style classes, layouts, and templates.

## Directory Structure
```
apps/
└── themes/
    ├── v2/                     # Version 2 (Current Only)
    │   ├── serializers/       # API serializers
    │   ├── services/          # Business logic
    │   ├── urls.py           # URL routing
    │   └── views/            # API views
    ├── models/                # Database models
    │   ├── theme.py
    │   ├── color_scheme.py
    │   ├── typography.py
    │   ├── style_class.py
    │   ├── layout.py
    │   └── template.py
    ├── admin.py
    ├── apps.py
    └── migrations/
```

## Models

### Theme
- Main theme model for each store
- Each store can have multiple themes, but only one active theme
- Fields: store, name, is_active, created_at, updated_at

### ColorScheme
- Color scheme with light/dark mode support
- Each theme can have multiple color schemes
- Includes default color palettes for both light and dark modes
- Fields: theme, store, name, key, colors, dark_colors, is_default

### Typography
- Typography settings for themes with comprehensive controls
- Supports responsive typography and font loading
- Fields: theme, store, base_font_size, font_smoothing, font_primary, font_secondary, etc.

### StyleClass
- Reusable style classes with light/dark mode support
- Supports version-specific overrides
- Fields: theme, store, name, slug, default_css, light_css, dark_css, etc.

### Layout
- Defines global structure including header, footer, and content slots
- Each theme can have multiple layouts, with one default layout
- Fields: theme, store, name, key, header_template, footer_template, content_slots, is_default, is_system

### Template
- Defines reusable template components with a specific role in the layout system
- Templates are body-only by default, with specialized roles for headers and footers
- Fields: theme, store, name, key, template_role, content, custom_css, custom_js, is_default, is_system, layout

## API Endpoints

### Public API (v2)
- `GET /api/v2/themes/current/` - Get current theme
- `GET /api/v2/themes/current/scheme/` - Get active color scheme
- `GET /api/v2/templates/{type}/{slug}/` - Get template by type and slug

### Dashboard API (v2)
- `GET /api/v2/dashboard/themes/` - List themes
- `POST /api/v2/dashboard/themes/` - Create theme
- `GET /api/v2/dashboard/themes/{id}/` - Get theme
- `PUT /api/v2/dashboard/themes/{id}/` - Update theme
- `DELETE /api/v2/dashboard/themes/{id}/` - Delete theme
- `POST /api/v2/dashboard/themes/{id}/activate/` - Activate theme
- `GET /api/v2/dashboard/templates/` - List templates
- `POST /api/v2/dashboard/templates/` - Create template
- `GET /api/v2/dashboard/templates/{id}/` - Get template
- `PUT /api/v2/dashboard/templates/{id}/` - Update template
- `DELETE /api/v2/dashboard/templates/{id}/` - Delete template

## Services

### ThemeService
- `create_theme(store, name, user=None)` - Create a new theme for a store
- `get_active_theme(store)` - Get active theme for a store
- `activate_theme(theme_id)` - Activate a theme

### TemplateService
- `create_default_templates(theme, user=None)` - Create default templates for a theme
- `render_template(template, context=None)` - Render a template with context
- `get_template_variables(template)` - Get variables used in a template

## Integration with Store Bootstrap

The themes app is integrated with the store bootstrap process in Phase 5:

```python
# In apps/stores/services.py
@staticmethod
def _phase5_theme(store):
    """Phase 5: Theme initialization"""
    try:
        from apps.themes.v2.services import ThemeService, TemplateService
        
        # Create default theme
        theme = ThemeService.create_theme(store, 'Default Theme')
        
        # Activate the theme
        theme.activate()
        
        # Create default templates
        TemplateService.create_default_templates(theme)
        
    except Exception as e:
        logger.warning(f"Phase 5 skipped for store {store.slug}: {e}")
    
    store.bootstrap_phase = 'phase5_complete'
    store.save(update_fields=['bootstrap_phase'])
    logger.info(f"Phase 5 complete for store: {store.slug}")
```

## Compatibility

This themes app is compatible with:
- **Logs app**: Uses async logging for all mutations
- **Accounts app**: Uses User model for created_by fields
- **Stores app**: Integrates with Store model and StoreBootstrapService
- **Store-bootstrap**: Follows the 8-phase bootstrap lifecycle

## Migration Commands

```bash
# Create migrations
python manage.py makemigrations themes

# Apply migrations
python manage.py migrate themes
```

## Testing

```bash
# Run tests for themes app
python manage.py test apps.themes
```

## Notes

1. The themes app uses v2 only (no backward compatibility with v1)
2. All models include proper store scoping for multi-tenancy
3. Templates are body-only by default (no <html>, <head>, or <body> tags)
4. Layouts define page structure (header + footer + content slots)
5. Pages can override their layout
6. System templates and themes cannot be deleted (is_system flag)
