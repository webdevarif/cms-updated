"""
Services for dashboard ecommerce operations.
"""
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Sum, F, Q
from django.contrib.auth import get_user_model
from decimal import Decimal
import logging

from apps.public.ecommerce.v2.services import (
    ProductService as PublicProductService,
    OrderService as PublicOrderService,
    CartService as PublicCartService
)
from apps.public.ecommerce.models import (
    Product, ProductVariant, Order, OrderItem, Cart, CartItem,
    Customer, Collection, Coupon, Inventory, InventoryTransaction
)
from apps.logs.tasks import log_event_async

User = get_user_model()
logger = logging.getLogger(__name__)


class DashboardProductService(PublicProductService):
    """Service for dashboard product operations."""
    
    @classmethod
    @transaction.atomic
    def create_product(cls, store, user, data):
        """
        Create a new product with variants.
        
        Args:
            store: The store to create the product for
            user: The authenticated user
            data: Product data including variants
            
        Returns:
            The created product
            
        Raises:
            ValidationError: If the product data is invalid
        """
        from django.core.files.base import ContentFile
        import base64
        import uuid
        
        # Handle image upload if present
        image_data = data.pop('image', None)
        variants_data = data.pop('variants', [])
        collections_data = data.pop('collections', [])
        
        # Create the product
        product = Product.objects.create(store=store, **data)
        
        # Add to collections if specified
        if collections_data:
            collections = Collection.objects.filter(
                id__in=collections_data,
                store=store
            )
            product.collections.set(collections)
        
        # Handle image upload
        if image_data and ';base64,' in image_data:
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            product.image.save(filename, ContentFile(base64.b64decode(imgstr)), save=True)
        
        # Create variants
        for variant_data in variants_data:
            variant_data['product'] = product
            variant_data['store'] = store
            ProductVariant.objects.create(**variant_data)
        
        # Log the creation
        log_event_async.delay(
            'product_created',
            f'Product {product.title} created',
            'product',
            product.id,
            user.id if user else None,
            store.id
        )
        
        return product
        
        # Create variants
        for variant_data in variants_data:
            ProductVariant.objects.create(product=product, **variant_data)
        
        # Log the event
        log_event_async.delay({
            'event_type': 'PRODUCT_CREATED',
            'message': f"Product created: {product.title}",
            'store': store.id,
            'user': user.id,
            'entity_type': 'Product',
            'entity_id': product.id
        })
        
        return product
    
    @classmethod
    @transaction.atomic
    def update_product(cls, product, user, data):
        """
        Update a product and its variants.
        
        Args:
            product: The product to update
            user: The authenticated user
            data: Updated product data
            
        Returns:
            The updated product
            
        Raises:
            ValidationError: If the update data is invalid
        """
        variants_data = data.pop('variants', None)
        
        # Update product fields
        for field, value in data.items():
            setattr(product, field, value)
        product.save()
        
        # Update or create variants
        if variants_data is not None:
            # Get existing variant IDs
            existing_variant_ids = set(product.variants.values_list('id', flat=True))
            updated_variant_ids = set()
            
            for variant_data in variants_data:
                variant_id = variant_data.pop('id', None)
                if variant_id and variant_id in existing_variant_ids:
                    # Update existing variant
                    variant = ProductVariant.objects.get(id=variant_id, product=product)
                    for field, value in variant_data.items():
                        setattr(variant, field, value)
                    variant.save()
                    updated_variant_ids.add(variant_id)
                else:
                    # Create new variant
                    ProductVariant.objects.create(product=product, **variant_data)
            
            # Delete variants that were not included in the update
            deleted_variant_ids = existing_variant_ids - updated_variant_ids
            if deleted_variant_ids:
                ProductVariant.objects.filter(id__in=deleted_variant_ids).delete()
        
        # Log the event
        log_event_async.delay({
            'event_type': 'PRODUCT_UPDATED',
            'message': f"Product updated: {product.title}",
            'store': product.store.id,
            'user': user.id,
            'entity_type': 'Product',
            'entity_id': product.id
        })
        
        return product


class DashboardOrderService(PublicOrderService):
    """Service for dashboard order operations."""
    
    @classmethod
    def get_order_metrics(cls, store, start_date=None, end_date=None):
        """
        Get order metrics for the dashboard.
        
        Args:
            store: The store to get metrics for
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary of order metrics
        """
        from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
        
        # Set default date range if not provided
        if not end_date:
            end_date = timezone.now()
        if not start_date:
            start_date = end_date - timezone.timedelta(days=30)
            
        # Base queryset
        orders = Order.objects.filter(
            store=store,
            created_at__range=(start_date, end_date)
        )
        
        # Basic metrics
        total_orders = orders.count()
        total_sales = orders.aggregate(total=Sum('total_price'))['total'] or 0
        avg_order_value = orders.aggregate(avg=Avg('total_price'))['avg'] or 0
        
        # Time series data
        time_series = (
            orders
            .annotate(period=TruncDay('created_at'))
            .values('period')
            .annotate(
                order_count=Count('id'),
                total_sales=Sum('total_price')
            )
            .order_by('period')
        )
        
        # Status distribution
        status_distribution = (
            orders
            .values('status')
            .annotate(count=Count('id'), total=Sum('total_price'))
            .order_by('-count')
        )
        
        # Top products
        top_products = (
            OrderItem.objects
            .filter(order__store=store)
            .values('product__title')
            .annotate(
                quantity_sold=Sum('quantity'),
                total_revenue=Sum(F('quantity') * F('price'))
            )
            .order_by('-quantity_sold')[:10]
        )
        
        # Customer metrics
        customer_metrics = (
            Order.objects
            .filter(store=store)
            .values('customer__email')
            .annotate(
                order_count=Count('id'),
                total_spent=Sum('total_price')
            )
            .order_by('-total_spent')[:10]
        )
        
        return {
            'total_orders': total_orders,
            'total_sales': total_sales,
            'avg_order_value': avg_order_value,
            'time_series': list(time_series),
            'status_distribution': list(status_distribution),
            'top_products': list(top_products),
            'customer_metrics': list(customer_metrics),
            'period': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
    
    @classmethod
    @transaction.atomic
    def update_order_status(cls, order, status, user):
        """
        Update an order's status.
        
        Args:
            order: The order to update
            status: The new status
            user: The user making the update
            
        Returns:
            The updated order
            
        Raises:
            ValidationError: If the status update is not allowed
        """
        # Add any additional validation for dashboard-specific status updates
        if status not in dict(Order.STATUS_CHOICES):
            raise ValidationError({"status": "Invalid status"})
            
        # Prevent invalid status transitions
        current_status = order.status
        valid_transitions = {
            'pending': ['processing', 'cancelled', 'on_hold'],
            'processing': ['shipped', 'completed', 'on_hold', 'cancelled'],
            'on_hold': ['processing', 'cancelled'],
            'shipped': ['completed', 'returned'],
            'completed': ['refunded'],
            'cancelled': [],
            'refunded': [],
            'returned': ['refunded', 'completed']
        }
        
        if status != current_status and status not in valid_transitions.get(current_status, []):
            raise ValidationError({
                "status": f"Cannot change status from {current_status} to {status}"
            })
            
        order.status = status
        
        # Update timestamps based on status
        now = timezone.now()
        if status == 'processing':
            order.processed_at = now
        elif status == 'shipped':
            order.shipped_at = now
        elif status == 'completed':
            order.completed_at = now
        elif status == 'cancelled':
            order.cancelled_at = now
        
        order.save()
        
        # Log the event
        log_event_async.delay({
            'event_type': 'ORDER_STATUS_UPDATED',
            'message': f"Order {order.order_number} status updated to {status}",
            'store': order.store.id,
            'user': user.id,
            'entity_type': 'Order',
            'entity_id': order.id,
            'metadata': {
                'old_status': current_status,
                'new_status': status
            }
        })
        
        return order


class DashboardInventoryService:
    """Service for dashboard inventory operations."""
    
    @classmethod
    def update_inventory_levels(cls, store, user, updates):
        """
        Update inventory levels for multiple variants.
        
        Args:
            store: The store to update inventory for
            user: The user making the update
            updates: List of updates in the format [{'variant_id': X, 'adjustment': Y}]
            
        Returns:
            Dictionary with results of the updates
            
        Raises:
            ValidationError: If any update is invalid
        """
        results = []
        
        with transaction.atomic():
            for update in updates:
                variant_id = update.get('variant_id')
                adjustment = update.get('adjustment', 0)
                
                try:
                    variant = ProductVariant.objects.select_for_update().get(
                        id=variant_id,
                        product__store=store
                    )
                    
                    # Update inventory
                    new_quantity = variant.inventory_quantity + adjustment
                    if new_quantity < 0:
                        raise ValidationError(f"Insufficient inventory for variant {variant_id}")
                    
                    variant.inventory_quantity = new_quantity
                    variant.save()
                    
                    # Record stock movement
                    StockMovement.objects.create(
                        variant=variant,
                        quantity=adjustment,
                        previous_quantity=new_quantity - adjustment,
                        new_quantity=new_quantity,
                        user=user,
                        note=update.get('note', 'Manual adjustment')
                    )
                    
                    results.append({
                        'variant_id': variant_id,
                        'status': 'success',
                        'new_quantity': new_quantity
                    })
                    
                except (ProductVariant.DoesNotExist, ValidationError) as e:
                    results.append({
                        'variant_id': variant_id,
                        'status': 'error',
                        'error': str(e)
                    })
        
        return results
    
    @classmethod
    def get_low_stock_items(cls, store, threshold=10):
        """
        Get items with low inventory levels.
        
        Args:
            store: The store to check
            threshold: The inventory threshold to consider as low stock
            
        Returns:
            QuerySet of variants with low inventory
        """
        return ProductVariant.objects.filter(
            product__store=store,
            inventory_management=True,
            inventory_quantity__lte=threshold
        ).select_related('product').order_by('inventory_quantity')
