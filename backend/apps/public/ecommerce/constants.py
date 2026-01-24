"""
Ecommerce constants for consistent status management.

As per 09-improvements.md: Consistent status management across all models.
"""

class StatusChoices:
    """Consistent status choices for all ecommerce models"""
    
    # Common statuses
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    FAILED = 'failed'
    
    # Product specific
    DRAFT = 'draft'
    ACTIVE = 'active'
    ARCHIVED = 'archived'
    
    # Order specific
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    REFUNDED = 'refunded'
    
    # Cart specific
    ACTIVE = 'active'
    ABANDONED = 'abandoned'
    CONVERTED = 'converted'
    
    # Payment specific
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    
    # Fulfillment specific
    UNFULFILLED = 'unfulfilled'
    PARTIAL = 'partial'
    FULFILLED = 'fulfilled'
    
    @classmethod
    def get_choices(cls):
        """Get all status choices"""
        return [
            (cls.PENDING, 'Pending'),
            (cls.CONFIRMED, 'Confirmed'),
            (cls.PROCESSING, 'Processing'),
            (cls.COMPLETED, 'Completed'),
            (cls.CANCELLED, 'Cancelled'),
            (cls.FAILED, 'Failed'),
            (cls.DRAFT, 'Draft'),
            (cls.ACTIVE, 'Active'),
            (cls.ARCHIVED, 'Archived'),
            (cls.SHIPPED, 'Shipped'),
            (cls.DELIVERED, 'Delivered'),
            (cls.REFUNDED, 'Refunded'),
            (cls.ABANDONED, 'Abandoned'),
            (cls.CONVERTED, 'Converted'),
            (cls.UNFULFILLED, 'Unfulfilled'),
            (cls.PARTIAL, 'Partial'),
            (cls.FULFILLED, 'Fulfilled'),
        ]
    
    @classmethod
    def get_product_choices(cls):
        """Get product-specific status choices"""
        return [
            (cls.DRAFT, 'Draft'),
            (cls.ACTIVE, 'Active'),
            (cls.ARCHIVED, 'Archived'),
        ]
    
    @classmethod
    def get_order_choices(cls):
        """Get order-specific status choices"""
        return [
            (cls.PENDING, 'Pending'),
            (cls.CONFIRMED, 'Confirmed'),
            (cls.PROCESSING, 'Processing'),
            (cls.SHIPPED, 'Shipped'),
            (cls.DELIVERED, 'Delivered'),
            (cls.CANCELLED, 'Cancelled'),
            (cls.REFUNDED, 'Refunded'),
        ]
    
    @classmethod
    def get_cart_choices(cls):
        """Get cart-specific status choices"""
        return [
            (cls.ACTIVE, 'Active'),
            (cls.ABANDONED, 'Abandoned'),
            (cls.CONVERTED, 'Converted'),
        ]
    
    @classmethod
    def get_payment_choices(cls):
        """Get payment-specific status choices"""
        return [
            (cls.PENDING, 'Pending'),
            (cls.PROCESSING, 'Processing'),
            (cls.COMPLETED, 'Completed'),
            (cls.FAILED, 'Failed'),
            (cls.REFUNDED, 'Refunded'),
        ]
    
    @classmethod
    def get_fulfillment_choices(cls):
        """Get fulfillment-specific status choices"""
        return [
            (cls.UNFULFILLED, 'Unfulfilled'),
            (cls.PARTIAL, 'Partial'),
            (cls.FULFILLED, 'Fulfilled'),
        ]


class ProductTypeChoices:
    """Product type choices"""
    
    PHYSICAL = 'physical'
    DIGITAL = 'digital'
    SERVICE = 'service'
    GIFT_CARD = 'gift_card'
    
    @classmethod
    def get_choices(cls):
        """Get product type choices"""
        return [
            (cls.PHYSICAL, 'Physical'),
            (cls.DIGITAL, 'Digital'),
            (cls.SERVICE, 'Service'),
            (cls.GIFT_CARD, 'Gift Card'),
        ]


class GenderChoices:
    """Gender choices for customer profiles"""
    
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'
    NOT_SPECIFIED = ''
    
    @classmethod
    def get_choices(cls):
        """Get gender choices"""
        return [
            (cls.MALE, 'Male'),
            (cls.FEMALE, 'Female'),
            (cls.OTHER, 'Other'),
            (cls.NOT_SPECIFIED, 'Not Specified'),
        ]


class InventoryPolicyChoices:
    """Inventory policy choices"""
    
    DENY = 'deny'
    CONTINUE = 'continue'
    
    @classmethod
    def get_choices(cls):
        """Get inventory policy choices"""
        return [
            (cls.DENY, 'Deny'),
            (cls.CONTINUE, 'Continue'),
        ]


# Default timeout values for caching and operations
CACHE_TIMEOUTS = {
    'short': 300,      # 5 minutes
    'medium': 3600,    # 1 hour
    'long': 86400,     # 24 hours
    'very_long': 604800,  # 7 days
}

# Default pagination sizes
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
