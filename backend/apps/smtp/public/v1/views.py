"""
Public smtp API views.
"""
import logging

from apps.smtp.models import EmailLog, EmailTemplate, SmtpConfiguration
from apps.smtp.serializers import EmailLogSerializer, EmailTemplateSerializer, SmtpConfigSerializer
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class SmtpPublicViewSet(viewsets.ViewSet):
    """
    Public smtp endpoints.
    """

    permission_classes = [permissions.AllowAny]

    def list(self, request):
        return Response({"message": "smtp public API"})


class SmtpDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard SMTP configuration management endpoints for store owners and admins.
    Provides full CRUD access to SMTP configurations.
    """

    serializer_class = SmtpConfigSerializer
    permission_classes = [permissions.IsAuthenticated, IsStoreOwner]

    def get_queryset(self):
        return SmtpConfiguration.objects.filter(store=self.request.store)

    @action(detail=True, methods=["post"])
    def test_connection(self, request, pk=None):
        """Test SMTP connection"""
        try:
            config = self.get_object()
            # Test SMTP connection
            from apps.smtp.services.smtp_service import SmtpService

            result = SmtpService.test_connection(config)
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["post"])
    def send_test_email(self, request, pk=None):
        """Send a test email"""
        try:
            config = self.get_object()
            # Send test email
            from apps.smtp.services.smtp_service import SmtpService

            result = SmtpService.send_test_email(config, request.data)
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailTemplateDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard email template management endpoints.
    """

    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsStoreOwner]

    def get_queryset(self):
        return EmailTemplate.objects.filter(store=self.request.store)

    @action(detail=True, methods=["post"])
    def preview_email(self, request, pk=None):
        """Preview email with test data"""
        try:
            template = self.get_object()
            # Preview email
            from apps.smtp.services.smtp_service import SmtpService

            result = SmtpService.preview_email(template, request.data)
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailLogDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard email log management endpoints.
    """

    serializer_class = EmailLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsStoreOwner]

    def get_queryset(self):
        return EmailLog.objects.filter(store=self.request.store)

    @action(detail=True, methods=["post"])
    def resend_email(self, request, pk=None):
        """Resend a failed email"""
        try:
            log = self.get_object()
            # Resend email
            from apps.smtp.services.smtp_service import SmtpService

            result = SmtpService.resend_email(log)
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
