"""
Public webhooks API.
"""
import hashlib
import hmac
import logging

from apps.webhooks.models import Webhook, WebhookDelivery
from apps.webhooks.services import WebhookService
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .serializers import (
    WebhookDeliveryPublicSerializer,
    WebhookPublicSerializer,
    WebhookStatusSerializer,
)

logger = logging.getLogger(__name__)


class WebhookPublicThrottle(AnonRateThrottle):
    """Custom throttle for public webhook endpoints"""

    rate = "100/hour"


@method_decorator(csrf_exempt, name="dispatch")
class WebhookPublicView(views.APIView):
    """
    Public webhook delivery endpoint with signature verification.
    This is the main endpoint that external services call to deliver webhook events.
    """

    permission_classes = [AllowAny]
    throttle_classes = [WebhookPublicThrottle]

    def verify_webhook_signature(self, request, webhook):
        """Verify webhook signature"""
        if not webhook.secret:
            return True  # Skip verification if no secret

        signature = request.headers.get("X-Webhook-Signature")
        timestamp = request.headers.get("X-Webhook-Timestamp")

        if not signature or not timestamp:
            return False

        # Verify timestamp (prevent replay attacks)
        try:
            import time

            if (time.time() - int(timestamp)) > 300:  # 5 minutes
                logger.warning("Webhook timestamp too old")
                return False
        except (ValueError, TypeError):
            return False

        # Verify signature
        payload = f"{timestamp}{request.body.decode('utf-8')}"
        expected_signature = hmac.new(
            key=webhook.secret.encode("utf-8"),
            msg=payload.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def post(self, request, webhook_id=None, *args, **kwargs):
        """Handle webhook delivery"""
        try:
            # Get webhook by ID or from request
            if webhook_id:
                try:
                    webhook = Webhook.objects.get(id=webhook_id, is_active=True)
                except Webhook.DoesNotExist:
                    return Response(
                        {"error": "Webhook not found or inactive"}, status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Try to identify webhook by event type or other means
                return Response(
                    {"error": "Webhook ID required"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Verify signature if webhook has secret
            if not self.verify_webhook_signature(request, webhook):
                logger.warning(f"Invalid webhook signature for {webhook.name}")
                return Response({"error": "Invalid signature"}, status=status.HTTP_401_UNAUTHORIZED)

            # Parse webhook data
            event_type = request.headers.get("X-Event-Type", "unknown")
            event_id = request.headers.get("X-Event-ID", "")

            # Trigger webhook processing
            delivery = WebhookService.process_webhook_delivery(
                webhook=webhook,
                event_type=event_type,
                event_id=event_id,
                payload=request.data,
                headers=dict(request.headers),
                store=webhook.store,
            )

            return Response(
                {
                    "status": "received",
                    "delivery_id": delivery.id,
                    "message": "Webhook received successfully",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
            return Response(
                {"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WebhookStatusView(views.APIView):
    """
    Public webhook status endpoint for health checks.
    """

    permission_classes = [AllowAny]

    def get(self, request, webhook_id=None, *args, **kwargs):
        """Get webhook status"""
        if webhook_id:
            try:
                webhook = Webhook.objects.get(id=webhook_id)
                return Response(
                    {
                        "webhook_id": webhook.id,
                        "name": webhook.name,
                        "is_active": webhook.is_active,
                        "url": webhook.url,
                        "method": webhook.method,
                        "last_triggered_at": webhook.last_triggered_at,
                    }
                )
            except Webhook.DoesNotExist:
                return Response({"error": "Webhook not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # List all active webhooks (limited info)
            webhooks = Webhook.objects.filter(is_active=True).values(
                "id", "name", "url", "method", "last_triggered_at"
            )
            return Response({"active_webhooks": list(webhooks), "total_count": webhooks.count()})
