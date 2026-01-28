# Giftcards Rules v1.0

## 🎯 Purpose
This document defines strict development rules for the **giftcards** app in CMS-Updated backend, implementing a comprehensive gift card management system supporting digital and physical cards, redemption flows, and deep e-commerce integration.

---

## 🏗️ Structure
### **Fixed Directory Structure**
```
apps/
├── public/                    # Public APIs (no authentication)
│   └── giftcards/           # Public gift card APIs
│       ├── v2/               # Version 2 (Current Only)
│       │   ├── urls.py
│       │   ├── views.py
│       │   ├── serializers.py
│       │   └── tests.py
│       ├── models/             # Shared models across versions
│       │   ├── __init__.py
│       │   ├── gift_card.py     # GiftCard model
│       │   └── history.py     # GiftCardHistory model
│       ├── services.py
│       └── admin.py
├── customer/                  # Customer APIs (customer authentication)
│   └── giftcards/           # Customer gift card APIs
│       ├── v2/               # Version 2 (Current Only)
│       │   ├── urls.py
│       │   ├── views.py
│       │   ├── serializers.py
│       │   └── tests.py
│       └── models/             # Same shared models
└── dashboard/                 # Dashboard APIs (admin authentication)
    └── giftcards/           # Dashboard gift card APIs
        ├── v2/               # Version 2 (Current Only)
        │   ├── urls.py
        │   ├── views.py
        │   ├── serializers.py
        │   └── tests.py
        └── models/             # Same shared models
```

---

## 🔧 Implementation
### **GiftCard Model**
```python
# apps/public/giftcards/models/gift_card.py
from django.db import models
from django.utils import timezone
from core.models import TenantModel

class GiftCard(TenantModel):
    """Store-scoped gift card with balance and status tracking"""

    GIFT_CARD_TYPES = (
        ('digital', 'Digital'),
        ('physical', 'Physical'),
        ('promotional', 'Promotional'),
        ('refund', 'Refund'),
        ('loyalty', 'Loyalty'),
    )

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('redeemed', 'Redeemed'),
        ('expired', 'Expired'),
        ('voided', 'Voided'),
    )

    # Core fields
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    initial_balance = models.DecimalField(max_digits=10, decimal_places=2)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    gift_card_type = models.CharField(max_length=20, choices=GIFT_CARD_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Timing
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Sender/Recipient info
    sender_name = models.CharField(max_length=100, blank=True)
    sender_email = models.EmailField(blank=True)
    recipient_name = models.CharField(max_length=100, blank=True)
    recipient_email = models.EmailField(blank=True)
    message = models.TextField(blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)

    class Meta(TenantModel.Meta):
        db_table = 'giftcards_gift_card'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['status']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['store', 'status']),
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
```

### **GiftCardHistory Model**
```python
# apps/public/giftcards/models/history.py
from django.db import models
from core.models import TenantModel

class GiftCardHistory(TenantModel):
    """Audit trail for all gift card transactions"""

    ACTION_CHOICES = (
        ('created', 'Created'),
        ('sent', 'Sent'),
        ('redeemed', 'Redeemed'),
        ('refunded', 'Refunded'),
        ('expired', 'Expired'),
        ('voided', 'Voided'),
    )

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
        'accounts.User',
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

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta(TenantModel.Meta):
        db_table = 'giftcards_history'
        ordering = ['-created_at']
        verbose_name_plural = 'Gift Card History'

    def __str__(self):
        return f"{self.gift_card.code} - {self.get_action_display()} - {self.amount if self.amount else ''}"
```

---

## 🔒 Permissions
### **Access Control**
- **Store Owners**: Full CRUD on all gift cards
- **Staff**: Read-only access to gift cards
- **Customers**: Can only view their own gift cards
- **Public**: Limited gift card balance checking

### **Validation Rules**
- Gift card codes must match regex pattern
- Prevent duplicate codes
- Enforce minimum/maximum gift card values
- Rate limiting for redemption attempts

---

## 🧪 Testing
### **Unit Tests**
```python
# apps/giftcards/tests/test_models.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from ..models import GiftCard, GiftCardHistory

class GiftCardTests(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', slug='test-store')
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

    def test_gift_card_creation(self):
        """Test creating a gift card"""
        gift_card = GiftCard.objects.create(
            store=self.store,
            code='TEST123XYZ456',
            initial_balance=100.00,
            current_balance=100.00,
            gift_card_type='digital',
            created_by=self.user
        )

        self.assertEqual(gift_card.code, 'TEST123XYZ456')
        self.assertEqual(gift_card.current_balance, 100.00)
        self.assertTrue(gift_card.is_redeemable())

    def test_gift_card_redemption(self):
        """Test gift card redemption"""
        gift_card = GiftCard.objects.create(
            store=self.store,
            code='TEST123XYZ456',
            initial_balance=100.00,
            current_balance=100.00,
            created_by=self.user
        )

        # Redeem 25.00
        gift_card.current_balance = 75.00
        gift_card.save()

        # Create history entry
        GiftCardHistory.objects.create(
            gift_card=gift_card,
            action='redeemed',
            amount=25.00,
            created_by=self.user
        )

        self.assertEqual(gift_card.current_balance, 75.00)
        self.assertEqual(gift_card.history.count(), 1)
```

---

## ⚙️ Services
### **GiftCardService**
```python
# apps/public/giftcards/services.py
from django.db import transaction
from django.core.exceptions import ValidationError
import string
import random

class GiftCardService:
    """Business logic for gift card operations"""

    @staticmethod
    @transaction.atomic
    def create_gift_card(store, created_by, **kwargs):
        """Create a new gift card with validation"""
        # Generate unique code if not provided
        code = kwargs.get('code') or GiftCardService._generate_code()

        # Validate balance
        initial_balance = kwargs.get('initial_balance', 0)
        if initial_balance < 10.00:
            raise ValidationError("Minimum gift card amount is $10.00")
        if initial_balance > 1000.00:
            raise ValidationError("Maximum gift card amount is $1,000.00")

        # Create gift card
        gift_card = GiftCard.objects.create(
            store=store,
            code=code,
            initial_balance=initial_balance,
            current_balance=initial_balance,
            created_by=created_by,
            **{k: v for k, v in kwargs.items() if k != 'code'}
        )

        # Log creation
        GiftCardHistory.objects.create(
            gift_card=gift_card,
            action='created',
            amount=initial_balance,
            created_by=created_by
        )

        return gift_card

    @staticmethod
    @transaction.atomic
    def redeem_gift_card(code, amount, user=None, order=None, method='online'):
        """Redeem a gift card"""
        try:
            gift_card = GiftCard.objects.get(code=code, status='active')
        except GiftCard.DoesNotExist:
            raise ValidationError("Invalid gift card code")

        if gift_card.is_expired():
            raise ValidationError("Gift card has expired")

        if amount > gift_card.current_balance:
            raise ValidationError("Insufficient balance")

        # Update balance
        gift_card.current_balance -= amount
        gift_card.save()

        # Create history entry
        GiftCardHistory.objects.create(
            gift_card=gift_card,
            action='redeemed',
            amount=amount,
            order=order,
            created_by=user
        )

        return gift_card

    @staticmethod
    def get_gift_card_balance(code):
        """Get current balance of a gift card"""
        try:
            gift_card = GiftCard.objects.get(code=code, status='active')
            return {
                'code': gift_card.code,
                'balance': gift_card.current_balance,
                'currency': gift_card.currency,
                'is_expired': gift_card.is_expired()
            }
        except GiftCard.DoesNotExist:
            return None

    @staticmethod
    def _generate_code(length=12):
        """Generate a random gift card code"""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=length))

    @staticmethod
    def get_gift_card_analytics(store, start_date=None, end_date=None):
        """Generate analytics for gift cards"""
        from .models import GiftCard, GiftCardHistory

        queryset = GiftCard.objects.filter(store=store)

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        # Calculate metrics
        total_issued = queryset.count()
        redeemed = queryset.filter(status='redeemed').count()
        active = queryset.filter(status='active').count()

        redemption_rate = (redeemed / total_issued * 100) if total_issued > 0 else 0

        # Breakage calculation
        breakage = GiftCard.objects.filter(
            store=store,
            status='active',
            expires_at__lt=timezone.now()
        ).aggregate(total=models.Sum('current_balance'))['total'] or 0

        return {
            'total_issued': total_issued,
            'redeemed': redeemed,
            'active': active,
            'redemption_rate': redemption_rate,
            'breakage': breakage,
            'total_value': queryset.aggregate(
                total=models.Sum('initial_balance')
            )['total'] or 0
        }
```

---

## 🔗 Dependencies
```tree
[Related components with @path references]
```
- ecommerce.md for order integration
- smtp.md for email notifications
- accounts.md for user management
- logs.md for audit trails
- core.md for base models and utilities

---

## 📋 Migration
### **From Legacy Gift Card System**
```python
# apps/giftcards/management/commands/migrate_giftcards.py
from django.core.management.base import BaseCommand
from django.db import transaction

class Command(BaseCommand):
    help = 'Migrate legacy gift cards to new structure'

    def handle(self, *args, **options):
        from apps.legacy.models import LegacyGiftCard
        from .models import GiftCard, GiftCardHistory

        with transaction.atomic():
            for legacy_card in LegacyGiftCard.objects.all():
                # Create new gift card
                gift_card = GiftCard.objects.create(
                    store=legacy_card.store,
                    code=legacy_card.code,
                    initial_balance=legacy_card.balance,
                    current_balance=legacy_card.balance,
                    gift_card_type=legacy_card.type,
                    status=legacy_card.status,
                    expires_at=legacy_card.expires_at,
                    created_by=legacy_card.created_by
                )

                # Migrate history
                for legacy_history in legacy_card.history.all():
                    GiftCardHistory.objects.create(
                        gift_card=gift_card,
                        action=legacy_history.action,
                        amount=legacy_history.amount,
                        order=legacy_history.order,
                        notes=legacy_history.notes,
                        created_at=legacy_history.created_at,
                        created_by=legacy_history.created_by
                    )

        self.stdout.write(self.style.SUCCESS('Migration completed'))
```

---

## ✅ Benefits
- ✅ **Multi-tenant**: Store-scoped gift card management
- ✅ **Flexible Types**: Digital, physical, promotional, refund, loyalty cards
- ✅ **E-commerce Integration**: Deep cart and checkout integration
- ✅ **Audit Trail**: Complete history tracking
- ✅ **Email Notifications**: Automated gift card delivery
- ✅ **Analytics**: Comprehensive reporting and metrics
- ✅ **Security**: Rate limiting and validation
- ✅ **Performance**: Optimized with caching and indexing

---

**Version**: 1.0
**Last Updated**: 2026-01-26
**Next Review**: 2026-02-25
