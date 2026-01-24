"""Template service."""
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class TemplateService:
    """Template management service"""
    
    @staticmethod
    @transaction.atomic
    def create_default_templates(theme):
        """Create default templates for a theme using centralized service"""
        from ..models import Template, Layout
        from apps.logs.tasks import log_event_async
        
        # Create default layout using centralized method
        layout = TemplateService.create_default_layout(theme)
        
        # Create body template using centralized method
        body_template = TemplateService.create_body_template(theme, layout)
        
        # Create header template using centralized method
        header_template = TemplateService.create_header_template(theme, layout)
        
        # Create footer template using centralized method
        footer_template = TemplateService.create_footer_template(theme, layout)
        
        log_event_async.delay({
            'event_type': 'TEMPLATES_CREATED',
            'message': f"Default templates created for theme: {theme.name}",
            'store': theme.store,
            'entity_type': 'Template',
            'entity_id': body_template.id,
            'metadata': {
                'theme_id': theme.id,
                'template_count': 4
            }
        })
        
        return {
            'layout': layout,
            'body': body_template,
            'header': header_template,
            'footer': footer_template
        }
    
    @staticmethod
    def create_default_layout(theme):
        """Create default layout"""
        from ..models import Layout
        
        return Layout.objects.create(
            theme=theme,
            store=theme.store,
            name="Default Layout",
            template_type="layout",
            content="{% include 'header' %}\n{% block content %}{% endblock %}\n{% include 'footer' %}",
            is_default=True
        )
    
    @staticmethod
    def create_body_template(theme, layout):
        """Create body template"""
        from ..models import Template
        
        return Template.objects.create(
            theme=theme,
            store=theme.store,
            name="Default Body",
            template_type="body",
            role="body",
            content="{% extends layout %}\n\n{% block content %}\n    <main>\n        {% block main %}{% endblock %}\n    </main>\n{% endblock %}",
            layout=layout,
            is_default=True
        )
    
    @staticmethod
    def create_header_template(theme, layout):
        """Create header template"""
        from ..models import Template
        
        return Template.objects.create(
            theme=theme,
            store=theme.store,
            name="Default Header",
            template_type="partial",
            role="header",
            content="<header>\n    <nav>\n        <a href=\"/\">{{ store.name }}</a>\n    </nav>\n</header>",
            layout=layout,
            is_default=True
        )
    
    @staticmethod
    def create_footer_template(theme, layout):
        """Create footer template"""
        from ..models import Template
        
        return Template.objects.create(
            theme=theme,
            store=theme.store,
            name="Default Footer",
            template_type="partial",
            role="footer",
            content="<footer>\n    <p>&copy; 2024 {{ store.name }}. All rights reserved.</p>\n</footer>",
            layout=layout,
            is_default=True
        )
        
        logger.info(f"Default templates created for theme: {theme.name}")
        
        return {
            'layout': layout,
            'body_template': body_template,
            'header_template': header_template,
            'footer_template': footer_template
        }
    
    @staticmethod
    def render_template(template, context=None):
        """Render a template with context"""
        return template.render_content(context)
    
    @staticmethod
    def get_template_variables(template):
        """Get variables used in a template"""
        return template.get_variables_list()
