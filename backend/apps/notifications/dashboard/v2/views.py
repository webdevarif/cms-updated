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

    Full admin CRUD on notifications.
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
                {"error": "notification_ids required"}, status=status.HTTP_400_BAD_REQUEST
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
