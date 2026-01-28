"""
Gift cards settings.
"""
from django.conf import settings

# Gift card code generation settings
GIFT_CARD_CODE_LENGTH = getattr(settings, "GIFT_CARD_CODE_LENGTH", 12)
GIFT_CARD_CODE_PREFIX = getattr(settings, "GIFT_CARD_CODE_PREFIX", "GC")
GIFT_CARD_CODE_CHARS = getattr(settings, "GIFT_CARD_CODE_CHARS", "ABCDEFGHJKLMNPQRSTUVWXYZ23456789")

# Gift card validation settings
GIFT_CARD_MIN_AMOUNT = getattr(settings, "GIFT_CARD_MIN_AMOUNT", 10.00)
GIFT_CARD_MAX_AMOUNT = getattr(settings, "GIFT_CARD_MAX_AMOUNT", 1000.00)
GIFT_CARD_DEFAULT_EXPIRY_DAYS = getattr(settings, "GIFT_CARD_DEFAULT_EXPIRY_DAYS", 365)

# Gift card statuses
GIFT_CARD_STATUS_ACTIVE = "active"
GIFT_CARD_STATUS_REDEEMED = "redeemed"
GIFT_CARD_STATUS_EXPIRED = "expired"
GIFT_CARD_STATUS_VOIDED = "voided"

# Gift card types
GIFT_CARD_TYPE_DIGITAL = "digital"
GIFT_CARD_TYPE_PHYSICAL = "physical"
GIFT_CARD_TYPE_PROMOTIONAL = "promotional"
GIFT_CARD_TYPE_REFUND = "refund"
GIFT_CARD_TYPE_LOYALTY = "loyalty"

# Cache settings
GIFT_CARD_CACHE_TIMEOUT = getattr(settings, "GIFT_CARD_CACHE_TIMEOUT", 300)  # 5 minutes
GIFT_CARD_BALANCE_CACHE_PREFIX = "gift_card_balance_"

# Email settings
GIFT_CARD_EMAIL_TEMPLATE = "emails/gift_card.html"
GIFT_CARD_EMAIL_SUBJECT = "Your Gift Card from {store_name}"
GIFT_CARD_EMAIL_FROM = "noreply@digitalfarmers.com"

# API settings
GIFT_CARD_REDEEM_THROTTLE_RATE = getattr(settings, "GIFT_CARD_REDEEM_THROTTLE_RATE", "5/minute")

# Default currency
DEFAULT_CURRENCY = getattr(settings, "DEFAULT_CURRENCY", "USD")
