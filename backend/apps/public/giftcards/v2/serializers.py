"""
Serializers for the Gift Cards API.
"""
from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from ..models import GiftCard, GiftCardHistory


class GiftCardHistorySerializer(serializers.ModelSerializer):
    """Serializer for GiftCardHistory model."""
    order = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = GiftCardHistory
        fields = [
            'id', 'action', 'amount', 'order', 'notes', 
            'metadata', 'created_at', 'created_by', 'gift_card'
        ]
        read_only_fields = ['id', 'created_at', 'created_by']


class GiftCardRedeemSerializer(serializers.Serializer):
    """Serializer for gift card redemption."""
    code = serializers.CharField(required=True)
    amount = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2,
        min_value=0.01,
        required=True
    )
    order_id = serializers.IntegerField(required=False)
    method = serializers.ChoiceField(
        choices=[('online', 'Online'), ('in_store', 'In Store')],
        default='online'
    )


class GiftCardActivateSerializer(serializers.Serializer):
    """Serializer for activating a gift card."""
    expires_at = serializers.DateTimeField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)


class GiftCardVoidSerializer(serializers.Serializer):
    """Serializer for voiding a gift card."""
    reason = serializers.CharField(required=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class GiftCardSerializer(serializers.ModelSerializer):
    """Serializer for GiftCard model with enhanced validation."""
    history = GiftCardHistorySerializer(many=True, read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_redeemable = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = GiftCard
        fields = [
            'id', 'code', 'initial_balance', 'current_balance', 'currency',
            'gift_card_type', 'status', 'expires_at', 'sender_name',
            'sender_email', 'recipient_name', 'recipient_email', 'message',
            'metadata', 'created_at', 'updated_at', 'history',
            'is_expired', 'is_redeemable', 'store', 'created_by'
        ]
        read_only_fields = [
            'id', 'current_balance', 'status', 'created_at', 'updated_at',
            'history', 'is_expired', 'is_redeemable', 'store', 'created_by'
        ]
    
    def validate_code(self, value):
        """Validate gift card code format."""
        from core.settings import GIFT_CARD_CODE_REGEX
        import re
        if not re.match(GIFT_CARD_CODE_REGEX, value):
            raise serializers.ValidationError("Invalid gift card code format.")
        return value
    
    def validate_initial_balance(self, value):
        """Validate initial balance is within allowed range."""
        from core.settings import GIFT_CARD_MIN_AMOUNT, GIFT_CARD_MAX_AMOUNT
        if value < GIFT_CARD_MIN_AMOUNT:
            raise serializers.ValidationError(
                f"Amount must be at least {GIFT_CARD_MIN_AMOUNT}."
            )
        if value > GIFT_CARD_MAX_AMOUNT:
            raise serializers.ValidationError(
                f"Amount cannot exceed {GIFT_CARD_MAX_AMOUNT}."
            )
        return value
