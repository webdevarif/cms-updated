"""
Dashboard gift cards serializers - admin interface for gift card management.
"""

from datetime import datetime
from decimal import Decimal

from apps.giftcards.models import GiftCard, GiftCardHistory
from rest_framework import serializers


class DashboardGiftCardSerializer(serializers.ModelSerializer):
    """Dashboard gift card serializer for admin access."""

    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
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
            "sender_email",
            "message",
            "expires_at",
            "is_expired",
            "is_redeemable",
            "metadata",
            "store",
            "created_by",
            "created_by_email",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "code",
            "initial_balance",
            "current_balance",
            "currency",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_email",
            "created_by_name",
        ]


class DashboardGiftCardCreateSerializer(serializers.ModelSerializer):
    """Dashboard gift card creation serializer."""

    class Meta:
        model = GiftCard
        fields = [
            "initial_balance",
            "currency",
            "gift_card_type",
            "recipient_name",
            "recipient_email",
            "sender_name",
            "sender_email",
            "message",
            "expires_at",
            "metadata",
        ]

    def create(self, validated_data):
        """Create gift card using service."""
        store = self.context["request"].store
        user = self.context["request"].user

        return GiftCardService.create_gift_card(
            store=store,
            amount=validated_data["initial_balance"],
            recipient_email=validated_data.get("recipient_email", ""),
            recipient_name=validated_data.get("recipient_name", ""),
            sender_name=validated_data.get("sender_name", ""),
            sender_email=validated_data.get("sender_email", ""),
            message=validated_data.get("message", ""),
            gift_card_type=validated_data.get("gift_card_type", "digital"),
            created_by=user,
            expires_at=validated_data.get("expires_at"),
            metadata=validated_data.get("metadata", {}),
        )


class DashboardGiftCardBulkCreateSerializer(serializers.Serializer):
    """Dashboard bulk gift card creation serializer."""

    gift_cards = serializers.ListField(child=serializers.DictField(), min_length=1, max_length=100)
    send_emails = serializers.BooleanField(default=True)

    def validate_gift_cards(self, value):
        """Validate gift card data."""
        for card_data in value:
            if "amount" not in card_data:
                raise serializers.ValidationError("Each gift card must have an amount")

            amount = card_data["amount"]
            if not isinstance(amount, (int, float, Decimal)) or amount <= 0:
                raise serializers.ValidationError("Amount must be greater than 0")

            if amount > 10000:  # Max $10,000
                raise serializers.ValidationError("Amount cannot exceed $10,000")

        return value


class DashboardGiftCardHistorySerializer(serializers.ModelSerializer):
    """Dashboard gift card history serializer."""

    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)

    class Meta:
        model = GiftCardHistory
        fields = [
            "id",
            "action",
            "amount",
            "order",
            "notes",
            "metadata",
            "created_by",
            "created_by_email",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "created_by",
            "created_by_email",
            "created_by_name",
        ]


class DashboardGiftCardAnalyticsSerializer(serializers.Serializer):
    """Dashboard gift card analytics serializer."""

    total_cards = serializers.IntegerField()
    active_cards = serializers.IntegerField()
    redeemed_cards = serializers.IntegerField()
    expired_cards = serializers.IntegerField()
    voided_cards = serializers.IntegerField()

    total_issued = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_redeemed = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_balance = serializers.DecimalField(max_digits=12, decimal_places=2)

    cards_by_type = serializers.DictField()
    cards_by_status = serializers.DictField()

    monthly_issued = serializers.ListField(child=serializers.DictField())
    monthly_redeemed = serializers.ListField(child=serializers.DictField())

    top_recipients = serializers.ListField(child=serializers.DictField())
    expiring_soon_count = serializers.IntegerField()
    low_balance_count = serializers.IntegerField()


class DashboardGiftCardUpdateSerializer(serializers.ModelSerializer):
    """Dashboard gift card update serializer."""

    class Meta:
        model = GiftCard
        fields = [
            "recipient_name",
            "recipient_email",
            "sender_name",
            "sender_email",
            "message",
            "expires_at",
            "metadata",
        ]


class DashboardGiftCardExtendExpirySerializer(serializers.Serializer):
    """Dashboard gift card expiry extension serializer."""

    days = serializers.IntegerField(min_value=1, max_value=365, required=False)
    new_expiry_date = serializers.DateTimeField(required=False)

    def validate(self, data):
        """Validate that either days or new_expiry_date is provided."""
        if not data.get("days") and not data.get("new_expiry_date"):
            raise serializers.ValidationError("Either 'days' or 'new_expiry_date' must be provided")

        if data.get("new_expiry_date") and data.get("days"):
            raise serializers.ValidationError(
                "Provide either 'days' or 'new_expiry_date', not both"
            )

        return data


class DashboardGiftCardVoidSerializer(serializers.Serializer):
    """Dashboard gift card void serializer."""

    reason = serializers.CharField(max_length=255, required=True)


class BulkActionSerializer(serializers.Serializer):
    """Serializer for bulk actions on gift cards"""

    action = serializers.ChoiceField(
        choices=[
            "activate",
            "void",
            "delete",
            "extend_expiry",
            "archive",
            "restore",
            "status_change",
        ]
    )
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of gift card IDs to perform action on",
    )
    data = serializers.DictField(
        required=False,
        help_text="Additional data for actions like void reason, expiry extension, status changes, etc.",
    )
