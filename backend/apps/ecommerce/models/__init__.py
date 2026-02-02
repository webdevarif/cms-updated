"""
Ecommerce models.
"""

from .cart import Cart, CartItem
from .collections import ProductCollection
from .coupons import Coupon, CouponCampaign  # Re-enabled

# from .coupons import Coupon, CouponCampaign  # Temporarily disabled for schema generation
from .customers import CustomerProfile
from .inventory import Inventory
from .orders import Order, OrderItem
from .payments import Payment, PaymentMethod
from .products import Product, ProductCategory, ProductImage, ProductVariant
from .review import Review

__all__ = [
    "Product",
    "ProductVariant",
    "ProductCategory",
    "ProductImage",
    "ProductCollection",
    "Cart",
    "CartItem",
    "CustomerProfile",
    "Inventory",
    "Order",
    "OrderItem",
    "CouponCampaign",  # Re-enabled
    "Coupon",  # Re-enabled
    "PaymentMethod",
    "Payment",
    "Review",
]
