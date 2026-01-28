"""
Dashboard webhooks API.
"""
from apps.webhooks.models import Webhook, WebhookDelivery
from apps.webhooks.services import WebhookService
from core.permissions import IsStoreOwner
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import WebhookDashboardSerializer, WebhookDeliveryDashboardSerializer


class WebhookDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard webhook management endpoints.
    Provides full admin CRUD operations for all store webhooks.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "description", "url"]
    ordering_fields = ["created_at", "updated_at", "name"]
    ordering = ["-created_at"]
    filterset_fields = ["is_active", "method"]

    def get_queryset(self):
        """Filter webhooks by current user's store"""
        return Webhook.objects.filter(store=self.request.store)

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        return WebhookDashboardSerializer

    def perform_create(self, serializer):
        """Set store when creating webhook"""
        serializer.save(store=self.request.store)

    @action(detail=True, methods=["post"])
    def test(self, request, pk=None):
        """Test webhook delivery"""
        webhook = self.get_object()
        result = WebhookService.test_webhook(webhook)
        return Response(result)

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        """Toggle webhook active status"""
        webhook = self.get_object()
        webhook.is_active = not webhook.is_active
        webhook.save()
        return Response({"is_active": webhook.is_active})

    @action(detail=True, methods=["post"])
    def regenerate_secret(self, request, pk=None):
        """Regenerate webhook secret"""
        webhook = self.get_object()
        webhook.secret = WebhookService.generate_secret()
        webhook.save()
        return Response({"secret": webhook.secret})

    @action(detail=True, methods=["get"])
    def deliveries(self, request, pk=None):
        """Get webhook delivery history"""
        webhook = self.get_object()
        deliveries = webhook.deliveries.all().order_by("-created_at")
        serializer = WebhookDeliveryDashboardSerializer(deliveries, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def bulk_action(self, request):
        """Perform bulk actions on webhooks"""
        webhook_ids = request.data.get("webhook_ids", [])
        action_type = request.data.get("action")

        if not webhook_ids or not action_type:
            return Response(
                {"error": "webhook_ids and action are required"}, status=status.HTTP_400_BAD_REQUEST
            )

        webhooks = self.get_queryset().filter(id__in=webhook_ids)
        results = {"success": 0, "failed": 0, "errors": []}

        for webhook in webhooks:
            try:
                if action_type == "activate":
                    webhook.is_active = True
                    webhook.save()
                    results["success"] += 1
                elif action_type == "deactivate":
                    webhook.is_active = False
                    webhook.save()
                    results["success"] += 1
                elif action_type == "delete":
                    webhook.delete()
                    results["success"] += 1
                else:
                    results["errors"].append(f"Unknown action: {action_type}")
                    results["failed"] += 1
            except Exception as e:
                results["errors"].append(f"Error with webhook {webhook.id}: {str(e)}")
                results["failed"] += 1

        return Response(results)

    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get webhook analytics overview"""
        webhooks = self.get_queryset()
        deliveries = WebhookDelivery.objects.filter(webhook__store=self.request.store)

        return Response(
            {
                "total_webhooks": webhooks.count(),
                "active_webhooks": webhooks.filter(is_active=True).count(),
                "total_deliveries": deliveries.count(),
                "successful_deliveries": deliveries.filter(status="success").count(),
                "failed_deliveries": deliveries.filter(status="failed").count(),
                "recent_deliveries": WebhookDeliveryDashboardSerializer(
                    deliveries.order_by("-created_at")[:10], many=True
                ).data,
            }
        )


class WebhookDeliveryDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard webhook delivery endpoints.
    Provides full admin CRUD operations for webhook deliveries.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = WebhookDeliveryDashboardSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["event_type", "status"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    filterset_fields = ["status", "webhook"]

    def get_queryset(self):
        """Filter deliveries by current user's store"""
        return WebhookDelivery.objects.filter(webhook__store=self.request.store).select_related(
            "webhook"
        )

    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        """Retry failed webhook delivery"""
        delivery = self.get_object()
        if delivery.status != "failed":
            return Response(
                {"error": "Only failed deliveries can be retried"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = WebhookService.retry_delivery(delivery)
        return Response(result)

    @action(detail=False, methods=["post"])
    def bulk_retry(self, request):
        """Retry multiple failed deliveries"""
        delivery_ids = request.data.get("delivery_ids", [])
        deliveries = self.get_queryset().filter(id__in=delivery_ids, status="failed")

        results = {"success": 0, "failed": 0, "errors": []}

        for delivery in deliveries:
            try:
                WebhookService.retry_delivery(delivery)
                results["success"] += 1
            except Exception as e:
                results["errors"].append(f"Error with delivery {delivery.id}: {str(e)}")
                results["failed"] += 1

        return Response(results)
