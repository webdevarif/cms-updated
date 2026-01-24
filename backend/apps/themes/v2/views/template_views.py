"""Template views."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.viewsets import StoreScopedViewSet


class TemplatePublicViewSet(viewsets.ReadOnlyModelViewSet):
    """Public template API"""
    
    def get_queryset(self):
        """Get templates for store"""
        store_id = self.kwargs.get('store_id')
        template_role = self.request.query_params.get('role', None)
        from ..models import Template
        queryset = Template.objects.filter(store_id=store_id, is_active=True)
        
        if template_role:
            queryset = queryset.filter(template_role=template_role)
        
        return queryset
    
    def get_serializer_class(self):
        """Get appropriate serializer"""
        from ..v2.serializers import TemplatePublicSerializer
        return TemplatePublicSerializer
    
    @action(detail=False, methods=['get'])
    def by_role(self, request):
        """Get templates by role"""
        template_role = self.request.query_params.get('role', 'body')
        store_id = self.kwargs.get('store_id')
        from ..models import Template
        
        templates = Template.objects.filter(
            store_id=store_id,
            template_role=template_role,
            is_active=True
        )
        
        from ..v2.serializers import TemplatePublicSerializer
        serializer = TemplatePublicSerializer(templates, many=True)
        return Response(serializer.data)


class TemplateDashboardViewSet(StoreScopedViewSet):
    """Dashboard template management API"""
    
    def get_queryset(self):
        """Filter by current store"""
        from ..models import Template
        return Template.objects.filter(store=self.request.user.stores.first())
    
    def get_serializer_class(self):
        """Get appropriate serializer"""
        from ..v2.serializers import TemplateSerializer, TemplateCreateSerializer
        if self.action in ['create']:
            return TemplateCreateSerializer
        return TemplateSerializer
    
    @action(detail=True, methods=['post'])
    def render(self, request, pk=None):
        """Render template with context"""
        template = self.get_object()
        context = request.data.get('context', {})
        
        rendered = template.render_content(context)
        return Response({'rendered': rendered})
    
    @action(detail=True, methods=['get'])
    def variables(self, request, pk=None):
        """Get template variables"""
        template = self.get_object()
        variables = template.get_variables_list()
        return Response({'variables': variables})
