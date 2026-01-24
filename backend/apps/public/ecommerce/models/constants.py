"""
Constants for ecommerce models.
"""


class StatusChoices:
    """Common status choices for ecommerce models"""
    
    # Cart/Order Status
    PENDING = 'pending'
    ACTIVE = 'active'
    ABANDONED = 'abandoned'
    EXPIRED = 'expired'
    CONFIRMED = 'confirmed'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'
    FAILED = 'failed'
    FULFILLED = 'fulfilled'
    UNFULFILLED = 'unfulfilled'
    
    CART_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACTIVE, 'Active'),
        (ABANDONED, 'Abandoned'),
        (EXPIRED, 'Expired'),
    ]
    
    ORDER_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (PROCESSING, 'Processing'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
        (REFUNDED, 'Refunded'),
        (FAILED, 'Failed'),
        (FULFILLED, 'Fulfilled'),
    ]
    
    # Payment Status
    PAYMENT_PENDING = 'payment_pending'
    PAYMENT_PROCESSING = 'payment_processing'
    PAID = 'paid'
    PAYMENT_FAILED = 'payment_failed'
    REFUNDING = 'refunding'
    REFUNDED = 'refunded'
    
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, 'Payment Pending'),
        (PAYMENT_PROCESSING, 'Payment Processing'),
        (PAID, 'Paid'),
        (PAYMENT_FAILED, 'Payment Failed'),
        (REFUNDING, 'Refunding'),
        (REFUNDED, 'Refunded'),
    ]
    
    # Inventory Status
    IN_STOCK = 'in_stock'
    LOW_STOCK = 'low_stock'
    OUT_OF_STOCK = 'out_of_stock'
    DISCONTINUED = 'discontinued'
    
    INVENTORY_STATUS_CHOICES = [
        (IN_STOCK, 'In Stock'),
        (LOW_STOCK, 'Low Stock'),
        (OUT_OF_STOCK, 'Out of Stock'),
        (DISCONTINUED, 'Discontinued'),
    ]
    
    @classmethod
    def get_cart_choices(cls):
        """Get cart status choices"""
        return cls.CART_STATUS_CHOICES
    
    @classmethod
    def get_order_choices(cls):
        """Get order status choices"""
        return cls.ORDER_STATUS_CHOICES
    
    @classmethod
    def get_payment_choices(cls):
        """Get payment status choices"""
        return cls.PAYMENT_STATUS_CHOICES
    
    @classmethod
    def get_inventory_choices(cls):
        """Get inventory status choices"""
        return cls.INVENTORY_STATUS_CHOICES
    
    @classmethod
    def get_fulfillment_choices(cls):
        """Get fulfillment status choices"""
        return [
            (cls.PENDING, 'Pending'),
            (cls.PROCESSING, 'Processing'),
            (cls.SHIPPED, 'Shipped'),
            (cls.DELIVERED, 'Delivered'),
            (cls.FAILED, 'Failed'),
            (cls.FULFILLED, 'Fulfilled'),
        ]
