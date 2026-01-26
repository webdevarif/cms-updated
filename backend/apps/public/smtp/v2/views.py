"""
Public SMTP API.
"""
import logging
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from apps.smtp.v2.v1.views.webhooks import EmailWebhookView

logger = logging.getLogger(__name__)


class SmtpPublicViewSet(APIView):
    """
    Public SMTP status endpoint.
    Very limited public access - mainly for webhook handlers.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get SMTP service status"""
        try:
            # Check if SMTP service is configured
            from apps.smtp.models import SmtpConfiguration
            has_config = SmtpConfiguration.objects.filter(
                store=request.store,
                is_active=True
            ).exists()
            
            return Response({
                'status': 'available' if has_config else 'not_configured',
                'webhooks_enabled': True
            })
        except Exception as e:
            logger.error(f"Error checking SMTP status: {str(e)}")
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EmailWebhookPublicView(EmailWebhookView):
    """
    Public email webhook handler with signature verification.
    This is the same as the dashboard webhook but accessible publicly.
    """
    pass  # Inherits all functionality from the dashboard webhook view
