"""
Dashboard SMTP API.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from core.permissions import IsStoreOwner
from apps.smtp.models import SmtpConfiguration, EmailTemplate, EmailLog
from apps.smtp.serializers import SmtpConfigSerializer, EmailTemplateSerializer, EmailLogSerializer

logger = logging.getLogger(__name__)


class SmtpDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard SMTP configuration management endpoints for store owners and admins.
    Provides full CRUD access to SMTP configurations.
    """
    serializer_class = SmtpConfigSerializer
    permission_classes = [IsAuthenticated, IsStoreOwner]
    
    def get_queryset(self):
        return SmtpConfiguration.objects.filter(store=self.request.store)
    
    def perform_create(self, serializer):
        serializer.save(store=self.request.store)
    
    @extend_schema(
        summary="Test SMTP connection",
        description="Test SMTP configuration connection",
        responses={200: {"success": bool, "message": str}}
    )
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test SMTP connection"""
        config = self.get_object()
        try:
            # Test connection logic here
            from apps.smtp.services import SmtpService
            smtp_service = SmtpService()
            result = smtp_service.test_connection(config)
            
            # Update last tested timestamp
            config.last_tested_at = timezone.now()
            config.save(update_fields=['last_tested_at'])
            
            return Response({
                'success': result['success'],
                'message': result.get('message', 'Connection test completed')
            })
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class EmailTemplateDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard email template management endpoints.
    Allows admins to manage email templates.
    """
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAuthenticated, IsStoreOwner]
    
    def get_queryset(self):
        return EmailTemplate.objects.filter(store=self.request.store)
    
    def perform_create(self, serializer):
        serializer.save(store=self.request.store)


class EmailLogDashboardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Dashboard email log endpoints for admins.
    Read-only access to all email logs.
    """
    serializer_class = EmailLogSerializer
    permission_classes = [IsAuthenticated, IsStoreOwner]
    
    def get_queryset(self):
        return EmailLog.objects.filter(store=self.request.store).order_by('-created_at')


class EmailWebhookDashboardViewSet(viewsets.ViewSet):
    """
    Dashboard email webhook management endpoints.
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    
    @extend_schema(
        summary="List webhook configurations",
        description="List available webhook configurations",
        responses={200: dict}
    )
    def list(self, request, *args, **kwargs):
        """List webhook configurations"""
        from apps.smtp.v2.v1.views.webhooks import WEBHOOK_CONFIG
        return Response({
            'webhook_configs': WEBHOOK_CONFIG,
            'status': 'configured'
        })
