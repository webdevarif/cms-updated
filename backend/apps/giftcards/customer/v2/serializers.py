"""
Customer gift cards serializers - authenticated interface for gift card management.
"""

from decimal import Decimal

from apps.giftcards.models import GiftCard
from rest_framework import serializers


class CustomerGiftCardSerializer(serializers.ModelSerializer):
    """Customer gift card serializer for viewing own gift cards."""

    is_expired = serializers.BooleanField(read_only=True)
    is_redeemable = serializers.BooleanField(read_only=True)

    class Meta:
        model = GiftCard
        fields = [
            "id",
            "code",
            "initial_balance",
            "current_balance",
            "currency",
            "gift_card_type",
            "status",
            "recipient_name",
            "recipient_email",
            "sender_name",
            "message",
            "expires_at",
            "is_expired",
            "is_redeemable",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "code",
            "initial_balance",
            "current_balance",
            "currency",
            "gift_card_type",
            "status",
            "created_at",
            "updated_at",
        ]


class CustomerGiftCardPurchaseSerializer(serializers.Serializer):
    """Customer gift card purchase serializer."""

    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    recipient_email = serializers.EmailField(required=False)
    recipient_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    sender_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    message = serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        """Validate amount is positive and reasonable."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        if value > 10000:  # Max $10,000
            raise serializers.ValidationError("Amount cannot exceed $10,000")
        return value


class CustomerGiftCardRedeemSerializer(serializers.Serializer):
    """Customer gift card redemption serializer."""

    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, min_value=Decimal("0.01")
    )
    order_id = serializers.UUIDField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        """Validate amount is positive."""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value


class CustomerGiftCardBalanceSerializer(serializers.Serializer):
    """Customer gift card balance check serializer."""

    balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    currency = serializers.CharField(max_length=3, read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_redeemable = serializers.BooleanField(read_only=True)
    expires_at = serializers.DateTimeField(read_only=True)
