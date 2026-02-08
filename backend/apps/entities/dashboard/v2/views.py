"""
Dashboard entities views - admin interface for entity management.
"""

from apps.entities.models import EntityAction, EntityInteraction
from core.permissions import IsStoreOwner
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Count, Q, Sum

from .serializers import (
    DashboardEntityActionCreateSerializer,
    DashboardEntityActionSerializer,
    DashboardEntityAnalyticsSerializer,
    DashboardEntityInteractionSerializer,
)


class DashboardEntityActionViewSet(viewsets.ModelViewSet):
    """
    Dashboard entity actions API - admin access to entity actions.

    Provides:
    - Full CRUD on entity actions
    - Entity action analytics
    - Bulk operations
    - Interaction management
    """

    permission_classes = [permissions.IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "description", "slug"]
    ordering_fields = ["name", "created_at", "action_type"]
    ordering = ["name"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return DashboardEntityActionCreateSerializer
        return DashboardEntityActionSerializer

    def get_queryset(self):
        """Filter by store."""
        queryset = EntityAction.objects.select_related("store")
        store = getattr(self.request, "store", None)
        if store:
            queryset = queryset.filter(store=store)
        return queryset

    def perform_create(self, serializer):
        """Create entity action with store."""
        store = getattr(self.request, "store", None)
        if store:
            serializer.save(store=store)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """
        Activate an entity action.

        Returns:
            Updated entity action
        """
        entity_action = self.get_object()
        entity_action.is_active = True
        entity_action.save()

        return Response(
            DashboardEntityActionSerializer(entity_action).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """
        Deactivate an entity action.

        Returns:
            Updated entity action
        """
        entity_action = self.get_object()
        entity_action.is_active = False
        entity_action.save()

        return Response(
            DashboardEntityActionSerializer(entity_action).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"])
    def interactions(self, request, pk=None):
        """
        Get interactions for this entity action.

        Returns:
            List of interactions
        """
        entity_action = self.get_object()

        interactions = EntityInteraction.objects.filter(action=entity_action).select_related(
            "user", "content_type"
        )

        # Filter by user if specified
        user_id = request.query_params.get("user_id")
        if user_id:
            interactions = interactions.filter(user_id=user_id)

        # Filter by content type if specified
        content_type_id = request.query_params.get("content_type")
        if content_type_id:
            interactions = interactions.filter(content_type_id=content_type_id)

        serializer = DashboardEntityInteractionSerializer(interactions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        """
        Get statistics for this entity action.

        Returns:
            Statistics for the entity action
        """
        entity_action = self.get_object()

        # Use analytics service for statistics
        from ..services.entity_analytics_service import get_action_stats

        stats = get_action_stats(entity_action)
        return Response(stats)

    @action(detail=True, methods=["post"])
    def bulk_deactivate_interactions(self, request, pk=None):
        """
        Bulk deactivate interactions for this entity action.

        Args:
            user_ids: List of user IDs (optional)
            content_type_id: Content type ID (optional)
            object_id: Object ID (optional)

        Returns:
            Number of deactivated interactions
        """
        entity_action = self.get_object()

        interactions = EntityInteraction.objects.filter(action=entity_action)

        user_ids = request.data.get("user_ids")
        if user_ids:
            interactions = interactions.filter(user_id__in=user_ids)

        content_type_id = request.data.get("content_type_id")
        if content_type_id:
            interactions = interactions.filter(content_type_id=content_type_id)

        object_id = request.data.get("object_id")
        if object_id:
            interactions = interactions.filter(object_id=object_id)

        deactivated_count = interactions.update(is_active=False)

        return Response(
            {
                "message": f"Deactivated {deactivated_count} interactions",
                "count": deactivated_count,
            }
        )


class DashboardEntityInteractionViewSet(viewsets.ModelViewSet):
    """
    Dashboard entity interactions API - admin access to all interactions.

    Provides:
    - Full CRUD on entity interactions
    - Bulk operations
    - Analytics
    - User management
    """

    permission_classes = [permissions.IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["user__username", "action__name", "content_type__model"]
    ordering_fields = ["created_at", "rating", "action__name"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Return appropriate serializer."""
        return DashboardEntityInteractionSerializer

    def get_queryset(self):
        """Filter by store."""
        queryset = EntityInteraction.objects.select_related("action", "user", "content_type")
        store = getattr(self.request, "store", None)
        if store:
            queryset = queryset.filter(store=store)
        return queryset

    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """
        Get entity interaction analytics for the store.

        Returns:
            Entity interaction analytics data
        """
        try:
            store = getattr(request, "store", None)
            if not store:
                return Response(
                    {"error": "Store not specified"}, status=status.HTTP_400_BAD_REQUEST
                )

            queryset = self.get_queryset()

            analytics = {
                "total_interactions": queryset.count(),
                "active_interactions": queryset.filter(is_active=True).count(),
                "unique_users": queryset.values("user").distinct().count(),
                "actions_summary": list(
                    queryset.values("action__name", "action__slug", "action__action_type")
                    .annotate(count=Count("id"), avg_rating=Avg("rating"))
                    .order_by("-count")
                ),
                "content_types_summary": list(
                    queryset.values("content_type__model")
                    .annotate(count=Count("id"))
                    .order_by("-count")
                ),
                "monthly_trends": list(
                    queryset.extra(select={"month": 'strftime("%%Y-%%m", created_at)'})
                    .values("month")
                    .annotate(count=Count("id"))
                    .order_by("month")
                ),
                "top_users": list(
                    queryset.values("user__username")
                    .annotate(interaction_count=Count("id"))
                    .order_by("-interaction_count")[:10]
                ),
            }

            return Response(analytics)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["post"])
    def bulk_activate(self, request):
        """
        Bulk activate interactions.

        Args:
            interaction_ids: List of interaction IDs

        Returns:
            Number of activated interactions
        """
        interaction_ids = request.data.get("interaction_ids", [])

        if not interaction_ids:
            return Response(
                {"error": "interaction_ids are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(id__in=interaction_ids)
        activated_count = queryset.update(is_active=True)

        return Response(
            {
                "message": f"Activated {activated_count} interactions",
                "count": activated_count,
            }
        )

    @action(detail=False, methods=["post"])
    def bulk_deactivate(self, request):
        """
        Bulk deactivate interactions.

        Args:
            interaction_ids: List of interaction IDs

        Returns:
            Number of deactivated interactions
        """
        interaction_ids = request.data.get("interaction_ids", [])

        if not interaction_ids:
            return Response(
                {"error": "interaction_ids are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(id__in=interaction_ids)
        deactivated_count = queryset.update(is_active=False)

        return Response(
            {
                "message": f"Deactivated {deactivated_count} interactions",
                "count": deactivated_count,
            }
        )

    @action(detail=False, methods=["post"])
    def bulk_delete(self, request):
        """
        Bulk delete interactions.

        Args:
            interaction_ids: List of interaction IDs

        Returns:
            Number of deleted interactions
        """
        interaction_ids = request.data.get("interaction_ids", [])

        if not interaction_ids:
            return Response(
                {"error": "interaction_ids are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(id__in=interaction_ids)
        deleted_count, _ = queryset.delete()

        return Response(
            {"message": f"Deleted {deleted_count} interactions", "count": deleted_count}
        )

    @action(detail=False, methods=["get"])
    def by_user(self, request):
        """
        Get interactions by user.

        Args:
            user_id: User ID

        Returns:
            User's interactions
        """
        user_id = request.query_params.get("user_id")

        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        interactions = self.get_queryset().filter(user_id=user_id)
        serializer = self.get_serializer(interactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_content(self, request):
        """
        Get interactions by content.

        Args:
            content_type_id: Content type ID
            object_id: Object ID

        Returns:
            Content's interactions
        """
        content_type_id = request.query_params.get("content_type_id")
        object_id = request.query_params.get("object_id")

        if not content_type_id or not object_id:
            return Response(
                {"error": "content_type_id and object_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        interactions = self.get_queryset().filter(
            content_type_id=content_type_id, object_id=object_id
        )
        serializer = self.get_serializer(interactions, many=True)
        return Response(serializer.data)
