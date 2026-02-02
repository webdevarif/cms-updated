"""
Gift cards service with business logic.

This service handles:
- Gift card issuance and activation
- Gift card redemption and balance management
- Gift card status and lifecycle management
- Gift card history tracking and logging

All balance and status changes should go through this service to ensure proper auditing.
"""

from decimal import Decimal

from apps.giftcards.models import GiftCard, GiftCardHistory
from django.db import transaction
from django.utils import timezone


class GiftCardService:
    """
    Gift card management service.

    This service handles:
    - Gift card issuance and activation
    - Gift card redemption and balance management
    - Gift card status and lifecycle management
    - Gift card history tracking and logging

    All balance and status changes should go through this service to ensure proper auditing.
    """

    # Issuance & activation methods
    @staticmethod
    def create_gift_card(
        store,
        created_by,
        gift_card_type="digital",
        initial_balance=None,
        currency="USD",
        **kwargs,
    ):
        """
        Create a new gift card.
        """
        if initial_balance is None:
            initial_balance = Decimal("0.00")

        with transaction.atomic():
            gift_card = GiftCard.objects.create(
                store=store,
                created_by=created_by,
                gift_card_type=gift_card_type,
                initial_balance=initial_balance,
                current_balance=initial_balance,
                currency=currency,
                status="inactive",
                **kwargs,
            )

            # Create history entry
            GiftCardService._create_history_entry(
                gift_card,
                "created",
                initial_balance,
                created_by=created_by,
                notes=f"Gift card created with initial balance of {initial_balance} {currency}",
            )

            return gift_card

    @staticmethod
    def activate_gift_card(gift_card, activated_by, expires_at=None, notes=None):
        """
        Activate a gift card.
        """
        with transaction.atomic():
            gift_card.status = "active"
            if expires_at:
                gift_card.expires_at = expires_at

            gift_card.save()

            GiftCardService._create_history_entry(
                gift_card,
                "activated",
                None,
                created_by=activated_by,
                notes=notes or "Gift card activated",
            )

            return gift_card

    # Redemption methods
    @staticmethod
    def redeem_gift_card(code, amount, user, order=None, method="online"):
        """
        Redeem amount from a gift card.

        This is the primary integration point for ecommerce/payment code.
        All gift card applications to orders should use this method.

        Args:
            code: Gift card code
            amount: Amount to redeem
            user: User redeeming the card
            order: Optional Order instance for redemption tracking
            method: Redemption method (online, in-store, etc.)

        Returns:
            GiftCard: Updated gift card instance

        Raises:
            ValueError: If gift card not found, not redeemable, or insufficient balance
        """
        with transaction.atomic():
            try:
                gift_card = GiftCard.objects.get(code=code)
            except GiftCard.DoesNotExist:
                raise ValueError("Gift card not found")

            # Validate gift card status and balance
            GiftCardService._ensure_active_and_not_expired(gift_card)
            GiftCardService._check_balance_sufficient(gift_card, amount)

            # Update balance
            gift_card.current_balance -= amount
            gift_card.save()

            # Create history entry
            GiftCardService._create_history_entry(
                gift_card,
                "redeemed",
                amount,
                order=order,
                created_by=user,
                notes=f"Redeemed {amount} {gift_card.currency} via {method}",
                metadata={"method": method},
            )

            # Check if fully redeemed
            if gift_card.current_balance == 0:
                gift_card.status = "redeemed"
                gift_card.save()

                GiftCardService._create_history_entry(
                    gift_card,
                    "redeemed",
                    None,
                    created_by=user,
                    notes="Gift card fully redeemed",
                )

            return gift_card

    # Status & lifecycle methods
    @staticmethod
    def validate_gift_card(code):
        """
        Validate a gift card (existence, status, expiry).

        Args:
            code: Gift card code

        Returns:
            dict: Validation result with gift card info

        Raises:
            ValueError: If gift card not found or invalid
        """
        try:
            gift_card = GiftCard.objects.get(code=code)

            GiftCardService._ensure_active_and_not_expired(gift_card)

            return {
                "code": gift_card.code,
                "balance": str(gift_card.current_balance),
                "currency": gift_card.currency,
                "is_expired": gift_card.is_expired,
                "expires_at": (gift_card.expires_at.isoformat() if gift_card.expires_at else None),
                "status": gift_card.status,
            }
        except GiftCard.DoesNotExist:
            raise ValueError("Gift card not found")

    @staticmethod
    def expire_gift_card(gift_card, expired_by, notes=None):
        """
        Mark a gift card as expired.
        """
        with transaction.atomic():
            gift_card.status = "expired"
            gift_card.save()

            GiftCardService._create_history_entry(
                gift_card,
                "expired",
                None,
                created_by=expired_by,
                notes=notes or "Gift card expired automatically",
            )

            return gift_card

    @staticmethod
    def void_gift_card(gift_card, voided_by, reason, notes=None):
        """
        Void a gift card.
        """
        with transaction.atomic():
            gift_card.status = "voided"
            gift_card.save()

            GiftCardService._create_history_entry(
                gift_card,
                "voided",
                None,
                created_by=voided_by,
                notes=f"Voided: {reason}. {notes or ''}",
            )

            return gift_card

    @staticmethod
    def get_gift_card_balance(code):
        """
        Get gift card balance information.
        """
        try:
            gift_card = GiftCard.objects.get(code=code)

            return {
                "code": gift_card.code,
                "balance": str(gift_card.current_balance),
                "currency": gift_card.currency,
                "is_expired": gift_card.is_expired,
                "expires_at": (gift_card.expires_at.isoformat() if gift_card.expires_at else None),
                "status": gift_card.status,
            }
        except GiftCard.DoesNotExist:
            return None

    # Internal helper methods
    @staticmethod
    def _ensure_active_and_not_expired(gift_card):
        """
        Ensure gift card is active and not expired.

        Args:
            gift_card: GiftCard instance

        Raises:
            ValueError: If gift card is not redeemable
        """
        if not gift_card.is_redeemable:
            raise ValueError("Gift card cannot be redeemed")

    @staticmethod
    def _check_balance_sufficient(gift_card, amount):
        """
        Check if gift card has sufficient balance.

        Args:
            gift_card: GiftCard instance
            amount: Amount to check

        Raises:
            ValueError: If insufficient balance
        """
        if gift_card.current_balance < amount:
            raise ValueError("Insufficient balance")

    @staticmethod
    def _create_history_entry(
        gift_card, action, amount=None, order=None, user=None, notes=None, metadata=None
    ):
        """
        Create a history entry for a gift card transaction.

        Args:
            gift_card: GiftCard instance
            action: Action type (created, activated, redeemed, expired, voided)
            amount: Transaction amount (optional)
            order: Related Order instance (optional)
            user: User performing action (optional)
            notes: Additional notes (optional)
            metadata: Additional metadata (optional)
        """
        GiftCardHistory.objects.create(
            gift_card=gift_card,
            action=action,
            amount=amount,
            order=order,
            created_by=user,
            notes=notes,
            metadata=metadata or {},
        )

    @staticmethod
    def check_expired_cards():
        """
        Check and mark expired cards.
        """
        expired_cards = GiftCard.objects.filter(status="active", expires_at__lt=timezone.now())

        for gift_card in expired_cards:
            gift_card.status = "expired"
            gift_card.save()

            GiftCardService._create_history_entry(
                gift_card, "expired", None, notes="Gift card expired automatically"
            )

        return expired_cards.count()


__all__ = ["GiftCardService"]
