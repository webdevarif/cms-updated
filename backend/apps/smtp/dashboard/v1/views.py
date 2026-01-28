"""
Dashboard SMTP API views.
"""
from apps.smtp.models import EmailLog, SMTPConfig
from apps.smtp.services import SMTPService
from core.permissions import IsStoreOwner
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import EmailLogDashboardSerializer, SMTPConfigDashboardSerializer


class SMTPConfigDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard SMTP configuration management endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "host"]
    ordering_fields = ["created_at", "updated_at", "name"]
    ordering = ["-created_at"]
    filterset_fields = ["is_active", "is_default"]

    def get_queryset(self):
        """Filter SMTP configs by current user's store"""
        return SMTPConfig.objects.filter(store=self.request.store)

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        return SMTPConfigDashboardSerializer

    def perform_create(self, serializer):
        """Set store when creating SMTP config"""
        serializer.save(store=self.request.store)

    @action(detail=True, methods=["post"])
    def test_connection(self, request, pk=None):
        """Test SMTP connection"""
        smtp_config = self.get_object()
        result = SMTPService.test_connection(smtp_config)
        return Response(result)

    @action(detail=True, methods=["post"])
    def send_test_email(self, request, pk=None):
        """Send test email"""
        smtp_config = self.get_object()
        result = SMTPService.send_test_email(smtp_config, request.data.get("to_email"))
        return Response(result)

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        """Toggle SMTP config active status"""
        smtp_config = self.get_object()
        smtp_config.is_active = not smtp_config.is_active
        smtp_config.save()
        return Response({"is_active": smtp_config.is_active})

    @action(detail=True, methods=["post"])
    def set_default(self, request, pk=None):
        """Set as default SMTP config"""
        smtp_config = self.get_object()
        SMTPConfig.objects.filter(store=self.request.store).update(is_default=False)
        smtp_config.is_default = True
        smtp_config.save()
        return Response({"is_default": True})

    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get SMTP analytics overview"""
        configs = self.get_queryset()
        logs = EmailLog.objects.filter(smtp_config__store=self.request.store)

        return Response(
            {
                "total_configs": configs.count(),
                "active_configs": configs.filter(is_active=True).count(),
                "total_emails_sent": logs.count(),
                "successful_emails": logs.filter(status="sent").count(),
                "failed_emails": logs.filter(status="failed").count(),
                "recent_logs": EmailLogDashboardSerializer(
                    logs.order_by("-created_at")[:10], many=True
                ).data,
            }
        )


class EmailLogDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard email log endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = EmailLogDashboardSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["to_email", "subject", "status"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    filterset_fields = ["status", "smtp_config"]

    def get_queryset(self):
        """Filter email logs by current user's store"""
        return EmailLog.objects.filter(smtp_config__store=self.request.store).select_related(
            "smtp_config"
        )

    @action(detail=False, methods=["post"])
    def bulk_delete(self, request):
        """Bulk delete email logs"""
        log_ids = request.data.get("log_ids", [])
        deleted_count = EmailLog.objects.filter(
            id__in=log_ids, smtp_config__store=self.request.store
        ).delete()[0]
        return Response({"deleted_count": deleted_count})

    @action(detail=False, methods=["post"])
    def clear_old_logs(self, request):
        """Clear old email logs"""
        days = request.data.get("days", 30)
        deleted_count = SMTPService.clear_old_logs(self.request.store, days)
        return Response({"deleted_count": deleted_count})
