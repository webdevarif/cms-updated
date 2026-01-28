"""
Customer notification views.
"""
from apps.notifications.models import Notification, NotificationPreference
from apps.notifications.services import NotificationService
from core.permissions import IsStoreUser
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import NotificationCustomerSerializer, NotificationPreferenceCustomerSerializer


class NotificationCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer notification endpoints.

    Customer can only view their own notifications.
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = NotificationCustomerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "notification_type"]

    def get_queryset(self):
        """Filter by authenticated user"""
        return Notification.objects.filter(
            user=self.request.user, store__in=self.request.user.stores.all()
        ).order_by("-created_at")

    @extend_schema(
        summary="Mark notification as read",
        description="Mark a specific notification as read",
        responses={200: NotificationCustomerSerializer},
    )
    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.mark_as_read()

        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Mark all as read",
        description="Mark all user notifications as read",
        responses={200: dict},
    )
    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """Mark all user notifications as read"""
        count = NotificationService.mark_all_as_read(request.user)
        return Response(
            {"message": f"Marked {count} notifications as read"}, status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Get unread count",
        description="Get count of unread notifications",
        responses={200: dict},
    )
    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """Get unread notification count"""
        count = NotificationService.get_unread_count(request.user)
        return Response({"unread_count": count}, status=status.HTTP_200_OK)


class NotificationPreferenceCustomerViewSet(viewsets.ModelViewSet):
    """
    Customer notification preference endpoints.

    Customer can manage their own notification preferences.
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = NotificationPreferenceCustomerSerializer

    def get_queryset(self):
        """Filter by authenticated user"""
        return NotificationPreference.objects.filter(
            user=self.request.user, store__in=self.request.user.stores.all()
        ).order_by("notification_type")

    def perform_create(self, serializer):
        """Set user and store on creation"""
        serializer.save(
            user=self.request.user, store=self.request.user.stores.first()  # Default to first store
        )
