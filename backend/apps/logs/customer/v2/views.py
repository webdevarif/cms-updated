"""
Customer logs API views.
"""
from apps.logs.models import LogEntry
from apps.logs.services.log_service import LogService
from core.permissions import IsStoreUser
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class CustomerLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer log management endpoints.
    Provides read-only access to store-specific logs.
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ["message", "module", "level"]
    ordering_fields = ["created_at", "level", "module"]
    filterset_fields = ["level", "module"]

    def get_queryset(self):
        """Filter logs by current user's store"""
        return LogEntry.objects.filter(store=self.request.store)

    @extend_schema(
        summary="List store logs", description="Get paginated list of store-specific logs"
    )
    def list(self, request, *args, **kwargs):
        """List store logs"""
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Get log statistics", description="Get statistics about store logs")
    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get store log statistics"""
        stats = LogService.get_log_statistics(request.store)
        return Response(stats)

    @extend_schema(summary="Export store logs", description="Export store logs as CSV")
    @action(detail=False, methods=["get"])
    def export(self, request):
        """Export store logs as CSV"""
        csv_content = LogService.export_logs_csv(request.store)
        response = Response(csv_content, content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="store_logs.csv"'
        return Response(response)
