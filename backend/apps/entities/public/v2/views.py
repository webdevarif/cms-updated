"""
Public entities views - read-only interface for entity interactions.
"""
from apps.entities.models import EntityAction, EntityInteraction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .serializers import PublicEntityActionSerializer, PublicEntityInteractionSerializer


class PublicEntityActionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public entity actions API - read-only access to entity actions.

    Provides:
    - List available entity actions
    - Get entity action details
    - View public entity interactions
    """

    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_serializer_class(self):
        """Return appropriate serializer."""
        return PublicEntityActionSerializer

    def get_queryset(self):
        """Filter to active and public actions only."""
        queryset = EntityAction.objects.filter(is_active=True, is_public=True).select_related(
            "store"
        )

        store = getattr(self.request, "store", None)
        if store:
            queryset = queryset.filter(store=store)

        return queryset

    @action(detail=True, methods=["get"])
    def interactions(self, request, pk=None):
        """
        Get public interactions for this entity action.

        Returns:
            List of public interactions
        """
        entity_action = self.get_object()

        # Only show interactions from actions that allow anonymous or are public
        if not entity_action.allow_anonymous and not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required to view interactions"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        interactions = EntityInteraction.objects.filter(
            action=entity_action, is_active=True
        ).select_related("user", "content_type")

        # Filter by user if not anonymous
        if not entity_action.allow_anonymous and request.user.is_authenticated:
            interactions = interactions.filter(user=request.user)

        serializer = PublicEntityInteractionSerializer(interactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """
        Get public statistics for entity actions.

        Returns:
            Statistics for public entity actions
        """
        queryset = self.get_queryset()

        stats = {}
        for action in queryset:
            interaction_count = EntityInteraction.objects.filter(
                action=action, is_active=True
            ).count()

            stats[action.slug] = {
                "name": action.name,
                "action_type": action.action_type,
                "interaction_count": interaction_count,
                "icon": action.icon,
                "color": action.color,
            }

        return Response(stats)


class PublicEntityInteractionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public entity interactions API - read-only access to entity interactions.

    Provides:
    - View public entity interactions
    - Get interaction statistics
    """

    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["action__name", "user__username"]
    ordering_fields = ["created_at", "rating"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Return appropriate serializer."""
        return PublicEntityInteractionSerializer

    def get_queryset(self):
        """Filter to public interactions only."""
        queryset = EntityInteraction.objects.filter(
            is_active=True, action__is_public=True, action__is_active=True
        ).select_related("action", "user", "content_type")

        store = getattr(self.request, "store", None)
        if store:
            queryset = queryset.filter(store=store)

        # Filter by user if action doesn't allow anonymous
        if not request.user.is_authenticated:
            queryset = queryset.filter(action__allow_anonymous=True)

        return queryset

    @action(detail=False, methods=["get"])
    def by_content(self, request):
        """
        Get interactions by content type and object ID.

        Args:
            content_type: Content type ID
            object_id: Object ID

        Returns:
            Interactions for the specified content
        """
        content_type_id = request.query_params.get("content_type")
        object_id = request.query_params.get("object_id")

        if not content_type_id or not object_id:
            return Response(
                {"error": "content_type and object_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        interactions = self.get_queryset().filter(
            content_type_id=content_type_id, object_id=object_id
        )

        serializer = self.get_serializer(interactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """
        Get interaction summary by content.

        Returns:
            Summary of interactions grouped by content
        """
        queryset = self.get_queryset()

        summary = {}
        for interaction in queryset:
            content_key = f"{interaction.content_type.model}_{interaction.object_id}"

            if content_key not in summary:
                summary[content_key] = {
                    "content_type": interaction.content_type.model,
                    "object_id": interaction.object_id,
                    "actions": {},
                }

            action_slug = interaction.action.slug
            if action_slug not in summary[content_key]["actions"]:
                summary[content_key]["actions"][action_slug] = {
                    "name": interaction.action.name,
                    "action_type": interaction.action.action_type,
                    "count": 0,
                    "total_rating": 0,
                    "average_rating": 0,
                }

            summary[content_key]["actions"][action_slug]["count"] += 1

            if interaction.rating:
                summary[content_key]["actions"][action_slug]["total_rating"] += interaction.rating
                summary[content_key]["actions"][action_slug]["average_rating"] = (
                    summary[content_key]["actions"][action_slug]["total_rating"]
                    / summary[content_key]["actions"][action_slug]["count"]
                )

        return Response(summary)
