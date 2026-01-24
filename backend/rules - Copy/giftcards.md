# Gift Cards Module

## Overview
The Gift Cards module provides a comprehensive system for managing digital and physical gift cards, supporting multiple types, redemption flows, and deep e-commerce integration. This document outlines the architecture, models, services, and APIs required to implement this functionality.

## Table of Contents
1. [Architecture](#architecture)
2. [Models](#models)
3. [Services](#services)
4. [API Endpoints](#api-endpoints)
5. [Email Templates](#email-templates)
6. [Analytics](#analytics)
7. [E-commerce Integration](#e-commerce-integration)
8. [Security](#security)
9. [Performance](#performance)
10. [Testing](#testing)
11. [Deployment](#deployment)

## Architecture

### Key Components
- **GiftCard**: Core model representing a gift card with balance, status, and metadata
- **GiftCardHistory**: Audit trail for all gift card transactions
- **GiftCardService**: Business logic for gift card operations
- **GiftCardViewSet**: REST API endpoints
- **GiftCardEmailService**: Handles gift card email notifications
- **GiftCardAnalytics**: Tracks and reports on gift card usage

### Dependencies
- `ecommerce` for order integration
- `smtp` for email notifications
- `accounts` for user management
- `logs` for audit trails

## Models

### GiftCard
```python
class GiftCard(TenantModel):
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
    
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    initial_balance = models.DecimalField(max_digits=10, decimal_places=2)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    gift_card_type = models.CharField(max_length=20, choices=GIFT_CARD_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    expires_at = models.DateTimeField(null=True, blank=True)
    sender_name = models.CharField(max_length=100, blank=True)
    sender_email = models.EmailField(blank=True)
    recipient_name = models.CharField(max_length=100, blank=True)
    recipient_email = models.EmailField(blank=True)
    message = models.TextField(blank=True)
    metadata = JSONField(default=dict, blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
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
```

### GiftCardHistory
```python
class GiftCardHistory(TenantModel):
    ACTION_CHOICES = (
        ('created', 'Created'),
        ('sent', 'Sent'),
        ('redeemed', 'Redeemed'),
        ('refunded', 'Refunded'),
        ('expired', 'Expired'),
        ('voided', 'Voided'),
    )
    
    gift_card = models.ForeignKey(GiftCard, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    order = models.ForeignKey('ecommerce.Order', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    metadata = JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Gift Card History'
    
    def __str__(self):
        return f"{self.gift_card.code} - {self.get_action_display()} - {self.amount if self.amount else ''}"
```

## Services

### GiftCardService
```python
class GiftCardService:
    @staticmethod
    @transaction.atomic
    def create_gift_card(store, created_by, **kwargs):
        """
        Create a new gift card with validation and history logging
        """
        # Generate unique code
        code = kwargs.get('code') or GiftCardService._generate_code()
        
        # Create gift card
        gift_card = GiftCard.objects.create(
            store=store,
            code=code,
            created_by=created_by,
            **{k: v for k, v in kwargs.items() if k != 'code'}
        )
        
        # Log creation
        GiftCardHistory.objects.create(
            gift_card=gift_card,
            action='created',
            amount=gift_card.initial_balance,
            created_by=created_by
        )
        
        return gift_card
    
    @staticmethod
    @transaction.atomic
    def redeem_gift_card(code, amount, user=None, order=None, method='online'):
        """
        Redeem a gift card
        """
        try:
            gift_card = GiftCard.objects.get(code=code, status='active')
            
            if not gift_card.is_redeemable():
                raise ValidationError("Gift card is not redeemable")
                
            if amount > gift_card.current_balance:
                raise ValidationError("Insufficient balance")
            
            # Update balance
            gift_card.current_balance -= amount
            if gift_card.current_balance == 0:
                gift_card.status = 'redeemed'
            gift_card.save()
            
            # Log redemption
            GiftCardHistory.objects.create(
                gift_card=gift_card,
                action='redeemed',
                amount=amount,
                order=order,
                created_by=user,
                metadata={'method': method}
            )
            
            return gift_card
            
        except GiftCard.DoesNotExist:
            raise ValidationError("Invalid gift card code")
    
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
        # Implementation for analytics
        pass
```

## API Endpoints

### Base URL: `/api/v2/gift-cards/`

#### List/Search Gift Cards (GET)
- **Permissions**: `IsAuthenticated`, `IsStoreUser`
- **Query Params**:
  - `status`: Filter by status (active, redeemed, expired, voided)
  - `gift_card_type`: Filter by type (digital, physical, etc.)
  - `search`: Search by code, recipient name, or email
  - `expires_before`: Filter by expiration date
  - `ordering`: Sort field (-created_at, current_balance, etc.)

#### Create Gift Card (POST)
- **Permissions**: `IsAuthenticated`, `IsStoreUser`
- **Request Body**:
  ```json
  {
    "gift_card_type": "digital",
    "initial_balance": 100.00,
    "currency": "USD",
    "expires_at": "2024-12-31T23:59:59Z",
    "recipient_name": "John Doe",
    "recipient_email": "john@example.com",
    "message": "Enjoy your gift!",
    "metadata": {}
  }
  ```

#### Gift Card Detail (GET /{code})
- **Permissions**: `IsAuthenticated`, `IsStoreUser`
- **Response**:
  ```json
  {
    "code": "ABC123XYZ456",
    "gift_card_type": "digital",
    "initial_balance": "100.00",
    "current_balance": "100.00",
    "currency": "USD",
    "status": "active",
    "expires_at": "2024-12-31T23:59:59Z",
    "recipient_name": "John Doe",
    "recipient_email": "john@example.com",
    "created_at": "2023-01-15T10:30:00Z",
    "history": [
      {
        "action": "created",
        "amount": "100.00",
        "created_at": "2023-01-15T10:30:00Z"
      }
    ]
  }
  ```

#### Redeem Gift Card (POST /{code}/redeem)
- **Permissions**: `IsAuthenticated` (for online) or API key (for in-store)
- **Request Body**:
  ```json
  {
    "amount": 25.50,
    "order_id": "ORD-12345",
    "method": "online" // or "in_store"
  }
  ```

## Email Templates

### Gift Card Purchased
- **Trigger**: When a new gift card is purchased
- **Recipients**: Sender (confirmation) and Recipient (gift card)
- **Variables**:
  - `gift_card_code`
  - `recipient_name`
  - `sender_name`
  - `message`
  - `amount`
  - `expiration_date`
  - `redeem_url`

### Gift Card Redeemed
- **Trigger**: When a gift card is used
- **Recipients**: Sender (notification)
- **Variables**:
  - `gift_card_code`
  - `amount_used`
  - `remaining_balance`
  - `order_id`
  - `redemption_date`

## Analytics

### Key Metrics
1. **Redemption Rate**: Percentage of issued gift cards that have been redeemed
2. **Breakage**: Value of unredeemed gift cards
3. **Average Order Value (AOV)**: For orders using gift cards
4. **Popular Gift Card Types**: Distribution across different types
5. **Time to Redemption**: Average time between issuance and first use

### Sample Queries
```python
# Redemption rate
total_issued = GiftCard.objects.filter(store=store).count()
redeemed = GiftCard.objects.filter(store=store, status='redeemed').count()
redemption_rate = (redeemed / total_issued) * 100 if total_issued > 0 else 0

# Breakage
breakage = GiftCard.objects.filter(
    store=store, 
    status='active',
    expires_at__lt=timezone.now()
).aggregate(total=Sum('current_balance'))['total'] or 0

# Average Order Value with Gift Cards
from django.db.models import Avg, F
orders_with_gift_cards = Order.objects.filter(
    store=store,
    gift_card_history__isnull=False
).annotate(
    gift_card_total=Sum('gift_card_history__amount')
).aggregate(
    avg_order_value=Avg(F('total') + F('gift_card_total'))
)
```

## E-commerce Integration

### Cart Application Flow
1. Customer applies gift card code to cart
2. System validates code and checks balance
3. If valid, apply discount to order total
4. Store gift card usage in session until checkout

### Order Processing
1. On order completion, redeem gift card amount
2. Create GiftCardHistory entry linked to order
3. Update gift card balance
4. Send redemption confirmation if balance remains

### Refunds
1. If order is refunded, optionally refund amount to gift card
2. Create new gift card with refunded amount
3. Link to original order for tracking

## Security

### Rate Limiting
- 5 redemption attempts per minute per IP
- 10 gift card lookups per minute per user

### Validation
- Validate gift card codes against regex pattern
- Prevent duplicate codes
- Enforce minimum/maximum gift card values

### Access Control
- Store staff can view all gift cards
- Customers can only view their own gift cards
- API keys required for in-store redemption

## Performance

### Caching
- Cache gift card balances for 5 minutes
- Cache gift card validation results for 1 minute
- Use cache stampede protection

### Database Optimization
- Index on code, status, expires_at
- Select related for common queries
- Use `only()` and `defer()` to limit field selection

### Background Tasks
- Send emails asynchronously
- Process batch operations in background
- Schedule expiration checks

## Testing

### Unit Tests
- Gift card creation and validation
- Balance calculations
- Expiration logic
- Redemption scenarios

### Integration Tests
- API endpoints
- E-commerce flow
- Email delivery
- Concurrent redemptions

### Performance Tests
- Load testing for high-volume redemption
- Stress testing for concurrent access

## Deployment

### Migrations
```python
# 0001_initial.py
class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('ecommerce', '0001_initial'),
        ('accounts', '0001_initial'),
        ('stores', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GiftCard',
            fields=[
                # Model fields
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['code'], name='giftcards_g_code_123456_idx'),
                    models.Index(fields=['status'], name='giftcards_g_status_123456_idx'),
                    models.Index(fields=['expires_at'], name='giftcards_g_expires_123456_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='GiftCardHistory',
            fields=[
                # Model fields
            ],
            options={
                'ordering': ['-created_at'],
                'verbose_name_plural': 'Gift Card History',
            },
        ),
    ]
```

### Required Environment Variables
```bash
# Gift card settings
GIFT_CARD_CODE_LENGTH=12
GIFT_CARD_CODE_PREFIX=GC
GIFT_CARD_EXPIRY_DAYS=365
GIFT_CARD_MIN_AMOUNT=10.00
GIFT_CARD_MAX_AMOUNT=1000.00
```

### Monitoring
- Track gift card creation and redemption rates
- Monitor for failed redemption attempts
- Alert on suspicious activity

## Implementation Checklist

### Phase 1: Core Functionality
- [ ] Create GiftCard and GiftCardHistory models
- [ ] Implement GiftCardService with basic CRUD operations
- [ ] Create API endpoints for gift card management
- [ ] Add unit tests for core functionality

### Phase 2: E-commerce Integration
- [ ] Integrate with cart/checkout flow
- [ ] Implement order processing hooks
- [ ] Add refund handling
- [ ] Create integration tests

### Phase 3: Email & Notifications
- [ ] Design email templates
- [ ] Implement email sending
- [ ] Add notification preferences

### Phase 4: Analytics & Reporting
- [ ] Implement analytics queries
- [ ] Create admin reports
- [ ] Set up monitoring

### Phase 5: Optimization
- [ ] Add caching
- [ ] Optimize database queries
- [ ] Implement background tasks

## Future Enhancements
1. Bulk import/export of gift cards
2. Gift card categories with different rules
3. Scheduled gift card delivery
4. Multi-currency support
5. Gift card marketplaces
6. Loyalty program integration
