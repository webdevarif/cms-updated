"""
Public SMTP email views.
"""

import logging

from apps.smtp.models import EmailLog
from apps.smtp.serializers import EmailLogSerializer
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

logger = logging.getLogger(__name__)


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
