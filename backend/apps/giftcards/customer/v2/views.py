"""
Customer gift cards views - authenticated interface for gift card management.
"""

from apps.giftcards.models import GiftCard
from apps.giftcards.services.giftcard_service import GiftCardService
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .serializers import (
    CustomerGiftCardPurchaseSerializer,
    CustomerGiftCardRedeemSerializer,
    CustomerGiftCardSerializer,
)


class CustomerGiftCardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer gift cards API - authenticated access to own gift cards.

    Provides:
    - View own gift cards
    - Purchase gift cards
    - Redeem gift cards
    - Check own gift card balances
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["code", "recipient_email"]
    ordering_fields = ["created_at", "expires_at", "current_balance"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "purchase":
            return CustomerGiftCardPurchaseSerializer
        elif self.action == "redeem":
            return CustomerGiftCardRedeemSerializer
        return CustomerGiftCardSerializer

    def get_queryset(self):
        """Filter to user's own gift cards."""
        queryset = GiftCard.objects.filter(recipient_email=self.request.user.email).select_related(
            "store", "created_by"
        )

        store = getattr(self.request, "store", None)
        if store:
            queryset = queryset.filter(store=store)

        return queryset

    @action(detail=False, methods=["post"])
    def purchase(self, request):
        """
        Purchase a new gift card.

        Args:
            amount: Gift card amount
            recipient_email: Recipient email (optional, defaults to purchaser)
            recipient_name: Recipient name (optional)
            message: Personal message (optional)

        Returns:
            Created gift card information
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            store = getattr(request, "store", None)
            if not store:
                return Response(
                    {"error": "Store not specified"}, status=status.HTTP_400_BAD_REQUEST
                )

            gift_card = GiftCardService.create_gift_card(
                store=store,
                amount=serializer.validated_data["amount"],
                recipient_email=serializer.validated_data.get(
                    "recipient_email", request.user.email
                ),
                recipient_name=serializer.validated_data.get("recipient_name", ""),
                sender_name=serializer.validated_data.get(
                    "sender_name", request.user.get_full_name()
                ),
                message=serializer.validated_data.get("message", ""),
                gift_card_type="digital",
                created_by=request.user,
            )

            # Send email notification
            GiftCardService.send_gift_card_email(gift_card)

            return Response(
                CustomerGiftCardSerializer(gift_card).data,
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def redeem(self, request, pk=None):
        """
        Redeem a gift card.

        Args:
            amount: Amount to redeem (optional, defaults to full balance)
            order_id: Order ID if redeeming against an order (optional)
            notes: Redemption notes (optional)

        Returns:
            Redemption result
        """
        gift_card = self.get_object()

        if not gift_card.is_redeemable:
            return Response(
                {"error": "Gift card is not redeemable"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CustomerGiftCardRedeemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            amount = serializer.validated_data.get("amount", gift_card.current_balance)
            order_id = serializer.validated_data.get("order_id")
            notes = serializer.validated_data.get("notes", "")

            result = GiftCardService.redeem_gift_card(
                gift_card=gift_card,
                amount=amount,
                user=request.user,
                order_id=order_id,
                notes=notes,
            )

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def balance(self, request, pk=None):
        """
        Get gift card balance.

        Returns:
            Balance information for the gift card
        """
        gift_card = self.get_object()

        balance_info = GiftCardService.get_gift_card_balance(gift_card.code)
        return Response(balance_info)

    @action(detail=False, methods=["get"])
    def my_cards(self, request):
        """
        Get all gift cards for the current user.

        Returns:
            List of user's gift cards
        """
        queryset = self.get_queryset()
        serializer = CustomerGiftCardSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def active_cards(self, request):
        """
        Get active gift cards for the current user.

        Returns:
            List of user's active gift cards
        """
        queryset = self.get_queryset().filter(status="active")
        serializer = CustomerGiftCardSerializer(queryset, many=True)
        return Response(serializer.data)
