"""
Views for notifications API v2.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from rest_framework import viewsets
from core.permissions import IsStoreOwner

from ..models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """
    Notification management endpoints for dashboard
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    queryset = Notification.objects.select_related('user')
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        """Filter by store"""
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
        
        from ..services import NotificationService
        NotificationService.send_notification(notification)
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    Notification preference management endpoints
    """
    permission_classes = [IsAuthenticated]
    queryset = NotificationPreference.objects.select_related('user')
    serializer_class = NotificationPreferenceSerializer
    
    def get_queryset(self):
        """Filter by store"""
        queryset = super().get_queryset()
        notification_type_filter = self.request.query_params.get('notification_type')
        if notification_type_filter:
            queryset = queryset.filter(notification_type=notification_type_filter)
        return queryset
