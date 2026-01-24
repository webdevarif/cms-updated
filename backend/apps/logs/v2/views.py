"""
Views for logs API v2.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from ..models import LogEntry
from ..services import LogService
from ..tasks import log_event_async


class LogEntryViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only viewset for log entries"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return LogEntry.objects.filter(store=self.request.store)
    
    @extend_schema(
        summary="List log entries",
        description="List log entries with filtering",
        responses={200: list}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get log entry",
        description="Get a specific log entry",
        responses={200: dict}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class StoreAnalyticsView(viewsets.ViewSet):
    """Store analytics view"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get store analytics",
        description="Get analytics for the current store",
        responses={200: dict}
    )
    def list(self, request):
        days = int(request.query_params.get('days', 30))
        analytics = LogService.get_store_analytics(request.store, days)
        return Response(analytics)


class SecurityEventsView(viewsets.ViewSet):
    """Security events view"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get security events",
        description="Get detected suspicious activity",
        responses={200: list}
    )
    def list(self, request):
        hours = int(request.query_params.get('hours', 24))
        suspicious = LogService.detect_suspicious_activity(request.store, hours)
        return Response(suspicious)


@api_view(['POST'])
@permission_classes([AllowAny])
def track_event(request):
    """Track client-side events (clicks, hovers, etc.)"""
    try:
        event_data = {
            'event_type': request.data.get('event_type', 'CLICK'),
            'level': 'INFO',
            'message': request.data.get('message', ''),
            'store': getattr(request, 'store', None),
            'user': request.user if request.user.is_authenticated else None,
            'session_id': request.session.session_key,
            'ip_address': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'page_url': request.data.get('page_url', ''),
            'metadata': request.data.get('metadata', {}),
        }
        
        log_event_async.delay(event_data)
        return Response({'status': 'logged'}, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
