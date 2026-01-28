# Themes Rules v1.0

## 🎯 Purpose
This document defines the development rules for the **themes** app in CMS-Updated backend, providing a simplified yet powerful theming system that supports multiple color schemes, typography settings, and custom styles while maintaining a clean architecture.
---

## 🏗️ Structure
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

## 🔧 Implementation
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

## 🧪 Testing
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

## ⚙️ Services
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

## 🔗 Dependencies
[Dependencies content to be added]

## 📋 Migration
```bash
python manage.py makemigrations themes
python manage.py migrate themes
```

---

## ✅ Benefits
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

---
**Version**: 1.0
**Last Updated**: 2026-01-26
**Next Review**: 2026-02-25
