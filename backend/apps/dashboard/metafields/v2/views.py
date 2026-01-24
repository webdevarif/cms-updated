from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter

from core.permissions import IsStoreOwner
from apps.public.metafields.models import MetafieldDefinition, Metafield
from apps.public.metafields.services import MetafieldService
from . import serializers


class MetafieldDefinitionViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for metafield definitions
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = serializers.MetafieldDefinitionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['namespace', 'type', 'is_required', 'is_visible']
    search_fields = ['name', 'namespace', 'key']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        return MetafieldDefinition.objects.filter(store=self.request.store)
    
    def perform_create(self, serializer):
        instance = serializer.save(store=self.request.store)
        MetafieldService.invalidate_definition_cache(instance.store)
    
    def perform_update(self, serializer):
        instance = serializer.save()
        MetafieldService.invalidate_definition_cache(instance.store)
    
    def perform_destroy(self, instance):
        store = instance.store
        instance.delete()
        MetafieldService.invalidate_definition_cache(store)
    
    @extend_schema(
        summary="List Metafield Definitions",
        description="Get paginated list of metafield definitions",
        responses={200: serializers.MetafieldDefinitionSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Metafield Definition",
        request=serializers.MetafieldDefinitionSerializer,
        responses={201: serializers.MetafieldDefinitionSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Metafield Definition",
        request=serializers.MetafieldDefinitionSerializer,
        responses={200: serializers.MetafieldDefinitionSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class MetafieldViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for metafield values
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = serializers.MetafieldSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['definition__namespace', 'definition__type']
    search_fields = ['definition__name', 'definition__namespace', 'definition__key']
    ordering_fields = ['updated_at', 'created_at']
    
    def get_queryset(self):
        return Metafield.objects.filter(store=self.request.store)
    
    @extend_schema(
        summary="Get Metafields for Object",
        description="Get all metafields for a specific object",
        parameters=[
            OpenApiParameter(
                name='content_type',
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Content type model name (e.g., 'product')"
            ),
            OpenApiParameter(
                name='object_id',
                type=int,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Object ID"
            )
        ],
        responses={200: serializers.MetafieldSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def for_object(self, request):
        """Get all metafields for a specific object"""
        from django.contrib.contenttypes.models import ContentType
        
        content_type = request.query_params.get('content_type')
        object_id = request.query_params.get('object_id')
        
        if not content_type or not object_id:
            return Response(
                {"error": "content_type and object_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            content_type = ContentType.objects.get(model=content_type)
        except ContentType.DoesNotExist:
            return Response(
                {"error": f"Invalid content_type: {content_type}"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        metafields = Metafield.objects.filter(
            store=request.store,
            content_type=content_type,
            object_id=object_id
        ).select_related('definition')
        
        serializer = self.get_serializer(metafields, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Bulk Update Metafields",
        description="Update multiple metafields for an object",
        request=serializers.BulkMetafieldUpdateSerializer,
        responses={200: serializers.MetafieldSerializer(many=True)}
    )
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update metafields for an object"""
        from django.contrib.contenttypes.models import ContentType
        from django.apps import apps
        
        serializer = serializers.BulkMetafieldUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        content_type = serializer.validated_data['content_type']
        object_id = serializer.validated_data['object_id']
        metafields = serializer.validated_data['metafields']
        
        try:
            # Verify the object exists and belongs to the store
            model_class = ContentType.objects.get(model=content_type).model_class()
            obj = model_class.objects.filter(store=request.store, id=object_id).first()
            
            if not obj:
                return Response(
                    {"error": f"Object not found or access denied"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Update metafields
            updated = MetafieldService.bulk_update_metafields(
                obj, 
                metafields,
                create_definitions=True
            )
            
            # Return updated metafields
            serializer = self.get_serializer(updated, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
