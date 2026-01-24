"""
Services for ecommerce app.
"""
from django.db import transaction
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Basic notification service for ecommerce"""
    
    @staticmethod
    def notify_staff(store, notification_type, context):
        """Notify store staff"""
        # TODO: Implement staff notification
        pass
    
    @staticmethod
    def notify_user(user, notification_type, context, store=None):
        """Notify user"""
        # TODO: Implement user notification
        pass


class ProductService:
    """Service for product operations"""
    
    @staticmethod
    @transaction.atomic
    def create_product(store, user, data):
        """Create a new product using centralized service"""
        from ..models import Product
        from apps.logs.tasks import log_event_async
        
        # Use centralized product creation
        product = ProductService.create_product(store, user, data)
        
        log_event_async.delay({
            'event_type': 'PRODUCT_CREATED',
            'message': f"Product created: {product.title}",
            'store': store,
            'user': user,
            'entity_type': 'Product',
            'entity_id': product.id,
            'metadata': {
                'sku': product.sku,
                'price': str(product.base_price)
            }
        })
        
        return product
    
    @staticmethod
    def create_product_blog_post(product, user, title=None, content=None):
        """Create a blog-style post from product description using PostService"""
        from apps.posts.v2.services import PostService
        from apps.posts.v2.models import PostType
        
        # Get or create blog post type for the store
        post_type, created = PostType.objects.get_or_create(
            store=product.store,
            slug='product-blog',
            defaults={
                'name': 'Product Blog',
                'is_public': True,
                'supports_comments': True
            }
        )
        
        # Use provided title/content or fall back to product data
        post_title = title or f"Product Spotlight: {product.title}"
        post_content = content or product.description or f"<p>Check out our amazing product: {product.title}</p>"
        
        post = PostService.create_post(
            store=product.store,
            user=user,
            post_type=post_type,
            title=post_title,
            content=post_content,
            excerpt=product.short_description,
            status='draft',
            metadata={
                'product_id': product.id,
                'sku': product.sku,
                'auto_generated': True
            }
        )
        
        logger.info(f"Created blog post {post.id} for product {product.id}")
        return post
    
    @staticmethod
    def update_product(product, user, data):
        """Update an existing product"""
        from apps.logs.tasks import log_event_async
        
        for field, value in data.items():
            setattr(product, field, value)
        product.save()
        
        log_event_async.delay({
            'event_type': 'PRODUCT_UPDATED',
            'message': f"Product updated: {product.title}",
            'store': product.store,
            'user': user,
            'entity_type': 'Product',
            'entity_id': product.id
        })
        
        return product


class CartService:
    """Service for cart operations"""
    
    @staticmethod
    def get_or_create_cart(store, user=None, session_key=None):
        """Get or create cart for user/session"""
        from ..models import Cart
        
        if user:
            cart, created = Cart.objects.get_or_create(
                store=store,
                user=user
            )
        else:
            cart, created = Cart.objects.get_or_create(
                store=store,
                session_key=session_key
            )
        
        return cart
    
    @staticmethod
    @transaction.atomic
    def add_item(cart, product, variant=None, quantity=1):
        """Add item to cart"""
        from ..models import CartItem
        
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not created:
            item.quantity += quantity
            item.save()
        
        return item
    
    @staticmethod
    @transaction.atomic
    def remove_item(cart, product, variant=None):
        """Remove item from cart"""
        from ..models import CartItem
        CartItem.objects.filter(
            cart=cart,
            product=product,
            variant=variant
        ).delete()
    
    @staticmethod
    def clear_cart(cart):
        """Clear all items from cart"""
        cart.items.all().delete()


class OrderService:
    """Service for order operations"""
    
    @staticmethod
    @transaction.atomic
    def create_order(store, user, cart_data):
        """Create order from cart using centralized service"""
        from ..models import Order, OrderItem
        from apps.logs.tasks import log_event_async
        
        # Generate order number
        order_number = f"ORD-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        
        # Use centralized order creation
        order = OrderService.create_order(store, user, {
            'order_number': order_number,
            'status': 'pending',
            'currency': 'USD',
            'subtotal': cart_data['subtotal'],
            'tax': cart_data.get('tax', 0),
            'shipping': cart_data.get('shipping', 0),
            'total': cart_data['total'],
            'customer_notes': cart_data.get('customer_notes', ''),
        })
        
        # Create order items using centralized service
        for item_data in cart_data['items']:
            OrderService.create_order_item(order, item_data)
        
        # Log order creation
        log_event_async.delay({
            'event_type': 'ORDER_CREATED',
            'message': f"Order created: {order.order_number}",
            'store': store,
            'user': user,
            'entity_type': 'Order',
            'entity_id': order.id,
            'metadata': {
                'order_number': order.order_number,
                'total': str(order.total),
                'item_count': len(cart_data['items'])
            }
        })
        
        context = {
            'title': 'Order Created',
            'message': f'Your order {order_number} has been created',
            'order_id': order.id
        }
        
        # Notify store staff of new order
        NotificationService.notify_staff(
            store=store,
            notification_type='order.new_order',
            context={
                'title': 'New Order Received',
                'message': f'New order {order_number} received from {order.customer_email}',
                'order_id': order.id,
                'customer_email': order.customer_email,
                'total': str(order.total)
            }
        )
        
        return order
    
    @staticmethod
    def update_order_status(order, status):
        """Update order status"""
        from apps.logs.tasks import log_event_async
        from apps.notifications.services import NotificationService
        
        order.status = status
        order.save()
        
        log_event_async.delay({
            'event_type': 'ORDER_STATUS_UPDATED',
            'message': f"Order {order.order_number} status changed to {status}",
            'store': order.store,
            'entity_type': 'Order',
            'entity_id': order.id,
            'metadata': {'status': status}
        })
        
        # Send status update notification to customer
        NotificationService.notify_user(
            user=order.user,
            notification_type='order.status_updated',
            context={
                'title': 'Order Status Updated',
                'message': f'Your order {order.order_number} status has been updated to: {status.title()}',
                'order_id': order.id,
                'order_number': order.order_number,
                'new_status': status
            },
            store=order.store
        )
