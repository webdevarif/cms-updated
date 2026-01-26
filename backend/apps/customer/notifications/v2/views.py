"""
Customer notifications API.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from core.permissions import IsStoreUser
from apps.notifications.models import Notification, NotificationPreference
from .serializers import NotificationCustomerSerializer, NotificationPreferenceCustomerSerializer


class NotificationCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer notification endpoints for authenticated users.
    Users can view their own notifications and mark them as read.
    """
    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = NotificationCustomerSerializer
    
    def get_queryset(self):
        """Only return notifications for the current user"""
        return Notification.objects.filter(user=self.request.user).select_related()
    
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
        summary="Mark All as Read",
        description="Mark all unread notifications as read",
        responses={200: NotificationSerializer}
    )
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all unread notifications as read"""
        unread_notifications = self.get_queryset().filter(status='pending')
        for notification in unread_notifications:
            notification.mark_as_read()
        
        serializer = self.get_serializer(unread_notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Unread Count",
        description="Get count of unread notifications",
        responses={200: int}
    )
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = self.get_queryset().filter(status='pending').count()
        return Response({'unread_count': count}, status=status.HTTP_200_OK)


class NotificationPreferenceCustomerViewSet(viewsets.ModelViewSet):
    """
    Customer notification preference management endpoints.
    Users can manage their own notification preferences.
    """
    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = NotificationPreferenceCustomerSerializer
    
    def get_queryset(self):
        """Only return preferences for the current user"""
        return NotificationPreference.objects.filter(user=self.request.user).select_related()
    
    def get_serializer_context(self):
        """Add user to context for validation"""
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context
