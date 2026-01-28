"""
Public logs API views.
"""
from apps.logs.models import LogEntry
from apps.logs.services.log_service import LogService
from drf_spectacular.utils import extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class PublicLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public log endpoints.
    Provides limited read-only access to system logs.
    """

    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["message", "module"]
    ordering_fields = ["created_at", "level"]

    def get_queryset(self):
        """Only return non-sensitive logs"""
        return LogEntry.objects.filter(
            level__in=["INFO", "WARNING"], is_sensitive=False
        ).select_related("store")

    @extend_schema(
        summary="List public logs", description="Get paginated list of non-sensitive system logs"
    )
    def list(self, request, *args, **kwargs):
        """List public logs"""
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Get system status", description="Get basic system status from logs")
    @action(detail=False, methods=["get"])
    def status(self, request):
        """Get system status from recent logs"""
        status_info = LogService.get_system_status()
        return Response(status_info)
