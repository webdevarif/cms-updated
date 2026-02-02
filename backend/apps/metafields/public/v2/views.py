"""
Architectural + real implementation for public metafields interface.

Read-only access to metafields for content consumption.
"""

from apps.metafields.models import Metafield, MetafieldDefinition
from django.contrib.contenttypes.models import ContentType
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .serializers import MetafieldPublicSerializer


class MetafieldPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Architectural + real implementation for public metafields interface.

    Provides read-only access to published metafields for content consumption.
    Public users can view metafields for published content only.
    """

    permission_classes = [AllowAny]  # Public access
    throttle_classes = [AnonRateThrottle]
    serializer_class = MetafieldPublicSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["definition__namespace", "definition__type"]

    def get_queryset(self):
        """Filter by published metafields only"""
        return Metafield.objects.filter(
            definition__is_visible=True, definition__is_filterable=True
        ).select_related("definition", "content_type")

    @extend_schema(summary="List metafields", description="List published metafields")
    def list(self, request, *args, **kwargs):
        """List metafields"""
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Get metafield", description="Get metafield details")
    def retrieve(self, request, *args, **kwargs):
        """Get metafield"""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Get metafield value", description="Get metafield value")
    @action(detail=True, methods=["get"])
    def value(self, request, pk=None):
        """Get metafield value"""
        metafield = self.get_object()
        value = MetafieldService.get_metafield_value(metafield)
        return Response({"value": value})

    @extend_schema(summary="Get metafield definition", description="Get metafield definition")
    @action(detail=True, methods=["get"])
    def definition(self, request, pk=None):
        """Get metafield definition"""
        metafield = self.get_object()
        definition = metafield.definition

        return Response(
            {
                "id": definition.id,
                "name": definition.name,
                "namespace": definition.namespace,
                "key": definition.key,
                "type": definition.type,
                "is_required": definition.is_required,
                "is_visible": definition.is_visible,
                "is_filterable": definition.is_filterable,
                "options": definition.options,
                "validations": definition.validations,
            }
        )

    @extend_schema(
        summary="Get metafields by content",
        description="Get metafields for specific content",
    )
    @action(detail=False, methods=["get"])
    def by_content(self, request):
        """Get metafields by content"""
        content_type_id = request.query_params.get("content_type_id")
        object_id = request.query_params.get("object_id")

        if not content_type_id or not object_id:
            return Response(
                {"error": "content_type_id and object_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        metafields = Metafield.objects.filter(
            content_type_id=content_type_id,
            object_id=object_id,
            definition__is_visible=True,
            definition__is_filterable=True,
        ).select_related("definition", "content_type")

        serializer = self.get_serializer(metafields, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get metafield definitions",
        description="Get available metafield definitions",
    )
    @action(detail=False, methods=["get"])
    def definitions(self, request):
        """Get metafield definitions"""
        definitions = MetafieldDefinition.objects.filter(
            is_visible=True, is_filterable=True
        ).order_by("namespace", "key")

        return Response(
            [
                {
                    "id": definition.id,
                    "name": definition.name,
                    "namespace": definition.namespace,
                    "key": definition.key,
                    "type": definition.type,
                    "is_required": definition.is_required,
                    "is_visible": definition.is_visible,
                    "is_filterable": definition.is_filterable,
                    "options": definition.options,
                    "validations": definition.validations,
                }
                for definition in definitions
            ]
        )

    @extend_schema(
        summary="Get metafield definitions by namespace",
        description="Get metafield definitions grouped by namespace",
    )
    @action(detail=False, methods=["get"])
    def definitions_by_namespace(self, request):
        """Get metafield definitions by namespace"""
        namespace = request.query_params.get("namespace")

        if not namespace:
            return Response(
                {"error": "namespace parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        definitions = MetafieldDefinition.objects.filter(
            namespace=namespace, is_visible=True, is_filterable=True
        ).order_by("key")

        return Response(
            [
                {
                    "id": definition.id,
                    "name": definition.name,
                    "key": definition.key,
                    "type": definition.type,
                    "is_required": definition.is_required,
                    "is_visible": definition.is_visible,
                    "is_filterable": definition.is_filterable,
                    "options": definition.options,
                    "validations": definition.validations,
                }
                for definition in definitions
            ]
        )

    @extend_schema(summary="Search metafields", description="Search metafields by value")
    @action(detail=False, methods=["get"])
    def search(self, request):
        """Search metafields by value"""
        query = request.query_params.get("q", "")
        if not query:
            return Response(
                {"error": "q parameter is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        metafields = (
            Metafield.objects.filter(definition__is_visible=True, definition__is_filterable=True)
            .filter(value_text__icontains=query)
            .select_related("definition", "content_type")
        )

        serializer = self.get_serializer(metafields, many=True)
        return Response(serializer.data)
