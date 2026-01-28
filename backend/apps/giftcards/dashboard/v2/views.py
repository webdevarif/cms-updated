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
                from apps.logs.tasks import log_event_async

                log_event_async.delay(
                    {
                        "event_type": "GIFTCARD_BULK_UPDATE",
                        "message": f"Bulk {action_type} operation on gift cards",
                        "user": request.user,
                        "store": request.store,
                        "entity_type": "GiftCard",
                        "metadata": {
                            "action": action_type,
                            "requested_count": total_requested,
                            "found_count": total_found,
                            "affected_count": updated
                            if "updated" in locals()
                            else deleted
                            if "deleted" in locals()
                            else extended_count
                            if "extended_count" in locals()
                            else voided_count
                            if "voided_count" in locals()
                            else 0,
                            "extra_data": extra_data,
                        },
                    }
                )

                return Response(
                    {
                        "message": message,
                        "action": action_type,
                        "requested": total_requested,
                        "found": total_found,
                        "affected": updated
                        if "updated" in locals()
                        else deleted
                        if "deleted" in locals()
                        else extended_count
                        if "extended_count" in locals()
                        else voided_count
                        if "voided_count" in locals()
                        else 0,
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
        gift_card = self.get_object()
        history = gift_card.history.all().select_related("created_by")
        serializer = DashboardGiftCardHistorySerializer(history, many=True)
        return Response(serializer.data)

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

            from datetime import datetime

            date_filter = {}
            if start_date:
                try:
                    start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                    date_filter["created_at__gte"] = start_dt
                except ValueError:
                    return Response(
                        {
                            "error": "Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if end_date:
                try:
                    end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                    date_filter["created_at__lte"] = end_dt
                except ValueError:
                    return Response(
                        {"error": "Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Base queryset with date filtering
            giftcards = self.get_queryset().filter(**date_filter)

            # Gift card status distribution
            total_giftcards = giftcards.count()
            active_giftcards = giftcards.filter(status="active").count()
            used_giftcards = giftcards.filter(status="used").count()
            expired_giftcards = giftcards.filter(status="expired").count()
            voided_giftcards = giftcards.filter(status="voided").count()

            # Financial metrics
            from django.db.models import Avg, Count, Sum

            total_value_created = giftcards.aggregate(total=Sum("initial_balance"))["total"] or 0

            remaining_value = (
                giftcards.filter(status="active").aggregate(total=Sum("current_balance"))["total"]
                or 0
            )

            redeemed_value = (
                giftcards.filter(status="used").aggregate(total=Sum("initial_balance"))["total"]
                or 0
            )

            avg_giftcard_value = giftcards.aggregate(avg=Avg("initial_balance"))["avg"] or 0

            # Redemption trends
            redemption_trends = []
            if start_date and end_date:
                from django.db.models.functions import TruncDate

                daily_redemptions = (
                    giftcards.filter(status="used")
                    .annotate(date=TruncDate("updated_at"))
                    .values("date")
                    .annotate(count=Count("id"), value=Sum("initial_balance"))
                    .order_by("date")
                )

                redemption_trends = [
                    {
                        "date": str(item["date"]),
                        "redemptions": item["count"],
                        "value": float(item["value"] or 0),
                    }
                    for item in daily_redemptions
                ]

            # Top recipients
            top_recipients = (
                giftcards.values("recipient_email")
                .annotate(count=Count("id"), total_value=Sum("initial_balance"))
                .exclude(recipient_email="")
                .order_by("-total_value")[:10]
            )

            recipients = []
            for recipient in top_recipients:
                recipients.append(
                    {
                        "email": recipient["recipient_email"],
                        "giftcards_count": recipient["count"],
                        "total_value": float(recipient["total_value"] or 0),
                    }
                )

            # Expiry analysis
            expiring_soon = giftcards.filter(
                status="active",
                expires_at__lte=timezone.now() + timedelta(days=30),
                expires_at__gt=timezone.now(),
            ).count()

            expired_unused = giftcards.filter(
                status="active", expires_at__lte=timezone.now()
            ).aggregate(count=Count("id"), value=Sum("current_balance"))

            # Sender analysis
            top_senders = (
                giftcards.values("sender_email")
                .annotate(count=Count("id"), total_value=Sum("initial_balance"))
                .exclude(sender_email="")
                .order_by("-total_value")[:10]
            )

            senders = []
            for sender in top_senders:
                senders.append(
                    {
                        "email": sender["sender_email"],
                        "giftcards_count": sender["count"],
                        "total_value": float(sender["total_value"] or 0),
                    }
                )

            analytics_data = {
                "overview": {
                    "total_giftcards": total_giftcards,
                    "active_giftcards": active_giftcards,
                    "used_giftcards": used_giftcards,
                    "expired_giftcards": expired_giftcards,
                    "voided_giftcards": voided_giftcards,
                    "redemption_rate": (used_giftcards / total_giftcards * 100)
                    if total_giftcards > 0
                    else 0,
                },
                "financial": {
                    "total_value_created": float(total_value_created),
                    "remaining_value": float(remaining_value),
                    "redeemed_value": float(redeemed_value),
                    "expired_value": float(expired_unused["value"] or 0),
                    "avg_giftcard_value": float(avg_giftcard_value),
                },
                "recipients": recipients,
                "senders": senders,
                "expiry_analysis": {
                    "expiring_soon_count": expiring_soon,
                    "expired_unused_count": expired_unused["count"],
                    "expired_unused_value": float(expired_unused["value"] or 0),
                },
                "trends": {"redemptions": redemption_trends},
                "time_range": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "has_date_filter": bool(start_date or end_date),
                },
            }

            return Response(analytics_data)

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
