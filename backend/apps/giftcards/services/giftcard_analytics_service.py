"""
Gift card analytics service for giftcards app.

Provides analytics and statistics for gift cards and transaction history.
"""

from datetime import datetime, timedelta

from django.db.models import Avg, Count, Sum
from django.utils import timezone

from ..models.gift_card import GiftCard
from ..models.history import GiftCardHistory


def get_giftcard_analytics(store, filters=None):
    """
    Get comprehensive analytics for gift cards in a store.

    Args:
        store: Store instance
        filters: dict with optional filters (start_date, end_date)

    Returns:
        dict: Comprehensive analytics including status distribution, financial metrics, and trends
    """
    if filters is None:
        filters = {}

    # Parse date filters
    date_filter = _parse_date_filters(filters.get("start_date"), filters.get("end_date"))

    # Base queryset with date filtering
    giftcards = GiftCard.objects.filter(store=store, **date_filter)

    # Gift card status distribution
    total_giftcards = giftcards.count()
    active_giftcards = giftcards.filter(status="active").count()
    used_giftcards = giftcards.filter(status="redeemed").count()
    expired_giftcards = giftcards.filter(status="expired").count()
    voided_giftcards = giftcards.filter(status="voided").count()

    # Financial metrics
    financial_metrics = _calculate_financial_metrics(giftcards)

    # Redemption trends
    redemption_trends = []
    if filters.get("start_date") and filters.get("end_date"):
        redemption_trends = _calculate_redemption_trends(
            giftcards, filters["start_date"], filters["end_date"]
        )

    # Top recipients and senders
    recipients = _get_top_recipients(giftcards)
    senders = _get_top_senders(giftcards)

    # Expiry analysis
    expiry_analysis = _calculate_expiry_analysis(giftcards)

    return {
        "overview": {
            "total_giftcards": total_giftcards,
            "active_giftcards": active_giftcards,
            "used_giftcards": used_giftcards,
            "expired_giftcards": expired_giftcards,
            "voided_giftcards": voided_giftcards,
            "redemption_rate": (
                (used_giftcards / total_giftcards * 100) if total_giftcards > 0 else 0
            ),
        },
        "financial": financial_metrics,
        "recipients": recipients,
        "senders": senders,
        "expiry_analysis": expiry_analysis,
        "trends": {"redemptions": redemption_trends},
        "time_range": {
            "start_date": filters.get("start_date"),
            "end_date": filters.get("end_date"),
            "has_date_filter": bool(filters.get("start_date") or filters.get("end_date")),
        },
    }


def get_giftcard_history(store, giftcard_id=None):
    """
    Get gift card history for a store or specific gift card.

    Args:
        store: Store instance
        giftcard_id: Optional specific gift card ID

    Returns:
        list or QuerySet: Gift card history records
    """
    if giftcard_id:
        try:
            gift_card = GiftCard.objects.get(id=giftcard_id, store=store)
            return gift_card.history.all().select_related("created_by")
        except GiftCard.DoesNotExist:
            return []
    else:
        return GiftCardHistory.objects.filter(gift_card__store=store).select_related(
            "gift_card", "created_by", "order"
        )


def _parse_date_filters(start_date, end_date):
    """
    Parse date filters from string to datetime objects.

    Args:
        start_date: Start date string in ISO format
        end_date: End date string in ISO format

    Returns:
        dict: Django date filter dictionary
    """
    date_filter = {}

    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            date_filter["created_at__gte"] = start_dt
        except ValueError:
            raise ValueError("Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)")

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            date_filter["created_at__lte"] = end_dt
        except ValueError:
            raise ValueError("Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)")

    return date_filter


def _calculate_financial_metrics(giftcards):
    """
    Calculate financial metrics for gift cards.

    Args:
        giftcards: GiftCard queryset

    Returns:
        dict: Financial metrics
    """
    total_value_created = giftcards.aggregate(total=Sum("initial_balance"))["total"] or 0

    remaining_value = (
        giftcards.filter(status="active").aggregate(total=Sum("current_balance"))["total"] or 0
    )

    redeemed_value = (
        giftcards.filter(status="redeemed").aggregate(total=Sum("initial_balance"))["total"] or 0
    )

    avg_giftcard_value = giftcards.aggregate(avg=Avg("initial_balance"))["avg"] or 0

    return {
        "total_value_created": float(total_value_created),
        "remaining_value": float(remaining_value),
        "redeemed_value": float(redeemed_value),
        "expired_value": 0,  # Would need expired unused calculation
        "avg_giftcard_value": float(avg_giftcard_value),
    }


def _calculate_redemption_trends(giftcards, start_date, end_date):
    """
    Calculate redemption trends by date.

    Args:
        giftcards: GiftCard queryset
        start_date: Start date string
        end_date: End date string

    Returns:
        list: Daily redemption trends
    """
    from django.db.models.functions import TruncDate

    daily_redemptions = (
        giftcards.filter(status="redeemed")
        .annotate(date=TruncDate("updated_at"))
        .values("date")
        .annotate(count=Count("id"), value=Sum("initial_balance"))
        .order_by("date")
    )

    return [
        {
            "date": str(item["date"]),
            "redemptions": item["count"],
            "value": float(item["value"] or 0),
        }
        for item in daily_redemptions
    ]


def _get_top_recipients(giftcards):
    """
    Get top recipients by total gift card value.

    Args:
        giftcards: GiftCard queryset

    Returns:
        list: Top recipients with gift card counts and values
    """
    top_recipients = (
        giftcards.values("recipient_email")
        .annotate(count=Count("id"), total_value=Sum("initial_balance"))
        .exclude(recipient_email="")
        .order_by("-total_value")[:10]
    )

    return [
        {
            "email": recipient["recipient_email"],
            "giftcards_count": recipient["count"],
            "total_value": float(recipient["total_value"] or 0),
        }
        for recipient in top_recipients
    ]


def _get_top_senders(giftcards):
    """
    Get top senders by total gift card value.

    Args:
        giftcards: GiftCard queryset

    Returns:
        list: Top senders with gift card counts and values
    """
    top_senders = (
        giftcards.values("sender_email")
        .annotate(count=Count("id"), total_value=Sum("initial_balance"))
        .exclude(sender_email="")
        .order_by("-total_value")[:10]
    )

    return [
        {
            "email": sender["sender_email"],
            "giftcards_count": sender["count"],
            "total_value": float(sender["total_value"] or 0),
        }
        for sender in top_senders
    ]


def _calculate_expiry_analysis(giftcards):
    """
    Calculate expiry analysis for gift cards.

    Args:
        giftcards: GiftCard queryset

    Returns:
        dict: Expiry analysis metrics
    """
    expiring_soon = giftcards.filter(
        status="active",
        expires_at__lte=timezone.now() + timedelta(days=30),
        expires_at__gt=timezone.now(),
    ).count()

    expired_unused = giftcards.filter(status="active", expires_at__lte=timezone.now()).aggregate(
        count=Count("id"), value=Sum("current_balance")
    )

    return {
        "expiring_soon_count": expiring_soon,
        "expired_unused_count": expired_unused["count"],
        "expired_unused_value": float(expired_unused["value"] or 0),
    }
