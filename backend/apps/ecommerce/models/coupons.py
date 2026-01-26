"""
Coupon models for ecommerce app.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid

User = get_user_model()


class CouponCampaign(models.Model):
    """
    Coupon campaign model for ecommerce.
    """
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('free_shipping', 'Free Shipping'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='coupon_campaigns')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Campaign settings
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Usage limits
    usage_limit_per_customer = models.PositiveIntegerField(null=True, blank=True)
    total_usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    
    # Date constraints
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ecommerce_coupon_campaign'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['store', 'is_active']),
            models.Index(fields=['starts_at', 'ends_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.discount_type})"
    
    @property
    def is_valid(self):
        """Check if campaign is currently valid"""
        now = timezone.now()
        return (
            self.is_active and
            self.starts_at <= now <= self.ends_at and
            (self.total_usage_limit is None or self.used_count < self.total_usage_limit)
        )
    
    def clean(self):
        """Validate campaign data"""
        if self.starts_at >= self.ends_at:
            raise ValidationError("End date must be after start date")
        
        if self.discount_type == 'percentage' and self.discount_value > 100:
            raise ValidationError("Percentage discount cannot exceed 100%")
        
        if self.discount_type == 'fixed' and self.discount_value < 0:
            raise ValidationError("Fixed discount cannot be negative")


class Coupon(models.Model):
    """
    Individual coupon model for ecommerce.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('used', 'Used'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(CouponCampaign, on_delete=models.CASCADE, related_name='coupons')
    code = models.CharField(max_length=50, unique=True)
    
    # Usage tracking
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='coupons')
    used_at = models.DateTimeField(null=True, blank=True)
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='coupons')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ecommerce_coupon'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['campaign', 'code']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"Coupon {self.code}"
    
    @property
    def is_usable(self):
        """Check if coupon can be used"""
        return (
            self.status == 'active' and
            self.campaign.is_valid and
            (self.customer is None or self.customer == self.customer)
        )
    
    def mark_as_used(self, customer, order):
        """Mark coupon as used"""
        self.customer = customer
        self.order = order
        self.used_at = timezone.now()
        self.status = 'used'
        self.save(update_fields=['customer', 'order', 'used_at', 'status'])
        
        # Update campaign usage count
        self.campaign.used_count += 1
        self.campaign.save(update_fields=['used_count'])
