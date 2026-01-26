"""
Customer SMTP API.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from core.permissions import IsStoreUser
from apps.smtp.models import SmtpConfiguration, EmailTemplate, EmailLog
from apps.smtp.serializers import SmtpConfigSerializer, EmailTemplateSerializer, EmailLogSerializer

logger = logging.getLogger(__name__)


class SmtpCustomerViewSet(viewsets.ModelViewSet):
    """
    Customer SMTP configuration management endpoints for authenticated users.
    Users can manage their own SMTP configurations (limited scope).
    """
    serializer_class = SmtpConfigSerializer
    permission_classes = [IsAuthenticated, IsStoreUser]
    
    def get_queryset(self):
        return SmtpConfiguration.objects.filter(
            store=self.request.store,
            is_active=True
        )
    
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


class EmailTemplateCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer email template endpoints for authenticated users.
    Users can view but not modify templates.
    """
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAuthenticated, IsStoreUser]
    
    def get_queryset(self):
        return EmailTemplate.objects.filter(
            store=self.request.store,
            is_active=True
        )


class EmailLogCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer email log endpoints for authenticated users.
    Users can view their own email logs only.
    """
    serializer_class = EmailLogSerializer
    permission_classes = [IsAuthenticated, IsStoreUser]
    
    def get_queryset(self):
        return EmailLog.objects.filter(
            store=self.request.store,
            from_email__in=[self.request.user.email]
        ).order_by('-created_at')
