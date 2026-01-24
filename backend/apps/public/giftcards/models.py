"""
Gift cards models.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import random
import string


class GiftCard(models.Model):
    """Gift card model"""
    GIFT_CARD_TYPES = [
        ('digital', 'Digital'),
        ('physical', 'Physical'),
        ('promotional', 'Promotional'),
        ('refund', 'Refund'),
        ('loyalty', 'Loyalty'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('redeemed', 'Redeemed'),
        ('expired', 'Expired'),
        ('voided', 'Voided'),
    ]
    
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    initial_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    current_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(max_length=3, default='USD')
    gift_card_type = models.CharField(max_length=20, choices=GIFT_CARD_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    expires_at = models.DateTimeField(null=True, blank=True)
    sender_name = models.CharField(max_length=100, blank=True)
    sender_email = models.EmailField(blank=True)
    recipient_name = models.CharField(max_length=100, blank=True)
    recipient_email = models.EmailField(blank=True)
    message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'giftcards'
        db_table = 'giftcards_giftcard'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['status']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.current_balance}/{self.initial_balance} {self.currency}"
    
    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at
    
    def is_redeemable(self):
        return (
            self.status == 'active' and 
            self.current_balance > 0 and 
            not self.is_expired()
        )

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        old_balance = None
        
        if not is_new:
            old_instance = GiftCard.objects.get(pk=self.pk)
            old_status = old_instance.status
            old_balance = old_instance.current_balance
        
        super().save(*args, **kwargs)
        
        from apps.logs.tasks import log_event_async
        
        if is_new:
            log_event_async.delay({
                'event_type': 'create_giftcard_public_giftcards',
                'message': f"Gift card created: {self.code}",
                'store_id': self.store.id,
                'user_id': self.created_by.id if self.created_by else None,
                'object_id': self.id,
                'metadata': {
                    'code': self.code,
                    'initial_balance': str(self.initial_balance),
                    'current_balance': str(self.current_balance),
                    'type': self.gift_card_type,
                    'currency': self.currency
                }
            })
        else:
            # Log status changes
            if old_status != self.status:
                log_event_async.delay({
                    'event_type': 'update_giftcard_public_giftcards',
                    'message': f"Gift card status changed: {self.code} from {old_status} to {self.status}",
                    'store_id': self.store.id,
                    'user_id': self.created_by.id if self.created_by else None,
                    'object_id': self.id,
                    'metadata': {
                        'code': self.code,
                        'old_status': old_status,
                        'new_status': self.status,
                        'current_balance': str(self.current_balance)
                    }
                })
            
            # Log balance changes
            if old_balance != self.current_balance:
                log_event_async.delay({
                    'event_type': 'update_giftcard_public_giftcards',
                    'message': f"Gift card balance changed: {self.code} from {old_balance} to {self.current_balance}",
                    'store_id': self.store.id,
                    'user_id': self.created_by.id if self.created_by else None,
                    'object_id': self.id,
                    'metadata': {
                        'code': self.code,
                        'old_balance': str(old_balance),
                        'new_balance': str(self.current_balance),
                        'status': self.status
                    }
                })


class GiftCardHistory(models.Model):
    """Gift card history model"""
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('sent', 'Sent'),
        ('redeemed', 'Redeemed'),
        ('refunded', 'Refunded'),
        ('expired', 'Expired'),
        ('voided', 'Voided'),
    ]

    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    gift_card = models.ForeignKey(GiftCard, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        app_label = 'giftcards'
        db_table = 'giftcards_gifthistory'
        ordering = ['-created_at']
        verbose_name_plural = 'Gift Card History'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            from apps.logs.tasks import log_event_async
            log_event_async.delay({
                'event_type': 'create_giftcardhistory_public_giftcards',
                'message': f"Gift card history created: {self.gift_card.code} - {self.action}",
                'store_id': self.store.id,
                'user_id': self.created_by.id if self.created_by else None,
                'object_id': self.id,
                'metadata': {
                    'gift_card_code': self.gift_card.code,
                    'action': self.action,
                    'amount': str(self.amount) if self.amount else None
                }
            })

    def __str__(self):
        return f"{self.gift_card.code} - {self.get_action_display()} - {self.amount if self.amount else ''}"
