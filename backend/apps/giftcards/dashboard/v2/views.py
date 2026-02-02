"""
Dashboard gift cards views - admin interface for gift card management.
"""

from datetime import timedelta

from apps.giftcards.models import GiftCard, GiftCardHistory
from apps.giftcards.services.giftcard_service import GiftCardService
from core.permissions import IsStoreOwner
from django.db.models import Count, Q, Sum
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .serializers import (
    DashboardGiftCardAnalyticsSerializer,
    DashboardGiftCardBulkCreateSerializer,
    DashboardGiftCardCreateSerializer,
    DashboardGiftCardHistorySerializer,
    DashboardGiftCardSerializer,
)


class DashboardGiftCardViewSet(viewsets.ModelViewSet):
    """
    Dashboard gift cards API - admin access to all gift cards.

    Provides:
    - Full CRUD on gift cards
    - Bulk gift card creation
    - Gift card analytics
    - Gift card history
    - Email sending
    """

    permission_classes = [permissions.IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["code", "recipient_email", "recipient_name", "sender_name"]
    ordering_fields = ["created_at", "expires_at", "current_balance", "status"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return DashboardGiftCardCreateSerializer
        elif self.action == "bulk_create":
            return DashboardGiftCardBulkCreateSerializer
        return DashboardGiftCardSerializer

    def get_queryset(self):
        """Filter by store."""
        queryset = GiftCard.objects.select_related("store", "created_by")
        store = getattr(self.request, "store", None)
        if store:
            queryset = queryset.filter(store=store)
        return queryset

    @action(detail=False, methods=["post"])
    def bulk_action(self, request):
        """Perform bulk actions on gift cards (activate, void, delete, extend expiry)"""
        from django.db import transaction

        from .serializers import BulkActionSerializer

        serializer = BulkActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        action_type = serializer.validated_data["action"]
        giftcard_ids = serializer.validated_data["ids"]
        extra_data = serializer.validated_data.get("data", {})

        # Filter gift cards by store and IDs
        queryset = self.get_queryset().filter(id__in=giftcard_ids)
        total_requested = len(giftcard_ids)
        total_found = queryset.count()

        try:
            with transaction.atomic():
                if action_type == "activate":
                    updated = queryset.filter(status="inactive").update(status="active")
                    message = f"Successfully activated {updated} gift cards"

                elif action_type == "void":
                    reason = extra_data.get("reason", "Voided by admin")
                    voided_count = 0
                    for giftcard in queryset.filter(status="active"):
                        try:
                            GiftCardService.void_gift_card(giftcard, request.user, reason)
                            voided_count += 1
                        except Exception:
                            continue  # Skip if voiding fails
                    message = f"Successfully voided {voided_count} gift cards"

                elif action_type == "delete":
                    deleted = queryset.delete()[0]  # delete() returns (count, details)
                    message = f"Successfully deleted {deleted} gift cards"

                elif action_type == "extend_expiry":
                    days = extra_data.get("days", 30)
                    extended_count = 0
                    for giftcard in queryset.filter(status="active"):
                        try:
                            GiftCardService.extend_gift_card_expiry_days(
                                giftcard, days, request.user
                            )
                            extended_count += 1
                        except Exception:
                            continue  # Skip if extension fails
                    message = f"Successfully extended expiry for {extended_count} gift cards by {days} days"

                else:
                    return Response(
                        {"error": f"Unsupported action: {action_type}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Log the bulk operation
                from apps.analytics.services.event_service import EventService

                EventService.log_event(
                    event_type="GIFTCARD_BULK_UPDATE",
                    event_name=f"Bulk {action_type} operation on gift cards",
                    properties={
                        "user": request.user.id if request.user else None,
                        "store": request.store.id,
                        "action_type": action_type,
                        "count": len(giftcard_ids),
                        "giftcard_ids": giftcard_ids,
                    },
                    user=request.user,
                    store=request.store,
                )

                return Response(
                    {
                        "message": message,
                        "action": action_type,
                        "requested": total_requested,
                        "found": total_found,
                        "affected": (
                            updated
                            if "updated" in locals()
                            else (
                                deleted
                                if "deleted" in locals()
                                else (
                                    extended_count
                                    if "extended_count" in locals()
                                    else (voided_count if "voided_count" in locals() else 0)
                                )
                            )
                        ),
                    }
                )

        except Exception as e:
            return Response(
                {"error": f"Bulk operation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def bulk_create(self, request):
        """
        Bulk create gift cards.

        Args:
            gift_cards: List of gift card data
            send_emails: Whether to send emails (default: True)

        Returns:
            Created gift cards information
        """
        serializer = DashboardGiftCardBulkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            store = getattr(request, "store", None)
            if not store:
                return Response(
                    {"error": "Store not specified"}, status=status.HTTP_400_BAD_REQUEST
                )

            gift_cards_data = serializer.validated_data["gift_cards"]
            send_emails = serializer.validated_data.get("send_emails", True)

            created_cards = []
            for card_data in gift_cards_data:
                gift_card = GiftCardService.create_gift_card(
                    store=store,
                    amount=card_data["amount"],
                    recipient_email=card_data.get("recipient_email", ""),
                    recipient_name=card_data.get("recipient_name", ""),
                    sender_name=card_data.get("sender_name", ""),
                    message=card_data.get("message", ""),
                    gift_card_type=card_data.get("gift_card_type", "digital"),
                    created_by=request.user,
                    expires_at=card_data.get("expires_at"),
                )

                if send_emails and gift_card.recipient_email:
                    GiftCardService.send_gift_card_email(gift_card)

                created_cards.append(gift_card)

            return Response(
                DashboardGiftCardSerializer(created_cards, many=True).data,
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """
        Activate a gift card.

        Returns:
            Updated gift card information
        """
        gift_card = self.get_object()

        try:
            GiftCardService.activate_gift_card(gift_card, request.user)
            return Response(DashboardGiftCardSerializer(gift_card).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def void(self, request, pk=None):
        """
        Void a gift card.

        Args:
            reason: Reason for voiding

        Returns:
            Updated gift card information
        """
        gift_card = self.get_object()
        reason = request.data.get("reason", "Voided by admin")

        try:
            GiftCardService.void_gift_card(gift_card, request.user, reason)
            return Response(DashboardGiftCardSerializer(gift_card).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def extend_expiry(self, request, pk=None):
        """
        Extend gift card expiry.

        Args:
            days: Number of days to extend
            new_expiry_date: New expiry date (optional, overrides days)

        Returns:
            Updated gift card information
        """
        gift_card = self.get_object()
        days = request.data.get("days")
        new_expiry_date = request.data.get("new_expiry_date")

        try:
            if new_expiry_date:
                GiftCardService.extend_gift_card_expiry(gift_card, new_expiry_date, request.user)
            else:
                GiftCardService.extend_gift_card_expiry_days(gift_card, days, request.user)

            return Response(DashboardGiftCardSerializer(gift_card).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def send_email(self, request, pk=None):
        """
        Send gift card email.

        Returns:
            Email send result
        """
        gift_card = self.get_object()

        try:
            result = GiftCardService.send_gift_card_email(gift_card)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        """
        Get gift card history.

        Returns:
            Gift card history records
        """
        try:
            store = getattr(request, "store", None)
            if not store:
                return Response(
                    {"error": "Store not specified"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Use analytics service for history
            from ..services.giftcard_analytics_service import get_giftcard_history

            history = get_giftcard_history(store, giftcard_id=pk)
            serializer = DashboardGiftCardHistorySerializer(history, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": f"History retrieval failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """
        Get gift card analytics for the store with time-range filtering.

        Returns:
            Gift card analytics data with time-based metrics
        """
        try:
            store = getattr(request, "store", None)
            if not store:
                return Response(
                    {"error": "Store not specified"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Parse time range parameters
            start_date = request.GET.get("start_date")
            end_date = request.GET.get("end_date")

            filters = {}
            if start_date:
                filters["start_date"] = start_date
            if end_date:
                filters["end_date"] = end_date

            # Use analytics service
            from ..services.giftcard_analytics_service import get_giftcard_analytics

            analytics_data = get_giftcard_analytics(store, filters)
            return Response(analytics_data)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Analytics failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def expiring_soon(self, request):
        """
        Get gift cards expiring soon.

        Args:
            days: Days threshold (default: 30)

        Returns:
            List of expiring gift cards
        """
        days = int(request.query_params.get("days", 30))
        expiry_date = timezone.now() + timedelta(days=days)

        queryset = self.get_queryset().filter(expires_at__lte=expiry_date, status="active")

        serializer = DashboardGiftCardSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def low_balance(self, request):
        """
        Get gift cards with low balance.

        Args:
            threshold: Balance threshold (default: 10.00)

        Returns:
            List of low balance gift cards
        """
        threshold = float(request.query_params.get("threshold", 10.00))

        queryset = self.get_queryset().filter(
            current_balance__lte=threshold, current_balance__gt=0, status="active"
        )

        serializer = DashboardGiftCardSerializer(queryset, many=True)
        return Response(serializer.data)
