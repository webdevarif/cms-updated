"""
Customer SMTP configuration views.
"""
from apps.smtp.models import SmtpConfiguration
from apps.smtp.services import SmtpEmailService
from core.permissions import IsStoreUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import SMTPConfigCustomerSerializer


class SMTPConfigCustomerViewSet(viewsets.ModelViewSet):
    """
    Customer SMTP configuration management endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "host"]
    ordering_fields = ["created_at", "updated_at", "name"]
    ordering = ["-created_at"]
    filterset_fields = ["is_active", "is_default"]

    def get_queryset(self):
        """Filter SMTP configs by current user's store"""
        return SmtpConfiguration.objects.filter(store=self.request.store)

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        return SMTPConfigCustomerSerializer

    def perform_create(self, serializer):
        """Set store when creating SMTP config"""
        serializer.save(store=self.request.store)

    @action(detail=True, methods=["post"])
    def test_connection(self, request, pk=None):
        """Test SMTP connection"""
        smtp_config = self.get_object()
        result = SmtpEmailService.test_connection(smtp_config)
        return Response(result)

    @action(detail=True, methods=["post"])
    def send_test_email(self, request, pk=None):
        """Send test email"""
        smtp_config = self.get_object()
        result = SmtpEmailService.send_test_email(smtp_config, request.data.get("to_email"))
        return Response(result)
