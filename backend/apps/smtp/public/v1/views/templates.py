"""
Public SMTP template views.
"""

import logging
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from core.permissions import IsStoreOwner
from apps.smtp.models import EmailTemplate
from apps.smtp.serializers import EmailTemplateSerializer

logger = logging.getLogger(__name__)


class EmailTemplateDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard email template management endpoints.
    """
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsStoreOwner]

    def get_queryset(self):
        return EmailTemplate.objects.filter(store=self.request.store)

    @action(detail=True, methods=['post'])
    def preview_email(self, request, pk=None):
        """Preview email with test data"""
        try:
            template = self.get_object()
            # Preview email
            from apps.smtp.services.smtp_service import SmtpService
            result = SmtpService.preview_email(template, request.data)
            return Response(result)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
