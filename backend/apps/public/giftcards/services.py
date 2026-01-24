"""
Services for gift cards module.
"""
import logging
from datetime import timedelta
from django.db import transaction, models
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
import random
import string

logger = logging.getLogger(__name__)

class GiftCardService:
    """Service for gift card operations with comprehensive functionality"""
    
    # Cache timeout in seconds (5 minutes)
    CACHE_TIMEOUT = 300
    
    @classmethod
    def get_balance_cache_key(cls, code):
        """Get cache key for gift card balance"""
        return f"gift_card_balance_{code}"
    
    @classmethod
    def invalidate_balance_cache(cls, code):
        """Invalidate balance cache for a gift card"""
        cache.delete(cls.get_balance_cache_key(code))
    
    @staticmethod
    @transaction.atomic
    def create_gift_card(store, created_by, **kwargs):
        """
        Create a new gift card with validation and history logging
        
        Args:
            store: Store instance
            created_by: User who is creating the gift card
            **kwargs: Gift card attributes
            
        Returns:
            GiftCard: The created gift card instance
            
        Raises:
            ValidationError: If the gift card data is invalid
        """
        from .models import GiftCard, GiftCardHistory
        
        # Generate unique code if not provided
        code = kwargs.get('code') or GiftCardService._generate_code()
        
        # Set default expiration if not provided
        expires_at = kwargs.get('expires_at')
        if not expires_at and hasattr(settings, 'GIFT_CARD_DEFAULT_EXPIRY_DAYS'):
            expires_at = timezone.now() + timedelta(days=settings.GIFT_CARD_DEFAULT_EXPIRY_DAYS)
            kwargs['expires_at'] = expires_at
        
        # Create gift card using centralized service
        from core.services.base import BaseTenantCRUDService
        
        gift_card = BaseTenantCRUDService.create(
            store=store,
            code=code,
            created_by=created_by,
            **{k: v for k, v in kwargs.items() if k != 'code'}
        )
        
        # Log creation using centralized service
        BaseTenantCRUDService.create(
            gift_card=gift_card,
            action='created',
            amount=gift_card.initial_balance,
            created_by=created_by,
            metadata={
                'initial_balance': str(gift_card.initial_balance),
                'expires_at': gift_card.expires_at.isoformat() if gift_card.expires_at else None
            }
        )
        
        logger.info(f"Created gift card {gift_card.code} for store {store.id}")
        return gift_card
    
    @classmethod
    @transaction.atomic
    def redeem_gift_card(cls, code, amount, user=None, order=None, method='online'):
        """
        Redeem a gift card
        
        Args:
            code: Gift card code
            amount: Amount to redeem
            user: User performing the redemption (optional)
            order: Associated order (optional)
            method: Redemption method (default: 'online')
            
        Returns:
            GiftCard: The updated gift card instance
            
        Raises:
            ValidationError: If the gift card is not redeemable or has insufficient balance
        """
        from .models import GiftCard, GiftCardHistory
        
        try:
            from core.services.base import BaseTenantCRUDService
            gift_card = BaseTenantCRUDService.get(
                code=code, 
                status='active'
            )
            
            if not gift_card.is_redeemable():
                raise ValidationError("Gift card is not redeemable (may be expired or inactive)")
                
            if amount <= 0:
                raise ValidationError("Amount must be greater than zero")
                
            if amount > gift_card.current_balance:
                raise ValidationError(
                    f"Insufficient balance. Available: {gift_card.current_balance}"
                )
            
            # Update balance
            gift_card.current_balance -= amount
            if gift_card.current_balance == 0:
                gift_card.status = 'redeemed'
            gift_card.save()
            
            # Log redemption using centralized service
            from core.services.base import BaseTenantCRUDService
            BaseTenantCRUDService.create(
                gift_card=gift_card,
                action='redeemed',
                amount=amount,
                order=order,
                created_by=user,
                metadata={
                    'method': method,
                    'order_id': str(order.id) if order else None,
                    'remaining_balance': str(gift_card.current_balance)
                }
            )
            
            # Invalidate balance cache
            cls.invalidate_balance_cache(gift_card.code)
            
            logger.info(
                f"Redeemed {amount} from gift card {gift_card.code}. "
                f"Remaining balance: {gift_card.current_balance}"
            )
            
            return gift_card
            
        except GiftCard.DoesNotExist:
            logger.warning(f"Attempted to redeem non-existent or inactive gift card: {code}")
            raise ValidationError("Invalid or inactive gift card code")
    
    @classmethod
    def get_gift_card_balance(cls, code, use_cache=True):
        """
        Get current balance of a gift card with optional caching
        
        Args:
            code: Gift card code
            use_cache: Whether to use cache (default: True)
            
        Returns:
            dict: Balance information or None if not found
        """
        from .models import GiftCard
        
        cache_key = cls.get_balance_cache_key(code)
        
        # Try to get from cache first
        if use_cache:
            cached_balance = cache.get(cache_key)
            if cached_balance is not None:
                return cached_balance
        
        try:
            from core.services.base import BaseTenantCRUDService
            gift_card = BaseTenantCRUDService.get(code=code, status='active')
            balance_data = {
                'code': gift_card.code,
                'balance': str(gift_card.current_balance),
                'currency': gift_card.currency,
                'is_expired': gift_card.is_expired(),
                'expires_at': gift_card.expires_at.isoformat() if gift_card.expires_at else None
            }
            
            # Cache the result
            cache.set(cache_key, balance_data, timeout=cls.CACHE_TIMEOUT)
            
            return balance_data
            
        except GiftCard.DoesNotExist:
            return None
    
    @classmethod
    @transaction.atomic
    def activate_gift_card(cls, gift_card, activated_by, expires_at=None, notes=None):
        """
        Activate a gift card
        
        Args:
            gift_card: GiftCard instance to activate
            activated_by: User performing the activation
            expires_at: Optional expiration date (defaults to settings.GIFT_CARD_DEFAULT_EXPIRY_DAYS)
            notes: Optional notes for the history entry
            
        Returns:
            GiftCard: The activated gift card
            
        Raises:
            ValidationError: If the gift card cannot be activated
        """
        from .models import GiftCardHistory
        
        if gift_card.status != 'active':
            gift_card.status = 'active'
            
            if expires_at:
                gift_card.expires_at = expires_at
            elif not gift_card.expires_at and hasattr(settings, 'GIFT_CARD_DEFAULT_EXPIRY_DAYS'):
                gift_card.expires_at = timezone.now() + timedelta(
                    days=settings.GIFT_CARD_DEFAULT_EXPIRY_DAYS
                )
            
            gift_card.save()
            
            # Log activation using centralized service
            from core.services.base import BaseTenantCRUDService
            BaseTenantCRUDService.create(
                gift_card=gift_card,
                action='activated',
                created_by=activated_by,
                notes=notes,
                metadata={
                    'expires_at': gift_card.expires_at.isoformat() if gift_card.expires_at else None
                }
            )
            
            # Invalidate cache
            cls.invalidate_balance_cache(gift_card.code)
            
            logger.info(f"Activated gift card {gift_card.code}")
        
        return gift_card
    
    @classmethod
    @transaction.atomic
    def void_gift_card(cls, gift_card, voided_by, reason, notes=None):
        """
        Void a gift card
        
        Args:
            gift_card: GiftCard instance to void
            voided_by: User performing the void
            reason: Reason for voiding
            notes: Optional additional notes
            
        Returns:
            GiftCard: The voided gift card
            
        Raises:
            ValidationError: If the gift card cannot be voided
        """
        from .models import GiftCardHistory
        
        if gift_card.status != 'voided':
            previous_status = gift_card.status
            gift_card.status = 'voided'
            gift_card.save()
            
            # Log void using centralized service
            from core.services.base import BaseTenantCRUDService
            BaseTenantCRUDService.create(
                gift_card=gift_card,
                action='voided',
                created_by=voided_by,
                notes=notes,
                metadata={
                    'previous_status': previous_status,
                    'reason': reason
                }
            )
            
            # Invalidate cache
            cls.invalidate_balance_cache(gift_card.code)
            
            logger.info(f"Voided gift card {gift_card.code}. Reason: {reason}")
        
        return gift_card
    
    @classmethod
    def expire_gift_cards(cls):
        """
        Expire gift cards that have passed their expiration date
        
        Returns:
            tuple: (expired_count, error_count)
        """
        from core.services.base import BaseTenantCRUDService
        from .models import GiftCard, GiftCardHistory
        from django.utils import timezone
        
        now = timezone.now()
        BaseTenantCRUDService.model_class = GiftCard
        expired_cards = BaseTenantCRUDService.filter(
            status='active',
            expires_at__lte=now
        )
        
        expired_count = 0
        error_count = 0
        
        for card in expired_cards:
            try:
                with transaction.atomic():
                    card.status = 'expired'
                    card.save()
                    
                    # Log expiration using centralized service
                    BaseTenantCRUDService.model_class = GiftCardHistory
                    BaseTenantCRUDService.create(
                        gift_card=card,
                        action='expired',
                        metadata={'expired_at': now.isoformat()}
                    )
                    
                    cls.invalidate_balance_cache(card.code)
                    expired_count += 1
                    
                    logger.info(f"Expired gift card {card.code}")
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error expiring gift card {card.code}: {str(e)}")
        
        return expired_count, error_count
    
    @classmethod
    def get_gift_card_analytics(cls, store, start_date=None, end_date=None):
        """
        Generate analytics for gift cards
        
        Args:
            store: Store to get analytics for
            start_date: Start date for the period (optional)
            end_date: End date for the period (defaults to now)
            
        Returns:
            dict: Analytics data
        """
        from core.services.base import GiftCardQueryHelper
        return GiftCardQueryHelper.get_store_analytics(store, start_date, end_date)
    
    @staticmethod
    def _generate_code(length=None):
        """
        Generate a random gift card code
        
        Args:
            length: Length of the code (defaults to GIFT_CARD_CODE_LENGTH setting or 12)
            
        Returns:
            str: Generated code
        """
        if length is None:
            length = getattr(settings, 'GIFT_CARD_CODE_LENGTH', 12)
        
        # Use custom character set if defined in settings
        chars = getattr(settings, 'GIFT_CARD_CODE_CHARS', 
                       string.ascii_uppercase + string.digits)
        
        # Add prefix if defined
        prefix = getattr(settings, 'GIFT_CARD_CODE_PREFIX', '')
        
        # Generate random code
        code = prefix + ''.join(random.choices(chars, k=length - len(prefix)))
        
        return code
    
    @staticmethod
    def validate_gift_card_data(store, **kwargs):
        """
        Validate gift card data before creation
        
        Args:
            store: Store instance
            **kwargs: Gift card data to validate
            
        Returns:
            dict: Validation result with errors if any
        """
        errors = {}
        
        # Validate amount
        initial_balance = kwargs.get('initial_balance')
        if initial_balance is None:
            errors['initial_balance'] = 'Initial balance is required'
        elif initial_balance <= 0:
            errors['initial_balance'] = 'Initial balance must be greater than 0'
        else:
            min_amount = getattr(settings, 'GIFT_CARD_MIN_AMOUNT', 10.00)
            max_amount = getattr(settings, 'GIFT_CARD_MAX_AMOUNT', 1000.00)
            
            if initial_balance < min_amount:
                errors['initial_balance'] = f'Minimum amount is ${min_amount}'
            elif initial_balance > max_amount:
                errors['initial_balance'] = f'Maximum amount is ${max_amount}'
        
        # Validate currency
        currency = kwargs.get('currency', 'USD')
        allowed_currencies = getattr(settings, 'GIFT_CARD_ALLOWED_CURRENCIES', ['USD'])
        if currency not in allowed_currencies:
            errors['currency'] = f'Currency must be one of: {", ".join(allowed_currencies)}'
        
        # Validate gift card type
        gift_card_type = kwargs.get('gift_card_type', 'digital')
        valid_types = [choice[0] for choice in GiftCard.GIFT_CARD_TYPES]
        if gift_card_type not in valid_types:
            errors['gift_card_type'] = f'Type must be one of: {", ".join(valid_types)}'
        
        # Validate expiration
        expires_at = kwargs.get('expires_at')
        if expires_at and expires_at <= timezone.now():
            errors['expires_at'] = 'Expiration date must be in the future'
        
        # Validate code uniqueness if provided
        code = kwargs.get('code')
        if code:
            from core.services.base import BaseTenantCRUDService
            BaseTenantCRUDService.model_class = GiftCard
            if BaseTenantCRUDService.filter(code=code).exists():
                errors['code'] = 'Gift card code already exists'
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    @staticmethod
    def bulk_create_gift_cards(store, created_by, gift_cards_data):
        """
        Create multiple gift cards in bulk
        
        Args:
            store: Store instance
            created_by: User creating the gift cards
            gift_cards_data: List of gift card data dictionaries
            
        Returns:
            dict: Results with created gift cards and any errors
        """
        results = {'created': [], 'errors': []}
        
        for i, card_data in enumerate(gift_cards_data):
            try:
                # Validate each card
                validation = GiftCardService.validate_gift_card_data(store, **card_data)
                if not validation['valid']:
                    results['errors'].append({
                        'index': i,
                        'data': card_data,
                        'errors': validation['errors']
                    })
                    continue
                
                # Create the gift card
                gift_card = GiftCardService.create_gift_card(store, created_by, **card_data)
                results['created'].append(gift_card)
                
            except Exception as e:
                results['errors'].append({
                    'index': i,
                    'data': card_data,
                    'error': str(e)
                })
        
        return results
    
    @staticmethod
    def get_gift_card_by_code(code, store=None):
        """
        Get gift card by code with optional store filtering
        
        Args:
            code: Gift card code
            store: Optional store to filter by
            
        Returns:
            GiftCard or None
        """
        from core.services.base import BaseTenantCRUDService
        BaseTenantCRUDService.model_class = GiftCard
        
        filters = {'code': code}
        if store:
            filters['store'] = store
        
        try:
            return BaseTenantCRUDService.get(**filters)
        except:
            return None
    
    @staticmethod
    def update_gift_card_balance(gift_card, amount_change, user=None, reason=None):
        """
        Update gift card balance with validation and history logging
        
        Args:
            gift_card: GiftCard instance
            amount_change: Amount to add (positive) or subtract (negative)
            user: User making the change
            reason: Reason for the change
            
        Returns:
            GiftCard: Updated gift card
        """
        from core.services.base import BaseTenantCRUDService
        
        if amount_change == 0:
            raise ValidationError("Amount change cannot be zero")
        
        new_balance = gift_card.current_balance + amount_change
        
        if new_balance < 0:
            raise ValidationError("Insufficient balance for this operation")
        
        if new_balance > gift_card.initial_balance * 2:  # Prevent overloading
            raise ValidationError("Balance exceeds maximum allowed limit")
        
        # Update balance
        old_balance = gift_card.current_balance
        gift_card.current_balance = new_balance
        
        # Update status if needed
        if new_balance == 0 and gift_card.status == 'active':
            gift_card.status = 'redeemed'
        elif new_balance > 0 and gift_card.status == 'redeemed':
            gift_card.status = 'active'
        
        gift_card.save()
        
        # Log the balance change
        action = 'balance_added' if amount_change > 0 else 'balance_subtracted'
        BaseTenantCRUDService.model_class = GiftCardHistory
        BaseTenantCRUDService.create(
            gift_card=gift_card,
            action=action,
            amount=abs(amount_change),
            created_by=user,
            notes=reason,
            metadata={
                'old_balance': str(old_balance),
                'new_balance': str(new_balance),
                'change': str(amount_change)
            }
        )
        
        # Invalidate cache
        GiftCardService.invalidate_balance_cache(gift_card.code)
        
        return gift_card
