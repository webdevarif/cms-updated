"""
Public test API views.
"""

from apps.webhooks.models import Webhook, WebhookDelivery
from apps.webhooks.services import WebhookService
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .serializers import (
    TestDashboardSerializer,
    TestDeliveryDashboardSerializer,
    TestResultsSummarySerializer,
)


class TestPublicViewSet(viewsets.ViewSet):
    """
    Public test endpoints.
    """

    permission_classes = [permissions.AllowAny]

    def list(self, request):
        return Response({"message": "test public API"})


class TestDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard test management endpoints for store owners and admins.
    """

    permission_classes = [IsStoreOwner]
    serializer_class = TestDashboardSerializer

    def get_queryset(self):
        """Filter by current user's stores"""
        return Webhook.objects.filter(store=self.request.store)

    @action(detail=True, methods=["post"])
    def run_test(self, request, pk=None):
        """Run a test suite"""
        try:
            webhook = self.get_object()
            results = WebhookService.run_test_suite(webhook)
            serializer = TestResultsSummarySerializer(results)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestDeliveryDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard test delivery management endpoints.
    """

    permission_classes = [IsStoreOwner]
    serializer_class = TestDeliveryDashboardSerializer

    def get_queryset(self):
        """Filter by current user's stores"""
        return WebhookDelivery.objects.filter(webhook__store=self.request.store)

    @action(detail=True, methods=["post"])
    def test_delivery(self, request, pk=None):
        """Test webhook delivery"""
        try:
            webhook = self.get_object()
            results = WebhookService.test_webhook_delivery(webhook)
            return Response(results)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
