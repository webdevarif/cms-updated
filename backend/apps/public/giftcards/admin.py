"""
Admin configuration for gift cards module.
"""
from django.contrib import admin
from .models import GiftCard, GiftCardHistory


@admin.register(GiftCard)
class GiftCardAdmin(admin.ModelAdmin):
    """Admin for GiftCard"""
    list_display = ['code', 'gift_card_type', 'status', 'initial_balance', 'current_balance', 'currency']
    list_filter = ['status', 'gift_card_type']
    search_fields = ['code', 'sender_name', 'recipient_name', 'recipient_email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(GiftCardHistory)
class GiftCardHistoryAdmin(admin.ModelAdmin):
    """Admin for GiftCardHistory"""
    list_display = ['gift_card', 'action', 'amount', 'created_at']
    list_filter = ['action']
    readonly_fields = ['created_at']
