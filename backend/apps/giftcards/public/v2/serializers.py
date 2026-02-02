"""
Public gift cards serializers - read-only interface for gift card balance checks.
Architectural + real implementation for public gift cards interface.
"""

from apps.giftcards.models import GiftCard
from rest_framework import serializers


class PublicGiftCardSerializer(serializers.ModelSerializer):
    """Public gift card serializer with limited fields for read-only access."""

    is_expired = serializers.BooleanField(read_only=True)
    is_redeemable = serializers.BooleanField(read_only=True)

    class Meta:
        model = GiftCard
        fields = [
            "id",
            "code",
            "current_balance",
            "currency",
            "gift_card_type",
            "status",
            "expires_at",
            "is_expired",
            "is_redeemable",
        ]
        read_only_fields = fields


class PublicGiftCardBalanceSerializer(serializers.Serializer):
    """Public gift card balance check serializer."""

    code = serializers.CharField(required=True)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    currency = serializers.CharField(max_length=3, read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    expires_at = serializers.DateTimeField(read_only=True)
    status = serializers.CharField(max_length=20, read_only=True)
