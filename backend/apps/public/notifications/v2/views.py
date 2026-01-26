"""
Public notifications API placeholder.
"""
from rest_framework import viewsets


class NotificationPublicViewSet(viewsets.ViewSet):
    """
    No public notifications available.
    Notifications are user-specific and require authentication.
    Use customer layer for user notification access.
    """
    pass
