"""Tests for theme models."""
from django.test import TestCase
from apps.themes.models import Theme, ColorScheme, Typography, StyleClass, Layout, Template
from apps.stores.models import Store


class ThemeModelTest(TestCase):
    """Test Theme model"""
    
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            slug="test-store",
            owner=None
        )
    
    def test_theme_creation(self):
        """Test creating a theme"""
        theme = Theme.objects.create(
            store=self.store,
            name="Test Theme"
        )
        self.assertEqual(theme.name, "Test Theme")
        self.assertFalse(theme.is_active)
    
    def test_theme_activation(self):
        """Test activating a theme"""
        theme1 = Theme.objects.create(
            store=self.store,
            name="Theme 1",
            is_active=True
        )
        theme2 = Theme.objects.create(
            store=self.store,
            name="Theme 2",
            is_active=False
        )
        
        theme2.activate()
        
        theme1.refresh_from_db()
        theme2.refresh_from_db()
        
        self.assertFalse(theme1.is_active)
        self.assertTrue(theme2.is_active)
    
    def test_get_active_color_scheme(self):
        """Test getting active color scheme"""
        theme = Theme.objects.create(
            store=self.store,
            name="Test Theme"
        )
        
        color_scheme = ColorScheme.objects.create(
            theme=theme,
            store=self.store,
            name="Default",
            key="default",
            is_default=True
        )
        
        active_scheme = theme.get_active_color_scheme()
        self.assertEqual(active_scheme, color_scheme)


class ColorSchemeModelTest(TestCase):
    """Test ColorScheme model"""
    
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            slug="test-store",
            owner=None
        )
        self.theme = Theme.objects.create(
            store=self.store,
            name="Test Theme"
        )
    
    def test_color_scheme_creation(self):
        """Test creating a color scheme"""
        color_scheme = ColorScheme.objects.create(
            theme=self.theme,
            store=self.store,
            name="Light",
            key="light"
        )
        
        self.assertEqual(color_scheme.name, "Light")
        self.assertIsNotNone(color_scheme.colors)
        self.assertIsNotNone(color_scheme.dark_colors)
    
    def test_default_colors(self):
        """Test default colors are populated"""
        color_scheme = ColorScheme.objects.create(
            theme=self.theme,
            store=self.store,
            name="Light",
            key="light"
        )
        
        self.assertIn('primary', color_scheme.colors)
        self.assertIn('background', color_scheme.colors)
        self.assertIn('primary', color_scheme.dark_colors)


class TemplateModelTest(TestCase):
    """Test Template model"""
    
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            slug="test-store",
            owner=None
        )
        self.theme = Theme.objects.create(
            store=self.store,
            name="Test Theme"
        )
        self.layout = Layout.objects.create(
            theme=self.theme,
            store=self.store,
            name="Default Layout",
            key="default",
            is_default=True
        )
    
    def test_template_creation(self):
        """Test creating a template"""
        template = Template.objects.create(
            theme=self.theme,
            store=self.store,
            name="Body Template",
            key="body_template",
            template_role="body",
            content="<div>{{ content }}</div>",
            layout=self.layout
        )
        
        self.assertEqual(template.name, "Body Template")
        self.assertEqual(template.template_role, "body")
    
    def test_template_rendering(self):
        """Test rendering template content"""
        template = Template.objects.create(
            theme=self.theme,
            store=self.store,
            name="Body Template",
            key="body_template",
            template_role="body",
            content="<div>{{ content }}</div>",
            layout=self.layout
        )
        
        rendered = template.render_content({'content': 'Hello World'})
        self.assertIn('Hello World', rendered)
    
    def test_template_variables_extraction(self):
        """Test extracting variables from template"""
        template = Template.objects.create(
            theme=self.theme,
            store=self.store,
            name="Body Template",
            key="body_template",
            template_role="body",
            content="<div>{{ title }} {{ content }}</div>",
            layout=self.layout
        )
        
        variables = template.get_variables_list()
        self.assertIn('title', variables)
        self.assertIn('content', variables)
