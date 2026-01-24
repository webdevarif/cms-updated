"""
Ecommerce services with caching integration for Digital Farmers CMS.

Business logic for product management with cache optimization.
"""
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class ProductService:
    """Product management service with caching"""
    
    @staticmethod
    def create_order(store, user, order_data):
        """Create order using centralized service"""
        from ..models import Order
        from apps.logs.tasks import log_event_async
        
        # Generate unique order number
        order_number = f"ORD-{timezone.now().strftime('%Y%m%d%H%M%S')}-{store.id}"
        
        order = Order.objects.create(
            store=store,
            user=user,
            order_number=order_number,
            **order_data
        )
        
        log_event_async.delay({
            'event_type': 'ORDER_CREATED',
            'message': f"Order created: {order.order_number}",
            'store': store,
            'user': user,
            'entity_type': 'Order',
            'entity_id': order.id,
            'metadata': {
                'order_number': order.order_number,
                'total': str(order.total)
            }
        })
        
        return order
    
    @staticmethod
    def create_order_item(order, item_data):
        """Create order item using centralized service"""
        from ..models import OrderItem
        
        return OrderItem.objects.create(
            order=order,
            **item_data
        )
    
    @staticmethod
    def get_product(store, product_id):
        """
        Get product with caching
        """
        from apps.cache.services import CacheService
        from ..models import Product
        
        # Try cache first
        cached = CacheService.get_json(store, 'ecommerce', 'product', product_id)
        if cached:
            logger.debug(f"Cache HIT for product {product_id} in store {store.slug}")
            return cached
        
        # Fetch from database
        try:
            product = Product.objects.get(store=store, id=product_id, is_active=True)
        except Product.DoesNotExist:
            return None
        
        # Build product data
        data = {
            'id': product.id,
            'title': product.title,
            'slug': product.slug,
            'description': product.description,
            'short_description': product.short_description,
            'price': float(product.base_price),
            'sale_price': float(product.sale_price) if product.sale_price else None,
            'is_active': product.is_active,
            'is_featured': product.is_featured,
            'featured_image': product.primary_image.url if product.primary_image else None,
            'images': [img.url for img in product.images.all()],
            'categories': [cat.name for cat in product.categories.all()],
            'tags': [tag.name for tag in product.tags.all()],
            'inventory': product.inventory_count,
            'sku': product.sku,
            'created_at': product.created_at.isoformat(),
            'updated_at': product.updated_at.isoformat()
        }
        
        # Cache the result
        CacheService.cache_json(store, 'ecommerce', 'product', product_id, data, timeout=3600)
        logger.debug(f"Cached product {product_id} for store {store.slug}")
        
        return data
    
    @staticmethod
    def get_product_by_slug(store, slug):
        """
        Get product by slug with caching
        """
        from apps.cache.services import CacheService
        from ..models import Product
        
        # Try cache first
        cached = CacheService.get_json(store, 'ecommerce', 'product_by_slug', slug)
        if cached:
            logger.debug(f"Cache HIT for product slug {slug} in store {store.slug}")
            return cached
        
        # Fetch from database
        try:
            product = Product.objects.get(store=store, slug=slug, is_active=True)
        except Product.DoesNotExist:
            return None
        
        # Use get_product to build data
        return ProductService.get_product(store, product.id)
    
    @staticmethod
    def get_featured_products(store, limit=10):
        """
        Get featured products with caching
        """
        from apps.cache.services import CacheService
        from ..models import Product
        
        # Try cache first
        cache_key = f"featured_products_{limit}"
        cached = CacheService.get_json(store, 'ecommerce', cache_key, 'all')
        if cached:
            logger.debug(f"Cache HIT for featured products in store {store.slug}")
            return cached
        
        # Fetch from database
        products = Product.objects.filter(
            store=store,
            is_active=True,
            is_featured=True
        ).order_by('-created_at')[:limit].select_related('store')
        
        # Build product data
        data = []
        for product in products:
            product_data = {
                'id': product.id,
                'title': product.title,
                'slug': product.slug,
                'price': float(product.base_price),
                'sale_price': float(product.sale_price) if product.sale_price else None,
                'featured_image': product.primary_image.url if product.primary_image else None,
                'inventory': product.inventory_count,
                'sku': product.sku
            }
            data.append(product_data)
        
        # Cache the result
        CacheService.cache_json(store, 'ecommerce', cache_key, 'all', data, timeout=1800)
        logger.debug(f"Cached featured products for store {store.slug}")
        
        return data
    
    @staticmethod
    def get_products_by_category(store, category_id, limit=20):
        """
        Get products by category with caching
        """
        from apps.cache.services import CacheService
        from ..models import Product
        
        # Try cache first
        cache_key = f"products_by_category_{category_id}_{limit}"
        cached = CacheService.get_json(store, 'ecommerce', cache_key, 'all')
        if cached:
            logger.debug(f"Cache HIT for category {category_id} products in store {store.slug}")
            return cached
        
        # Fetch from database
        products = Product.objects.filter(
            store=store,
            is_active=True,
            categories__id=category_id
        ).order_by('-created_at')[:limit].select_related('store')
        
        # Build product data
        data = []
        for product in products:
            product_data = {
                'id': product.id,
                'title': product.title,
                'slug': product.slug,
                'price': float(product.base_price),
                'sale_price': float(product.sale_price) if product.sale_price else None,
                'featured_image': product.primary_image.url if product.primary_image else None,
                'inventory': product.inventory_count,
                'sku': product.sku
            }
            data.append(product_data)
        
        # Cache the result
        CacheService.cache_json(store, 'ecommerce', cache_key, 'all', data, timeout=1800)
        logger.debug(f"Cached category {category_id} products for store {store.slug}")
        
        return data
    
    @staticmethod
    def search_products(store, query, limit=20):
        """
        Search products with caching
        """
        from apps.cache.services import CacheService
        from ..models import Product
        from django.db.models import Q
        
        # Create cache key from query
        import hashlib
        query_hash = hashlib.md5(query.encode()).hexdigest()
        cache_key = f"search_products_{query_hash}_{limit}"
        
        # Try cache first
        cached = CacheService.get_json(store, 'ecommerce', cache_key, 'all')
        if cached:
            logger.debug(f"Cache HIT for search '{query}' in store {store.slug}")
            return cached
        
        # Search database
        products = Product.objects.filter(
            store=store,
            is_active=True,
            Q(title__icontains=query) | Q(description__icontains=query) | Q(sku__icontains=query)
        ).order_by('-created_at')[:limit].select_related('store')
        
        # Build product data
        data = []
        for product in products:
            product_data = {
                'id': product.id,
                'title': product.title,
                'slug': product.slug,
                'description': product.description[:200],  # Truncate for search results
                'price': float(product.base_price),
                'featured_image': product.primary_image.url if product.primary_image else None,
                'inventory': product.inventory_count,
                'sku': product.sku
            }
            data.append(product_data)
        
        # Cache the result
        CacheService.cache_json(store, 'ecommerce', cache_key, 'all', data, timeout=900)  # 15 minutes for search
        logger.debug(f"Cached search results for '{query}' in store {store.slug}")
        
        return data
    
    @staticmethod
    def update_product(product, **kwargs):
        """Update a product"""
        from apps.cache.services import CacheService
        
        # Update product
        for field, value in kwargs.items():
            setattr(product, field, value)
        product.save()
        
        # Invalidate cache
        CacheService.delete(product.store, 'ecommerce', 'product', str(product.id))
        CacheService.delete(product.store, 'ecommerce', 'product_by_slug', product.slug)
        CacheService.delete_pattern(product.store, 'ecommerce:product:*')
        
        # If price or status changed, invalidate listings
        if 'base_price' in kwargs or 'sale_price' in kwargs or 'is_active' in kwargs:
            CacheService.delete_pattern(product.store, 'ecommerce:featured_products:*')
            CacheService.delete_pattern(product.store, 'ecommerce:products_by_category:*')
        
        logger.info(f"Updated product {product.id} for store {product.store.slug}")
        
        return product
    
    @staticmethod
    def delete_product(product):
        """Delete a product"""
        from apps.cache.services import CacheService
        
        # Invalidate cache
        CacheService.delete(product.store, 'ecommerce', 'product', str(product.id))
        CacheService.delete(product.store, 'ecommerce', 'product_by_slug', product.slug)
        CacheService.delete_pattern(product.store, 'ecommerce:product:*')
        
        # Delete product
        product.delete()
        
        logger.info(f"Deleted product {product.id} for store {product.store.slug}")
        
        return True
    
    @staticmethod
    def create_product(store, title, slug, **kwargs):
        """Centralized product creation method"""
        from apps.public.ecommerce.models import Product
        from apps.logs.tasks import log_event_async
        
        product = Product.objects.create(
            store=store,
            title=title,
            slug=slug,
            **kwargs
        )
        
        log_event_async.delay({
            'event_type': 'PRODUCT_CREATED',
            'message': f"Product created: {product.title}",
            'store': store,
            'entity_type': 'Product',
            'entity_id': product.id,
            'metadata': {
                'sku': product.sku,
                'price': str(product.base_price)
            }
        })
        
        return product
