"""
Gift cards admin configuration.
"""

from django.contrib import admin

from .models import GiftCard, GiftCardHistory


@admin.register(GiftCard)
class GiftCardAdmin(admin.ModelAdmin):
    """Gift card admin configuration."""

    list_display = [
        "code",
        "store",
        "initial_balance",
        "current_balance",
        "currency",
        "gift_card_type",
        "status",
        "recipient_name",
        "expires_at",
        "created_at",
    ]
    list_filter = ["status", "gift_card_type", "store", "created_at", "expires_at"]
    search_fields = [
        "code",
        "recipient_name",
        "recipient_email",
        "sender_name",
        "sender_email",
    ]
    readonly_fields = ["code", "created_at", "updated_at"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("store", "code", "gift_card_type", "status")},
        ),
        ("Financial", {"fields": ("initial_balance", "current_balance", "currency")}),
        (
            "Recipient",
            {
                "fields": (
                    "recipient_name",
                    "recipient_email",
                    "sender_name",
                    "sender_email",
                )
            },
        ),
        ("Additional", {"fields": ("message", "expires_at", "metadata", "created_by")}),
    )


@admin.register(GiftCardHistory)
class GiftCardHistoryAdmin(admin.ModelAdmin):
    """Gift card history admin configuration."""

    list_display = [
        "gift_card",
        "action",
        "amount",
        "order",
        "created_by",
        "created_at",
        "notes",
    ]
    list_filter = ["action", "created_at", "gift_card__store"]
    search_fields = ["gift_card__code", "notes", "created_by__email"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
