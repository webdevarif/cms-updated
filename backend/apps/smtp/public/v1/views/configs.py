"""
Public SMTP configuration views.
"""

import logging
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from core.permissions import IsStoreOwner
from apps.smtp.models import SmtpConfiguration
from apps.smtp.serializers import SmtpConfigSerializer

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

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test SMTP connection"""
        try:
            config = self.get_object()
            # Test SMTP connection
            from apps.smtp.services.smtp_service import SmtpService
            result = SmtpService.test_connection(config)
            return Response(result)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
