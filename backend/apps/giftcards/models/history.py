"""
GiftCardHistory model for giftcards app.
"""
from django.db import models
from django.utils import timezone
from core.models import TenantModel


class GiftCardHistory(TenantModel):
    """
    Store-scoped audit trail for all gift card transactions.
    """
    
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('activated', 'Activated'),
        ('redeemed', 'Redeemed'),
        ('refunded', 'Refunded'),
        ('expired', 'Expired'),
        ('voided', 'Voided'),
        ('updated', 'Updated'),
    ]
    
    # Relationships
    gift_card = models.ForeignKey(
        'giftcards.GiftCard', 
        on_delete=models.CASCADE, 
        related_name='history'
    )
    order = models.ForeignKey(
        'ecommerce.Order', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Transaction details
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta(TenantModel.Meta):
        db_table = 'giftcards_history'
        indexes = [
            models.Index(fields=['gift_card', 'action']),
            models.Index(fields=['gift_card', 'created_at']),
            models.Index(fields=['store', 'action']),
        ]
        ordering = ['-created_at']
        verbose_name_plural = 'Gift Card History'

    def __str__(self):
        return f"{self.gift_card.code} - {self.action} - {self.amount if self.amount else ''}"
