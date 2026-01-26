"""
Product service for ecommerce app.
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
import logging

from apps.ecommerce.models import Product, ProductVariant, Cart, CartItem

logger = logging.getLogger(__name__)


class ProductService:
    """Service class for product operations."""
    
    @staticmethod
    def get_available_products(store):
        """Get all available products for a store."""
        return Product.objects.filter(
            store=store,
            status='active'
        ).prefetch_related('variants', 'images')
    
    @staticmethod
    def get_product_with_variants(product_id):
        """Get product with all variants."""
        return Product.objects.filter(
            id=product_id
        ).prefetch_related('variants', 'images').first()
    
    @staticmethod
    def update_product_inventory(product, quantity_change):
        """Update product inventory."""
        if hasattr(product, 'inventory'):
            inventory = product.inventory
            inventory.quantity += quantity_change
            inventory.save()


class CartService:
    """Service class for cart operations."""
    
    @staticmethod
    def get_or_create_cart(store, user=None, session_key=None):
        """Get or create cart for user/session."""
        if user:
            cart, created = Cart.objects.get_or_create(
                store=store,
                user=user,
                status='active',
                defaults={'session_key': session_key}
            )
        else:
            cart, created = Cart.objects.get_or_create(
                store=store,
                session_key=session_key,
                status='active'
            )
        return cart
    
    @staticmethod
    def add_to_cart(cart, product, variant=None, quantity=1):
        """Add item to cart."""
        # Get the effective price
        price = variant.effective_price if variant else product.price
        
        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={
                'quantity': quantity,
                'price': price
            }
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        # Update cart totals
        CartService._update_cart_totals(cart)
        
        return cart_item
    
    @staticmethod
    def remove_from_cart(cart, product, variant=None):
        """Remove item from cart."""
        CartItem.objects.filter(
            cart=cart,
            product=product,
            variant=variant
        ).delete()
        
        # Update cart totals
        CartService._update_cart_totals(cart)
    
    @staticmethod
    def _update_cart_totals(cart):
        """Update cart subtotal and total."""
        items = cart.items.all()
        subtotal = sum(item.line_total for item in items)
        
        cart.subtotal = subtotal
        cart.total = subtotal  # Add tax/shipping later
        cart.save()


class InventoryService:
    """Service class for inventory operations."""
    
    @staticmethod
    def check_inventory_availability(product, variant=None, quantity=1):
        """Check if product/variant is available in requested quantity."""
        if not product.track_quantity:
            return product.status == 'active'
        
        if variant:
            # Check variant inventory if it exists, otherwise product inventory
            if hasattr(variant, 'inventory'):
                return variant.inventory.available_quantity >= quantity
            elif hasattr(product, 'inventory'):
                return product.inventory.available_quantity >= quantity
        else:
            if hasattr(product, 'inventory'):
                return product.inventory.available_quantity >= quantity
        
        return False
    
    @staticmethod
    def reserve_inventory(product, variant=None, quantity=1):
        """Reserve inventory for a product/variant."""
        if hasattr(product, 'inventory'):
            inventory = product.inventory
            if inventory.available_quantity >= quantity:
                inventory.reserved_quantity += quantity
                inventory.save()
                return True
        return False
    
    @staticmethod
    def release_inventory(product, variant=None, quantity=1):
        """Release reserved inventory."""
        if hasattr(product, 'inventory'):
            inventory = product.inventory
            inventory.reserved_quantity = max(0, inventory.reserved_quantity - quantity)
            inventory.save()
