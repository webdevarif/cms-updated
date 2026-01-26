"""
Dashboard notifications API.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from core.permissions import IsStoreOwner
from apps.notifications.models import Notification, NotificationPreference
from .serializers import NotificationDashboardSerializer, NotificationPreferenceDashboardSerializer


class NotificationDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard notification management endpoints for store owners and admins.
    Provides full CRUD access to all notifications in the store.
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    queryset = Notification.objects.select_related('user')
    serializer_class = NotificationDashboardSerializer
    
    def get_queryset(self):
        """Filter notifications by store and status"""
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset
    
    @extend_schema(
        summary="Mark as Read",
        description="Mark notification as read",
        responses={200: NotificationSerializer}
    )
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Resend Notification",
        description="Resend failed notification",
        responses={200: NotificationSerializer}
    )
    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        """Resend notification"""
        notification = self.get_object()
        
        from apps.notifications.services import NotificationService
        NotificationService.send_notification(notification)
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationPreferenceDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard notification preference management endpoints.
    Allows admins to manage user notification preferences.
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    queryset = NotificationPreference.objects.select_related('user')
    serializer_class = NotificationPreferenceDashboardSerializer
    
    def get_queryset(self):
        """Filter preferences by store and notification type"""
        queryset = super().get_queryset()
        notification_type_filter = self.request.query_params.get('notification_type')
        if notification_type_filter:
            queryset = queryset.filter(notification_type=notification_type_filter)
        return queryset
