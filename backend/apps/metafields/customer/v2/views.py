"""
Architectural + real implementation for customer metafields interface.

Authenticated users manage their own metafields for content.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.contrib.contenttypes.models import ContentType

from core.permissions import IsStoreUser
from apps.metafields.models import MetafieldDefinition, Metafield
from apps.metafields.services import MetafieldService
from .serializers import MetafieldCustomerSerializer


class MetafieldCustomerViewSet(viewsets.ModelViewSet):
    """
    Architectural + real implementation for customer metafields interface.
    
    Authenticated users can manage metafields for their own content.
    Full CRUD operations with store ownership validation.
    """
    permission_classes = [IsAuthenticated, IsStoreUser]
    throttle_classes = [UserRateThrottle]
    serializer_class = MetafieldCustomerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['value_text', 'value_number', 'value_boolean']
    ordering_fields = ['created_at', 'updated_at']
    
    def get_queryset(self):
        """Filter by current user's store"""
        return Metafield.objects.filter(
            store__in=self.request.user.stores_owned.all()
        ).select_related('definition', 'content_type')
    
    @extend_schema(
        summary="List metafields",
        description="List metafields for user's content"
    )
    def list(self, request, *args, **kwargs):
        """List metafields"""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create metafield",
        description="Create new metafield for content"
    )
    def create(self, request, *args, **kwargs):
        """Create metafield"""
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get metafield",
        description="Get metafield details"
    )
    def retrieve(self, request, *args, **kwargs):
        """Get metafield"""
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update metafield",
        description="Update metafield"
    )
    def update(self, request, *args, **kwargs):
        """Update metafield"""
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partial update metafield",
        description="Partial update metafield"
    )
    def partial_update(self, request, *args, **kwargs):
        """Partial update metafield"""
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete metafield",
        description="Delete metafield"
    )
    def destroy(self, request, *args, **kwargs):
        """Delete metafield"""
        return super().destroy(request, *args, **kwargs)
    
    @extend_schema(
        summary="Bulk create metafields",
        description="Create multiple metafields"
    )
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create metafields"""
        metafields_data = request.data.get('metafields', [])
        if not metafields_data:
            return Response(
                {'error': 'metafields array is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_metafields = []
        for metafield_data in metafields_data:
            # Validate store ownership
            content_type_id = metafield_data.get('content_type_id')
            object_id = metafield_data.get('object_id')
            
            if not content_type_id or not object_id:
                continue
            
            # Validate user owns the content
            if not MetafieldService.user_owns_content(
                self.request.user, content_type_id, object_id
            ):
                continue
            
            metafield = MetafieldService.create_metafield(
                user=self.request.user,
                definition_id=metafield_data.get('definition_id'),
                content_type_id=content_type_id,
                object_id=object_id,
                value=metafield_data.get('value')
            )
            created_metafields.append(metafield)
        
        serializer = self.get_serializer(created_metafields, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Bulk update metafields",
        description="Update multiple metafields"
    )
    @action(detail=False, methods=['put'])
    def bulk_update(self, request):
        """Bulk update metafields"""
        metafields_data = request.data.get('metafields', [])
        if not metafields_data:
            return Response(
                {'error': 'metafields array is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_metafields = []
        for metafield_data in metafields_data:
            metafield_id = metafield_data.get('id')
            if not metafield_id:
                continue
            
            try:
                metafield = Metafield.objects.get(
                    id=metafield_id,
                    store__in=self.request.user.stores_owned.all()
                )
            except Metafield.DoesNotExist:
                continue
            
            # Validate user owns the content
            if not MetafieldService.user_owns_content(
                self.request.user, metafield.content_type_id, metafield.object_id
            ):
                continue
            
            updated_metafield = MetafieldService.update_metafield(
                metafield=metafield,
                value=metafield_data.get('value')
            )
            updated_metafields.append(updated_metafield)
        
        serializer = self.get_serializer(updated_metafields, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Bulk delete metafields",
        description="Delete multiple metafields"
    )
    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        """Bulk delete metafields"""
        metafield_ids = request.data.get('metafield_ids', [])
        if not metafield_ids:
            return Response(
                {'error': 'metafield_ids array is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count = 0
        for metafield_id in metafield_ids:
            try:
                metafield = Metafield.objects.get(
                    id=metafield_id,
                    store__in=self.request.user.stores_owned.all()
                )
                # Validate user owns the content
                if MetafieldService.user_owns_content(
                    self.request.user, metafield.content_type_id, metafield.object_id
                ):
                    metafield.delete()
                    deleted_count += 1
            except Metafield.DoesNotExist:
                continue
        
        return Response({
            'message': f'Deleted {deleted_count} metafields successfully'
        })
    
    @extend_schema(
        summary="Get metafield by content",
        description="Get metafields for specific content"
    )
    @action(detail=False, methods=['get'])
    def by_content(self, request):
        """Get metafields by content"""
        content_type_id = request.query_params.get('content_type_id')
        object_id = request.query_params.get('object_id')
        
        if not content_type_id or not object_id:
            return Response(
                {'error': 'content_type_id and object_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate user owns the content
        if not MetafieldService.user_owns_content(
            self.request.user, content_type_id, object_id
        ):
            return Response(
                {'error': 'Content not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        metafields = Metafield.objects.filter(
            content_type_id=content_type_id,
            object_id=object_id,
            store__in=self.request.user.stores_owned.all()
        ).select_related('definition')
        
        serializer = self.get_serializer(metafields, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get metafield definitions",
        description="Get available metafield definitions"
    )
    @action(detail=False, methods=['get'])
    def definitions(self, request):
        """Get metafield definitions"""
        definitions = MetafieldDefinition.objects.filter(
            store__in=self.request.user.stores_owned.all()
        ).filter(is_visible=True)
        
        return Response([
            {
                'id': definition.id,
                'name': definition.name,
                'namespace': definition.namespace,
                'key': definition.key,
                'type': definition.type,
                'is_required': definition.is_required,
                'options': definition.options,
                'validations': definition.validations
            }
            for definition in definitions
        ])
    
    @extend_schema(
        summary="Validate metafield",
        description="Validate metafield value against definition"
    )
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """Validate metafield value"""
        definition_id = request.data.get('definition_id')
        value = request.data.get('value')
        
        if not definition_id or value is None:
            return Response(
                {'error': 'definition_id and value are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            definition = MetafieldDefinition.objects.get(
                id=definition_id,
                store__in=self.request.user.stores_owned.all()
            )
        except MetafieldDefinition.DoesNotExist:
            return Response(
                {'error': 'Definition not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        validation_result = MetafieldService.validate_value(
            definition=definition,
            value=value
        )
        
        return Response({
            'is_valid': validation_result['is_valid'],
            'errors': validation_result.get('errors', [])
        })
