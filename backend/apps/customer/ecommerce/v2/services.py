"""
Services for customer ecommerce operations.
"""
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth import get_user_model
import logging
from decimal import Decimal

from apps.public.ecommerce.v2.services import (
    ProductService as PublicProductService,
    CartService as PublicCartService,
    OrderService as PublicOrderService
)
from apps.public.ecommerce.models import Cart, CartItem, Order, OrderItem, Product, ProductVariant
from apps.logs.tasks import log_event_async

User = get_user_model()
logger = logging.getLogger(__name__)


class CustomerProductService(PublicProductService):
    """Service for customer product operations."""
    
    @classmethod
    def get_available_products(cls, store, user, filters=None):
        """
        Get all available products for a customer.
        
        Args:
            store: The store to get products for
            user: The authenticated user
            filters: Dictionary of filters to apply
            
        Returns:
            QuerySet of available products
        """
        queryset = Product.objects.filter(
            store=store,
            status='active',
            is_available=True
        )
        
        # Apply filters
        if filters:
            if 'category' in filters:
                queryset = queryset.filter(categories__id=filters['category'])
            if 'tag' in filters:
                queryset = queryset.filter(tags__contains=[filters['tag']])
            if 'price_min' in filters:
                queryset = queryset.filter(price__gte=Decimal(filters['price_min']))
            if 'price_max' in filters:
                queryset = queryset.filter(price__lte=Decimal(filters['price_max']))
            if 'search' in filters:
                queryset = queryset.filter(
                    Q(title__icontains=filters['search']) |
                    Q(description__icontains=filters['search']) |
                    Q(tags__icontains=filters['search'])
                )
        
        return queryset.distinct()
    
    @classmethod
    def get_product_variants(cls, product, user):
        """
        Get available variants for a product.
        
        Args:
            product: The product to get variants for
            user: The authenticated user
            
        Returns:
            QuerySet of available variants
        """
        return ProductVariant.objects.filter(
            product=product,
            is_available=True
        )


class CustomerCartService(PublicCartService):
    """Service for customer cart operations."""
    
    @classmethod
    @transaction.atomic
    def add_item_to_cart(cls, cart, product_id, variant_id=None, quantity=1, custom_fields=None):
        """
        Add an item to the customer's cart with additional validation.
        
        Args:
            cart: The cart to add the item to
            product_id: ID of the product to add
            variant_id: Optional ID of the variant to add
            quantity: Quantity to add
            custom_fields: Optional custom fields for the cart item
            
        Returns:
            The created or updated cart item
            
        Raises:
            ValidationError: If the product is not available or out of stock
        """
        try:
            # Get the product and validate it's available
            product = Product.objects.get(
                id=product_id,
                store=cart.store,
                status='active',
                is_available=True
            )
            
            variant = None
            if variant_id:
                variant = ProductVariant.objects.get(
                    id=variant_id,
                    product=product,
                    is_available=True
                )
                # Check inventory if inventory management is enabled
                if variant.inventory_management and variant.inventory_quantity < quantity:
                    raise ValidationError("Not enough inventory available")
            
            # Check if the item already exists in the cart
            cart_item = CartItem.objects.filter(
                cart=cart,
                product=product,
                variant=variant
            ).first()
            
            if cart_item:
                # Update quantity if item already exists
                new_quantity = cart_item.quantity + quantity
                if variant and variant.inventory_management and variant.inventory_quantity < new_quantity:
                    raise ValidationError("Not enough inventory available for the requested quantity")
                cart_item.quantity = new_quantity
                if custom_fields:
                    cart_item.custom_fields = custom_fields
                cart_item.save()
            else:
                # Create new cart item
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    variant=variant,
                    quantity=quantity,
                    unit_price=variant.price_override if variant else product.price,
                    custom_fields=custom_fields or {}
                )
            
            # Update cart totals
            cls._update_cart_totals(cart)
            
            # Log the event
            log_event_async.delay({
                'event_type': 'CART_ITEM_ADDED',
                'message': f"Item added to cart: {product.title}",
                'store': cart.store.id,
                'user': cart.user.id if cart.user else None,
                'entity_type': 'CartItem',
                'entity_id': cart_item.id,
                'metadata': {
                    'product_id': str(product.id),
                    'variant_id': str(variant.id) if variant else None,
                    'quantity': quantity
                }
            })
            
            return cart_item
            
        except Product.DoesNotExist:
            raise ValidationError("Product not found or not available")
        except ProductVariant.DoesNotExist:
            raise ValidationError("Variant not found or not available")


class CustomerOrderService(PublicOrderService):
    """Service for customer order operations."""
    
    @classmethod
    @transaction.atomic
    def create_order_from_cart(cls, cart, shipping_address, billing_address=None, payment_method=None, notes=None):
        """
        Create an order from a customer's cart with additional validation.
        
        Args:
            cart: The cart to create the order from
            shipping_address: Shipping address for the order
            billing_address: Billing address for the order (optional)
            payment_method: Payment method for the order (optional)
            notes: Order notes (optional)
            
        Returns:
            The created order
            
        Raises:
            ValidationError: If the cart is empty or invalid
        """
        # Validate cart
        if not cart.items.exists():
            raise ValidationError("Cannot create order from empty cart")
        
        # Check inventory for all items
        for item in cart.items.all():
            if item.variant and item.variant.inventory_management:
                if item.variant.inventory_quantity < item.quantity:
                    raise ValidationError(f"Not enough inventory for {item.product.title}")
        
        # Create the order
        order = super().create_order_from_cart(
            cart=cart,
            shipping_address=shipping_address,
            billing_address=billing_address,
            payment_method=payment_method,
            notes=notes
        )
        
        # Log the event
        log_event_async.delay({
            'event_type': 'ORDER_CREATED',
            'message': f"Order #{order.order_number} created",
            'store': cart.store.id,
            'user': cart.user.id if cart.user else None,
            'entity_type': 'Order',
            'entity_id': order.id,
            'metadata': {
                'order_number': order.order_number,
                'total': str(order.total_price),
                'item_count': order.line_items.count()
            }
        })
        
        return order
    
    @classmethod
    def get_customer_orders(cls, user, store, status=None):
        """
        Get orders for a customer.
        
        Args:
            user: The customer user
            store: The store to get orders from
            status: Optional order status filter
            
        Returns:
            QuerySet of customer's orders
        """
        queryset = Order.objects.filter(
            store=store,
            customer=user,
            status__in=['open', 'paid', 'fulfilled']  Only show active orders
        )
        
        if status:
            queryset = queryset.filter(fulfillment_status=status)
            
        return queryset.order_by('-created_at')
