"""
Gift cards service with business logic.
"""
from decimal import Decimal

from apps.giftcards.models import GiftCard, GiftCardHistory
from django.db import transaction
from django.utils import timezone


class GiftCardService:
    """Gift card management service."""

    @staticmethod
    def create_gift_card(
        store, created_by, gift_card_type="digital", initial_balance=None, currency="USD", **kwargs
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
            GiftCardHistory.objects.create(
                gift_card=gift_card,
                action="created",
                amount=initial_balance,
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

            GiftCardHistory.objects.create(
                gift_card=gift_card,
                action="activated",
                created_by=activated_by,
                notes=notes or "Gift card activated",
            )

            return gift_card

    @staticmethod
    def redeem_gift_card(code, amount, user, order=None, method="online"):
        """
        Redeem amount from a gift card.
        """
        with transaction.atomic():
            try:
                gift_card = GiftCard.objects.get(code=code)
            except GiftCard.DoesNotExist:
                raise ValueError("Gift card not found")

            if not gift_card.is_redeemable:
                raise ValueError("Gift card cannot be redeemed")

            if gift_card.current_balance < amount:
                raise ValueError("Insufficient balance")

            # Update balance
            gift_card.current_balance -= amount
            gift_card.save()

            # Create history entry
            GiftCardHistory.objects.create(
                gift_card=gift_card,
                action="redeemed",
                amount=amount,
                order=order,
                created_by=user,
                notes=f"Redeemed {amount} {gift_card.currency} via {method}",
                metadata={"method": method},
            )

            # Check if fully redeemed
            if gift_card.current_balance == 0:
                gift_card.status = "redeemed"
                gift_card.save()

                GiftCardHistory.objects.create(
                    gift_card=gift_card,
                    action="redeemed",
                    created_by=user,
                    notes="Gift card fully redeemed",
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

            GiftCardHistory.objects.create(
                gift_card=gift_card,
                action="voided",
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
                "expires_at": gift_card.expires_at.isoformat() if gift_card.expires_at else None,
                "status": gift_card.status,
            }
        except GiftCard.DoesNotExist:
            return None

    @staticmethod
    def get_gift_card_analytics(store):
        """
        Get analytics for gift cards in a store.
        """
        queryset = GiftCard.objects.filter(store=store)

        return {
            "total_gift_cards": queryset.count(),
            "total_value": str(
                queryset.aggregate(total=models.Sum("initial_balance"))["total"] or Decimal("0.00")
            ),
            "active_gift_cards": queryset.filter(status="active").count(),
            "redeemed_gift_cards": queryset.filter(status="redeemed").count(),
            "expired_gift_cards": queryset.filter(status="expired").count(),
            "total_redeemed": str(
                queryset.filter(action="redeemed").aggregate(total=models.Sum("amount"))["total"]
                or Decimal("0.00")
            ),
        }

    @staticmethod
    def check_expired_cards():
        """
        Check and mark expired cards.
        """
        expired_cards = GiftCard.objects.filter(status="active", expires_at__lt=timezone.now())

        for gift_card in expired_cards:
            gift_card.status = "expired"
            gift_card.save()

            GiftCardHistory.objects.create(
                gift_card=gift_card, action="expired", notes="Gift card expired automatically"
            )

        return expired_cards.count()


__all__ = ["GiftCardService"]
