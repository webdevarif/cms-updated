"""
Public notifications API views.
"""
from apps.notifications.models import Notification
from rest_framework import viewsets
from rest_framework.permissions import AllowAny


class NotificationPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public notification endpoints.
    """

    permission_classes = [AllowAny]
    queryset = Notification.objects.all()

    def get_queryset(self):
        """Filter by current user"""
        return Notification.objects.filter(user=self.request.user)
