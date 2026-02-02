"""
Architectural + real implementation for dashboard metafields interface.

Full admin CRUD on all metafields + bulk operations.
"""

from apps.metafields.models import Metafield, MetafieldDefinition
from apps.metafields.services import MetafieldService
from core.permissions import IsStoreOwner
from django.contrib.contenttypes.models import ContentType
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from .serializers import (
    BulkMetafieldUpdateSerializer,
    MetafieldDashboardSerializer,
    MetafieldDefinitionDashboardSerializer,
)


class MetafieldDefinitionDashboardViewSet(viewsets.ModelViewSet):
    """
    Architectural + real implementation for dashboard metafield definitions interface.

    Full admin CRUD on metafield definitions.
    Store owners can manage all metafield definitions.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    throttle_classes = [UserRateThrottle]
    serializer_class = MetafieldDefinitionDashboardSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "namespace", "key"]
    ordering_fields = ["created_at", "name"]

    def get_queryset(self):
        """Filter by current user's stores"""
        return MetafieldDefinition.objects.filter(store__in=self.request.user.stores_owned.all())

    @extend_schema(
        summary="List metafield definitions",
        description="List all metafield definitions",
    )
    def list(self, request, *args, **kwargs):
        """List metafield definitions"""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create metafield definition",
        description="Create new metafield definition",
    )
    def create(self, request, *args, **kwargs):
        """Create metafield definition"""
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Get metafield definition",
        description="Get metafield definition details",
    )
    def retrieve(self, request, *args, **kwargs):
        """Get metafield definition"""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Update metafield definition", description="Update metafield definition")
    def update(self, request, *args, **kwargs):
        """Update metafield definition"""
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partial update metafield definition",
        description="Partial update metafield definition",
    )
    def partial_update(self, request, *args, **kwargs):
        """Partial update metafield definition"""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary="Delete metafield definition", description="Delete metafield definition")
    def destroy(self, request, *args, **kwargs):
        """Delete metafield definition"""
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary="Get metafield definitions by namespace",
        description="Get metafield definitions grouped by namespace",
    )
    @action(detail=False, methods=["get"])
    def by_namespace(self, request):
        """Get metafield definitions by namespace"""
        namespace = request.query_params.get("namespace")

        if not namespace:
            return Response(
                {"error": "namespace parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        definitions = self.get_queryset().filter(namespace=namespace)

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

    @extend_schema(
        summary="Validate metafield definition",
        description="Validate metafield definition structure",
    )
    @action(detail=True, methods=["post"])
    def validate(self, request, pk=None):
        """Validate metafield definition"""
        definition = self.get_object()

        validation_result = MetafieldService.validate_definition(definition)

        return Response(
            {
                "is_valid": validation_result["is_valid"],
                "errors": validation_result.get("errors", []),
            }
        )

    @extend_schema(
        summary="Export metafield definitions",
        description="Export metafield definitions as JSON",
    )
    @action(detail=False, methods=["get"])
    def export(self, request):
        """Export metafield definitions"""
        definitions = self.get_queryset()

        export_data = []
        for definition in definitions:
            export_data.append(
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

        return Response({"definitions": export_data})

    @extend_schema(
        summary="Import metafield definitions",
        description="Import metafield definitions from JSON",
    )
    @action(detail=False, methods=["post"])
    def import_definitions(self, request):
        """Import metafield definitions from JSON"""
        definitions_data = request.data.get("definitions", [])

        if not definitions_data:
            return Response(
                {"error": "definitions array is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        imported_count = 0
        for definition_data in definitions_data:
            try:
                definition = MetafieldService.import_definition(
                    user=self.request.user, definition_data=definition_data
                )
                imported_count += 1
            except Exception as e:
                continue

        return Response(
            {"message": f"Imported {imported_count} metafield definitions successfully"}
        )


class MetafieldDashboardViewSet(viewsets.ModelViewSet):
    """
    Architectural + real implementation for dashboard metafields interface.

    Full admin CRUD on all metafields + bulk operations.
    Store owners can manage all metafields in their stores.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    throttle_classes = [UserRateThrottle]
    serializer_class = MetafieldDashboardSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["value_text", "value_number", "value_boolean"]
    ordering_fields = ["created_at", "updated_at"]

    def get_queryset(self):
        """Filter by current user's stores"""
        return Metafield.objects.filter(
            store__in=self.request.user.stores_owned.all()
        ).select_related("definition", "content_type")

    @extend_schema(summary="List metafields", description="List all metafields in user's stores")
    def list(self, request, *args, **kwargs):
        """List metafields"""
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Create metafield", description="Create new metafield")
    def create(self, request, *args, **kwargs):
        """Create metafield"""
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Get metafield", description="Get metafield details")
    def retrieve(self, request, *args, **kwargs):
        """Get metafield"""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Update metafield", description="Update metafield")
    def update(self, request, *args, **kwargs):
        """Update metafield"""
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Partial update metafield", description="Partial update metafield")
    def partial_update(self, request, *args, **kwargs):
        """Partial update metafield"""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary="Delete metafield", description="Delete metafield")
    def destroy(self, request, *args, **kwargs):
        """Delete metafield"""
        return super().destroy(request, *args, **kwargs)

    @extend_schema(summary="Bulk create metafields", description="Create multiple metafields")
    @action(detail=False, methods=["post"])
    def bulk_create(self, request):
        """Bulk create metafields"""
        metafields_data = request.data.get("metafields", [])
        if not metafields_data:
            return Response(
                {"error": "metafields array is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_metafields = []
        for metafield_data in metafields_data:
            # Validate store ownership
            content_type_id = metafield_data.get("content_type_id")
            object_id = metafield_data.get("object_id")

            if not content_type_id or not object_id:
                continue

            # Validate user owns the content
            if not MetafieldService.user_owns_content(
                self.request.user, content_type_id, object_id
            ):
                continue

            metafield = MetafieldService.create_metafield(
                user=self.request.user,
                definition_id=metafield_data.get("definition_id"),
                content_type_id=content_type_id,
                object_id=object_id,
                value=metafield_data.get("value"),
            )
            created_metafields.append(metafield)

        serializer = self.get_serializer(created_metafields, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Bulk update metafields", description="Update multiple metafields")
    @action(detail=False, methods=["put"])
    def bulk_update(self, request):
        """Bulk update metafields"""
        metafields_data = request.data.get("metafields", [])
        if not metafields_data:
            return Response(
                {"error": "metafields array is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_metafields = []
        for metafield_data in metafields_data:
            metafield_id = metafield_data.get("id")
            if not metafield_id:
                continue

            try:
                metafield = Metafield.objects.get(
                    id=metafield_id, store__in=self.request.user.stores_owned.all()
                )
            except Metafield.DoesNotExist:
                continue

            # Validate user owns the content
            if not MetafieldService.user_owns_content(
                self.request.user, metafield.content_type_id, metafield.object_id
            ):
                continue

            updated_metafield = MetafieldService.update_metafield(
                metafield=metafield, value=metafield_data.get("value")
            )
            updated_metafields.append(updated_metafield)

        serializer = self.get_serializer(updated_metafields, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Bulk delete metafields", description="Delete multiple metafields")
    @action(detail=False, methods=["delete"])
    def bulk_delete(self, request):
        """Bulk delete metafields"""
        metafield_ids = request.data.get("metafield_ids", [])
        if not metafield_ids:
            return Response(
                {"error": "metafield_ids array is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        deleted_count = 0
        for metafield_id in metafield_ids:
            try:
                metafield = Metafield.objects.get(
                    id=metafield_id, store__in=self.request.user.stores_owned.all()
                )
                # Validate user owns the content
                if MetafieldService.user_owns_content(
                    self.request.user, metafield.content_type_id, metafield.object_id
                ):
                    metafield.delete()
                    deleted_count += 1
            except Metafield.DoesNotExist:
                continue

        return Response({"message": f"Deleted {deleted_count} metafields successfully"})

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

        # Validate user owns the content
        if not MetafieldService.user_owns_content(self.request.user, content_type_id, object_id):
            return Response(
                {"error": "Content not found or access denied"},
                status=status.HTTP_404_NOT_FOUND,
            )

        metafields = Metafield.objects.filter(
            content_type_id=content_type_id,
            object_id=object_id,
            store__in=self.request.user.stores_owned.all(),
        ).select_related("definition")

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
            store__in=self.request.user.stores_owned.all()
        ).filter(is_visible=True)

        return Response(
            [
                {
                    "id": definition.id,
                    "name": definition.name,
                    "namespace": definition.namespace,
                    "key": definition.key,
                    "type": definition.type,
                    "is_required": definition.is_required,
                    "options": definition.options,
                    "validations": definition.validations,
                }
                for definition in definitions
            ]
        )

    @extend_schema(
        summary="Validate metafield",
        description="Validate metafield value against definition",
    )
    @action(detail=False, methods=["post"])
    def validate(self, request):
        """Validate metafield value"""
        definition_id = request.data.get("definition_id")
        value = request.data.get("value")

        if not definition_id or value is None:
            return Response(
                {"error": "definition_id and value are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            definition = MetafieldDefinition.objects.get(
                id=definition_id, store__in=self.request.user.stores_owned.all()
            )
        except MetafieldDefinition.DoesNotExist:
            return Response(
                {"error": "Definition not found or access denied"},
                status=status.HTTP_404_NOT_FOUND,
            )

        validation_result = MetafieldService.validate_value(definition=definition, value=value)

        return Response(
            {
                "is_valid": validation_result["is_valid"],
                "errors": validation_result.get("errors", []),
            }
        )

    @extend_schema(summary="Get metafield analytics", description="Get metafield analytics data")
    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get metafield analytics"""
        analytics = MetafieldService.get_metafield_analytics(
            stores=self.request.user.stores_owned.all()
        )
        return Response(analytics)

    @extend_schema(summary="Export metafields", description="Export metafields as JSON")
    @action(detail=False, methods=["get"])
    def export(self, request):
        """Export metafields as JSON"""
        metafields = self.get_queryset()

        export_data = []
        for metafield in metafields:
            export_data.append(
                {
                    "id": metafield.id,
                    "definition": {
                        "id": metafield.definition.id,
                        "name": metafield.definition.name,
                        "namespace": metafield.definition.namespace,
                        "key": metafield.definition.key,
                        "type": metafield.definition.type,
                    },
                    "content_type": {
                        "id": metafield.content_type.id,
                        "model": metafield.content_type.model,
                    },
                    "object_id": metafield.object_id,
                    "value": MetafieldService.get_metafield_value(metafield),
                }
            )

        return Response({"metafields": export_data})

    @extend_schema(summary="Import metafields", description="Import metafields from JSON")
    @action(detail=False, methods=["post"])
    def import_metafields(self, request):
        """Import metafields from JSON"""
        metafields_data = request.data.get("metafields", [])

        if not metafields_data:
            return Response(
                {"error": "metafields array is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        imported_count = 0
        for metafield_data in metafields_data:
            try:
                metafield = MetafieldService.import_metafield(
                    user=self.request.user, metafield_data=metafield_data
                )
                imported_count += 1
            except Exception as e:
                continue

        return Response({"message": f"Imported {imported_count} metafields successfully"})

    @extend_schema(
        summary="Bulk attach metafields",
        description="Attach metafields to multiple objects",
    )
    @action(detail=False, methods=["post"])
    def bulk_attach(self, request):
        """Bulk attach metafields to objects"""
        bulk_data = request.data.get("bulk_data", [])
        if not bulk_data:
            return Response(
                {"error": "bulk_data array is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        attached_count = 0
        for item in bulk_data:
            content_type_id = item.get("content_type_id")
            object_id = item.get("object_id")
            metafields = item.get("metafields", {})

            if not content_type_id or not object_id or not metafields:
                continue

            # Validate user owns the content
            if not MetafieldService.user_owns_content(
                self.request.user, content_type_id, object_id
            ):
                continue

            for namespace_key, value in metafields.items():
                try:
                    definition = MetafieldDefinition.objects.get(
                        namespace=namespace_key,
                        key=namespace_key.split(".")[0],
                        store__in=self.request.user.stores_owned.all(),
                    )

                    metafield = MetafieldService.create_metafield(
                        user=self.request.user,
                        definition_id=definition.id,
                        content_type_id=content_type_id,
                        object_id=object_id,
                        value=value,
                    )
                    attached_count += 1
                except Exception as e:
                    continue

        return Response({"message": f"Attached {attached_count} metafields successfully"})

    @extend_schema(
        summary="Bulk detach metafields",
        description="Detach metafields from multiple objects",
    )
    @action(detail=False, methods=["post"])
    def bulk_detach(self, request):
        """Bulk detach metafields from objects"""
        bulk_data = request.data.get("bulk_data", [])
        if not bulk_data:
            return Response(
                {"error": "bulk_data array is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        detached_count = 0
        for item in bulk_data:
            content_type_id = item.get("content_type_id")
            object_id = item.get("object_id")
            metafields = item.get("metafields", [])

            if not content_type_id or not object_id or not metafields:
                continue

            # Validate user owns the content
            if not MetafieldService.user_owns_content(
                self.request.user, content_type_id, object_id
            ):
                continue

            for namespace_key in metafields.keys():
                try:
                    definition = MetafieldDefinition.objects.get(
                        namespace=namespace_key,
                        key=namespace_key.split(".")[0],
                        store__in=self.request.user.stores_owned.all(),
                    )

                    metafield = Metafield.objects.get(
                        definition=definition,
                        content_type_id=content_type_id,
                        object_id=object_id,
                    )
                    if metafield:
                        metafield.delete()
                        detached_count += 1
                except Exception as e:
                    continue

        return Response({"message": f"Detached {detached_count} metafields successfully"})

    @action(detail=False, methods=["post"])
    def bulk_action(self, request):
        """Perform bulk actions on metafields (publish, unpublish, delete)"""
        from django.db import transaction

        from .serializers import BulkActionSerializer

        serializer = BulkActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        action_type = serializer.validated_data["action"]
        metafield_ids = serializer.validated_data["ids"]
        extra_data = serializer.validated_data.get("data", {})

        # Filter metafields by store and IDs
        queryset = self.get_queryset().filter(id__in=metafield_ids)
        total_requested = len(metafield_ids)
        total_found = queryset.count()

        try:
            with transaction.atomic():
                if action_type == "publish":
                    # For metafields, publish means making them visible
                    updated = queryset.update(is_visible=True)
                    message = f"Successfully published {updated} metafields"

                elif action_type == "unpublish":
                    # For metafields, unpublish means hiding them
                    updated = queryset.update(is_visible=False)
                    message = f"Successfully unpublished {updated} metafields"

                elif action_type == "delete":
                    deleted = queryset.delete()[0]  # delete() returns (count, details)
                    message = f"Successfully deleted {deleted} metafields"

                else:
                    return Response(
                        {"error": f"Unsupported action: {action_type}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Log the bulk operation
                from apps.analytics.services.event_service import EventService

                EventService.log_event(
                    event_type="METAFIELD_BULK_UPDATE",
                    event_name=f"Bulk {action_type} operation on metafields",
                    properties={
                        "user": request.user.id if request.user else None,
                        "store": request.store.id,
                        "action_type": action_type,
                        "count": len(metafield_ids),
                        "metafield_ids": metafield_ids,
                    },
                    user=request.user,
                    store=request.store,
                )

                response_data = {
                    "message": message,
                    "action": action_type,
                    "requested": total_requested,
                    "found": total_found,
                    "affected": (
                        updated
                        if "updated" in locals()
                        else deleted
                        if "deleted" in locals()
                        else 0
                    ),
                }
                return Response(response_data)

        except Exception as e:
            return Response(
                {"error": f"Bulk operation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get metafields analytics and statistics for the store with time-range filtering"""
        user = request.user
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Parse time range parameters
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        from datetime import datetime

        date_filter = {}
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                date_filter["created_at__gte"] = start_dt
            except ValueError:
                return Response(
                    {"error": "Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                date_filter["created_at__lte"] = end_dt
            except ValueError:
                return Response(
                    {"error": "Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            # Base queryset with date filtering and store ownership
            base_queryset = Metafield.objects.filter(
                definition__store__in=user.stores_owned.all(), **date_filter
            )

            # Metafield counts by status and type
            total_metafields = base_queryset.count()
            visible_metafields = base_queryset.filter(is_visible=True).count()
            hidden_metafields = base_queryset.filter(is_visible=False).count()

            # Content type distribution
            from django.db.models import Count

            content_types = (
                base_queryset.values("content_type__model")
                .annotate(
                    count=Count("id"),
                    visible_count=Count("id", filter=Q(is_visible=True)),
                )
                .order_by("-count")
            )

            content_type_data = []
            for ct in content_types:
                content_type_data.append(
                    {
                        "model": ct["content_type__model"],
                        "total_metafields": ct["count"],
                        "visible_metafields": ct["visible_count"],
                        "visibility_rate": (
                            (ct["visible_count"] / ct["count"] * 100) if ct["count"] > 0 else 0
                        ),
                    }
                )

            # Metafield definition usage
            definition_usage = (
                base_queryset.values(
                    "definition__namespace", "definition__key", "definition__field_type"
                )
                .annotate(
                    total_usage=Count("id"),
                    visible_usage=Count("id", filter=Q(is_visible=True)),
                )
                .order_by("-total_usage")[:20]
            )

            definition_data = []
            for def_item in definition_usage:
                definition_data.append(
                    {
                        "namespace": def_item["definition__namespace"],
                        "key": def_item["definition__key"],
                        "field_type": def_item["definition__field_type"],
                        "total_usage": def_item["total_usage"],
                        "visible_usage": def_item["visible_usage"],
                    }
                )

            # Store performance (metafields per store)
            stores = (
                base_queryset.values("definition__store__name", "definition__store__id")
                .annotate(
                    total_metafields=Count("id"),
                    visible_metafields=Count("id", filter=Q(is_visible=True)),
                    definitions_used=Count("definition", distinct=True),
                )
                .order_by("-total_metafields")
            )

            store_data = []
            for store in stores:
                store_data.append(
                    {
                        "id": store["definition__store__id"],
                        "name": store["definition__store__name"],
                        "total_metafields": store["total_metafields"],
                        "visible_metafields": store["visible_metafields"],
                        "definitions_used": store["definitions_used"],
                    }
                )

            # Field type distribution
            field_types = (
                base_queryset.values("definition__field_type")
                .annotate(
                    count=Count("id"),
                    percentage=(
                        (Count("id") * 100.0 / total_metafields) if total_metafields > 0 else 0
                    ),
                )
                .order_by("-count")
            )

            field_type_data = [
                {
                    "field_type": ft["definition__field_type"],
                    "count": ft["count"],
                    "percentage": float(ft["percentage"]),
                }
                for ft in field_types
            ]

            # Metafield activity trends
            activity_trends = []
            if start_date and end_date:
                from django.db.models.functions import TruncDate

                daily_activity = (
                    base_queryset.annotate(date=TruncDate("created_at"))
                    .values("date")
                    .annotate(
                        created=Count("id"),
                        updated=Count("id", filter=Q(updated_at__date=F("created_at__date"))),
                    )
                    .order_by("date")
                )

                activity_trends = [
                    {
                        "date": str(item["date"]),
                        "metafields_created": item["created"],
                        "metafields_updated": item["updated"],
                    }
                    for item in daily_activity
                ]

            # Namespace analysis
            namespace_analysis = (
                base_queryset.values("definition__namespace")
                .annotate(
                    total_metafields=Count("id"),
                    unique_definitions=Count("definition", distinct=True),
                    avg_per_definition=Count("id") * 1.0 / Count("definition", distinct=True),
                )
                .order_by("-total_metafields")
            )

            namespace_data = [
                {
                    "namespace": ns["definition__namespace"],
                    "total_metafields": ns["total_metafields"],
                    "unique_definitions": ns["unique_definitions"],
                    "avg_per_definition": float(ns["avg_per_definition"]),
                }
                for ns in namespace_analysis
            ]

            analytics_data = {
                "overview": {
                    "total_metafields": total_metafields,
                    "visible_metafields": visible_metafields,
                    "hidden_metafields": hidden_metafields,
                    "visibility_rate": (
                        (visible_metafields / total_metafields * 100) if total_metafields > 0 else 0
                    ),
                    "total_content_types": len(content_type_data),
                    "total_stores": len(store_data),
                    "total_namespaces": len(namespace_data),
                },
                "content_types": content_type_data,
                "field_types": field_type_data,
                "definitions": definition_data,
                "stores": store_data,
                "namespaces": namespace_data,
                "trends": {"activity": activity_trends},
                "usage_metrics": {
                    "avg_metafields_per_content_type": (
                        total_metafields / len(content_type_data) if content_type_data else 0
                    ),
                    "most_used_definitions": (definition_data[:5] if definition_data else []),
                    "most_active_namespaces": (namespace_data[:5] if namespace_data else []),
                },
                "time_range": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "has_date_filter": bool(start_date or end_date),
                },
            }

            return Response(analytics_data)

        except Exception as e:
            return Response(
                {"error": f"Analytics failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
