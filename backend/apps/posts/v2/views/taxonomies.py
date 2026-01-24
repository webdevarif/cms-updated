"""
Views for taxonomy and term management.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from .base import StoreScopedViewSet
from ..models import Taxonomy, Term
from apps.logs.tasks import log_event_async


class TaxonomyViewSet(StoreScopedViewSet):
    """API endpoint for managing taxonomies"""
    queryset = Taxonomy.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        from ..serializers import TaxonomySerializer, TaxonomyCreateSerializer
        if self.action == 'create':
            return TaxonomyCreateSerializer
        return TaxonomySerializer


class TermViewSet(StoreScopedViewSet):
    """API endpoint for managing taxonomy terms"""
    queryset = Term.objects.select_related('taxonomy', 'parent')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        from ..serializers import TermSerializer, TermCreateSerializer
        if self.action == 'create':
            return TermCreateSerializer
        return TermSerializer
    
    def perform_create(self, serializer):
        """Create term with taxonomy validation"""
        taxonomy = serializer.validated_data.get('taxonomy')
        if taxonomy.store != self.request.store:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Taxonomy does not belong to this store")
        serializer.save()
        log_event_async.delay({
            'event_type': 'TAXONOMY_CREATED',
            'message': f"Taxonomy created: {serializer.instance.name}",
            'store': self.request.store,
            'user': self.request.user,
            'entity_type': 'Taxonomy',
            'entity_id': serializer.instance.id
        })
        return serializer

    def perform_update(self, serializer):
        serializer.save()
        log_event_async.delay({
            'event_type': 'TAXONOMY_UPDATED',
            'message': f"Taxonomy updated: {serializer.instance.name}",
            'store': self.request.store,
            'user': self.request.user,
            'entity_type': 'Taxonomy',
            'entity_id': serializer.instance.id
        })

    def perform_destroy(self, instance):
        tax_id = instance.id
        name = instance.name
        instance.delete()
        log_event_async.delay({
            'event_type': 'TAXONOMY_DELETED',
            'message': f"Taxonomy deleted: {name}",
            'store': self.request.store,
            'user': self.request.user,
            'entity_type': 'Taxonomy',
            'entity_id': tax_id
        })
