"""
Dashboard logs API views.
"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from core.permissions import IsStoreOwner
from apps.logs.models import LogEntry
from apps.logs.services.log_service import LogService


class DashboardLogViewSet(viewsets.ModelViewSet):
    """
    Dashboard log management endpoints.
    Provides access to system logs for administrators.
    """
    
    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = None  # Will be set based on action
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['message', 'module', 'level']
    ordering_fields = ['created_at', 'level', 'module']
    filterset_fields = ['level', 'module']
    
    def get_queryset(self):
        """Filter logs by current user's store"""
        return LogEntry.objects.filter(store=self.request.store)
    
    @extend_schema(
        summary="List system logs",
        description="Get paginated list of system logs"
    )
    def list(self, request, *args, **kwargs):
        """List logs with filtering"""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create log entry",
        description="Create a new log entry"
    )
    def create(self, request, *args, **kwargs):
        """Create log entry"""
        log_entry = LogService.create_log(
            store=request.store,
            level=request.data.get('level', 'INFO'),
            message=request.data.get('message'),
            module=request.data.get('module'),
            extra_data=request.data.get('extra_data', {})
        )
        return Response({"id": log_entry.id, "created": True}, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Get log statistics",
        description="Get statistics about log entries"
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get log statistics"""
        stats = LogService.get_log_statistics(request.store)
        return Response(stats)
    
    @extend_schema(
        summary="Export logs",
        description="Export logs as CSV"
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export logs as CSV"""
        csv_content = LogService.export_logs_csv(request.store)
        response = Response(csv_content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="logs.csv"'
        return response
    
    @extend_schema(
        summary="Clear old logs",
        description="Clear logs older than specified days"
    )
    @action(detail=False, methods=['post'])
    def clear_old(self, request):
        """Clear old logs"""
        days = request.data.get('days', 30)
        cleared_count = LogService.clear_old_logs(request.store, days)
        return Response({
            "cleared_count": cleared_count,
            "message": f"Cleared {cleared_count} log entries older than {days} days"
        })
