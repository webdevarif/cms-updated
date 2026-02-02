"""
Dashboard notification views.
"""

from apps.notifications.models import Notification, NotificationPreference, NotificationTemplate
from apps.notifications.services import NotificationService
from core.permissions import IsStoreOwner
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    NotificationDashboardSerializer,
    NotificationPreferenceDashboardSerializer,
    NotificationTemplateDashboardSerializer,
)


class NotificationDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard notification management endpoints.

    Manages concrete notifications - actual delivered/queued notification items.
    Use cases: inspection of notification history, manual mark-as-read operations,
    and viewing delivery status for store notifications.

    Future improvement: This viewset should focus on listing, inspecting, and marking
    notifications as read. Template management and preferences should remain in their
    respective dedicated viewsets.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = NotificationDashboardSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "notification_type", "user"]

    def get_queryset(self):
        """Filter by store ownership"""
        return Notification.objects.filter(store__in=self.request.user.stores_owned.all()).order_by(
            "-created_at"
        )

    @extend_schema(
        summary="Mark as read",
        description="Mark notification as read",
        responses={200: NotificationDashboardSerializer},
    )
    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.mark_as_read()

        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Resend notification",
        description="Resend failed notification",
        responses={200: NotificationDashboardSerializer},
    )
    @action(detail=True, methods=["post"])
    def resend(self, request, pk=None):
        """Resend notification"""
        notification = self.get_object()
        NotificationService.send_notification(notification)

        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Bulk mark as read",
        description="Mark multiple notifications as read",
        responses={200: dict},
    )
    @action(detail=False, methods=["post"])
    def bulk_mark_read(self, request):
        """Bulk mark notifications as read"""
        notification_ids = request.data.get("notification_ids", [])
        if not notification_ids:
            return Response(
                {"error": "notification_ids required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        notifications = self.get_queryset().filter(id__in=notification_ids)
        count = 0
        for notification in notifications:
            notification.mark_as_read()
            count += 1

        return Response({"marked_read": count}, status=status.HTTP_200_OK)


class NotificationPreferenceDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard notification preference management endpoints.

    Manages per-user notification preferences including channel opt-in/out settings,
    digest frequency, and notification type preferences. Use cases: configuring how
    users receive notifications and managing delivery preferences per notification type.

    Future improvement: This viewset should remain focused solely on preference management
    and not mix with notification creation or template management.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = NotificationPreferenceDashboardSerializer

    def get_queryset(self):
        """Filter by store ownership"""
        return NotificationPreference.objects.filter(
            store__in=self.request.user.stores_owned.all()
        ).order_by("user", "notification_type")


class NotificationTemplateDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard notification template management endpoints.

    Manages reusable notification templates with channel-specific content and variable
    substitution. Use cases: creating and managing email/in-app/push templates for
    different notification events, customizing content per channel, and managing template
    variables and rendering logic.

    Future improvement: This viewset should focus solely on template CRUD operations
    and not mix with notification delivery or preference management.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = NotificationTemplateDashboardSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["notification_type", "is_active"]

    def get_queryset(self):
        """Filter by store ownership"""
        return NotificationTemplate.objects.filter(
            store__in=self.request.user.stores_owned.all()
        ).order_by("notification_type", "name")
