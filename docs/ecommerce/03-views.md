# Ecommerce Views and API Endpoints

## 3. ViewSets and API Endpoints

### 3.1 Base Classes

#### TenantViewSet
```python
# All ecommerce ViewSets must inherit from TenantViewSet
from core.viewsets import TenantViewSet
from core.permissions import IsStoreOwner, IsStoreStaff, IsStoreUser

class EcommerceViewSet(TenantViewSet):
    """
    Base ViewSet for all ecommerce endpoints with store scoping
    Follows main backend rules pattern
    """

    def get_queryset(self):
        """Filter queryset by store (inherited from TenantViewSet)"""
        return super().get_queryset()

    def perform_create(self, serializer):
        """Set store on create (inherited from TenantViewSet)"""
        return super().perform_create(serializer)
```

### 3.2 Product Views

#### ProductViewSet
```python
# apps/dashboard/ecommerce/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema

class ProductViewSet(TenantViewSet):
    """
    Product management endpoints for dashboard
    Follows main backend rules pattern
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    queryset = Product.objects.select_related('store').prefetch_related(
        'variants', 'categories', 'images'
    ).all()
    serializer_class = ProductSerializer
    filterset_fields = ['status', 'featured', 'categories']
    search_fields = ['title', 'description', 'sku']
    ordering_fields = ['title', 'created_at', 'updated_at']
    ordering = ['-created_at']

    @extend_schema(
        summary="Duplicate Product",
        description="Create a duplicate of existing product",
        responses={201: ProductSerializer}
    )
    def duplicate(self, request, pk=None):
        """Duplicate a product using service layer"""
        product = self.get_object()

        from services.product import ProductService
        new_product = ProductService.duplicate_product(product, request.user)

        serializer = self.get_serializer(new_product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def bulk_update_variants(self, request, pk=None):
        """Bulk update product variants"""
        product = self.get_object()
        variants_data = request.data.get('variants', [])

        for variant_data in variants_data:
            variant_id = variant_data.get('id')
            if variant_id:
                variant = product.variants.get(id=variant_id)
                for attr, value in variant_data.items():
                    if attr != 'id':
                        setattr(variant, attr, value)
                variant.save()

        return Response({'status': 'updated'})

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export products to CSV"""
        store = self.get_store()
        products = self.get_queryset()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'

        writer = csv.writer(response)
        writer.writerow(['Title', 'SKU', 'Price', 'Status', 'Created At'])

        for product in products:
            writer.writerow([
                product.title,
                product.sku,
                product.variants.first().price if product.variants.exists() else '',
                product.status,
                product.created_at
            ])

        return response
```

#### ProductVariantViewSet
```python
class ProductVariantViewSet(StoreScopedViewSet):
    """
    Product variant management endpoints
    """
    queryset = ProductVariant.objects.select_related('product').all()
    serializer_class = ProductVariantSerializer
    filterset_fields = ['product', 'inventory_policy']
    search_fields = ['title', 'sku', 'barcode']
    ordering_fields = ['position', 'price', 'created_at']
    ordering = ['position']

    def get_queryset(self):
        store = self.get_store()
        return super().get_queryset().filter(product__store=store)

    @action(detail=True, methods=['post'])
    def adjust_inventory(self, request, pk=None):
        """Adjust variant inventory"""
        variant = self.get_object()
        quantity = request.data.get('quantity', 0)
        transaction_type = request.data.get('type', 'adjustment')
        notes = request.data.get('notes', '')

        inventory, created = Inventory.objects.get_or_create(
            store=variant.product.store,
            product=variant.product,
            variant=variant,
            defaults={'quantity': 0}
        )

        if transaction_type == 'add':
            inventory.quantity += quantity
        elif transaction_type == 'subtract':
            inventory.quantity -= quantity
        else:
            inventory.quantity = quantity

        inventory.save()

        # Create transaction record
        InventoryTransaction.objects.create(
            inventory=inventory,
            type=transaction_type,
            quantity=quantity,
            notes=notes,
            created_by=request.user
        )

        return Response({'quantity': inventory.quantity})
```

#### ProductCategoryViewSet
```python
class ProductCategoryViewSet(StoreScopedViewSet):
    """
    Product category management endpoints
    """
    queryset = ProductCategory.objects.select_related('parent', 'image').all()
    serializer_class = ProductCategorySerializer
    filterset_fields = ['parent', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'position', 'created_at']
    ordering = ['position']

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get category tree structure"""
        store = self.get_store()
        categories = self.get_queryset().filter(store=store, is_active=True)

        def build_tree(parent=None):
            children = categories.filter(parent=parent)
            return [
                {
                    'id': cat.id,
                    'name': cat.name,
                    'slug': cat.slug,
                    'children': build_tree(cat)
                }
                for cat in children
            ]

        tree = build_tree()
        return Response(tree)
```

### 3.3 Public API Views

#### PublicProductViewSet
```python
# apps/public/ecommerce/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import AllowAny

class PublicProductViewSet(TenantViewSet):
    """
    Public product catalog endpoints
    No authentication required
    """
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    queryset = Product.objects.filter(status='published').select_related('store').prefetch_related(
        'variants', 'categories', 'images'
    )
    serializer_class = PublicProductSerializer
    filterset_fields = ['status', 'featured', 'categories']
    search_fields = ['title', 'description', 'sku']
    ordering_fields = ['title', 'created_at']
    ordering = ['-created_at']

    @extend_schema(
        summary="List Public Products",
        description="Get paginated list of published products",
        responses={200: PublicProductSerializer}
    )
    def list(self, request, *args, **kwargs):
        """List published products"""
        return super().list(request, *args, **kwargs)
### 3.4 Customer API Views

#### CustomerCartViewSet
```python
# apps/customer/ecommerce/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreUser

class CustomerCartViewSet(TenantViewSet):
    """
    Customer cart management endpoints
    Customer authentication required
    """
    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = CartSerializer

    def get_queryset(self):
        """Get cart for authenticated customer"""
        from services.cart import CartService
        return CartService.get_cart_for_customer(self.request.user, self.request.store)

    @extend_schema(
        summary="Get Customer Cart",
        description="Get current customer's shopping cart",
        responses={200: CartSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        """Get or create cart for customer"""
        cart = self.get_queryset()
        if not cart:
            from services.cart import CartService
            cart = CartService.create_cart_for_customer(self.request.user, self.request.store)

        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    def get_store(self):
        """Get store from request"""
        if hasattr(self.request, 'store'):
            return self.request.store
        raise ValidationError("Store not found")

    ### 3.5 URL Structure

#### Main Ecommerce URLs
```python
# apps/public/ecommerce/urls.py
from django.urls import include, path

app_name = 'ecommerce'

urlpatterns = [
    path('v2/', include('apps.public.ecommerce.v2.urls')),
]

# apps/customer/ecommerce/urls.py
urlpatterns = [
    path('v2/', include('apps.customer.ecommerce.v2.urls')),
]

# apps/dashboard/ecommerce/urls.py
urlpatterns = [
    path('v2/', include('apps.dashboard.ecommerce.v2.urls')),
]

# Main project URLs
# config/urls.py
urlpatterns = [
    path('v2/api/public/ecommerce/', include('apps.public.ecommerce.urls')),
    path('v2/api/customer/ecommerce/', include('apps.customer.ecommerce.urls')),
    path('v2/api/dashboard/ecommerce/', include('apps.dashboard.ecommerce.urls')),
]
            'shipping': str(cart.get_shipping()),
            'total': str(cart.get_total()),
            'currency': cart.currency
        })
```

### 3.4 Order Views

#### OrderViewSet
```python
# apps/dashboard/ecommerce/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema

class OrderViewSet(TenantViewSet):
    """
    Order management endpoints for dashboard
    Follows main backend rules pattern
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    queryset = Order.objects.select_related(
        'customer', 'store'
    ).prefetch_related('items', 'payments').all()
    serializer_class = OrderSerializer
    filterset_fields = ['status', 'payment_status', 'fulfillment_status']
    search_fields = ['order_number', 'customer__email']
    ordering_fields = ['created_at', 'total', 'order_number']
    ordering = ['-created_at']

    @extend_schema(
        summary="Create Order from Cart",
        description="Convert shopping cart to order",
        request=OrderCreateSerializer,
        responses={201: OrderSerializer}
    )
    @action(detail=False, methods=['post'])
    def create_from_cart(self, request):
        """Create order from cart using service layer"""
        from services.order import OrderService

        try:
            order = OrderService.create_order_from_cart(
                request.user,
                request.store,
                request.data
            )

            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Update Order Status",
        description="Update order status with validation",
        request=OrderStatusSerializer,
        responses={200: OrderSerializer}
    )
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update order status using service layer"""
        order = self.get_object()
        new_status = request.data.get('status')

        from services.order import OrderService
        try:
            updated_order = OrderService.update_order_status(
                order, new_status, request.user
            )

            serializer = self.get_serializer(updated_order)
            return Response(serializer.data)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Create Payment",
        description="Process payment for order",
        request=PaymentSerializer,
        responses={201: PaymentSerializer}
    )
    @action(detail=True, methods=['post'])
    def create_payment(self, request, pk=None):
        """Create payment for order using service layer"""
        order = self.get_object()

        from services.payment import PaymentService
        try:
            payment = PaymentService.process_payment(
                order, request.data, request.user
            )

            serializer = PaymentSerializer(payment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Generate Invoice",
        description="Generate PDF invoice for order",
        responses={200: 'application/pdf'}
    )
    @action(detail=True, methods=['get'])
    def invoice(self, request, pk=None):
        """Generate order invoice PDF"""
        order = self.get_object()

        from services.order import OrderService
        pdf_buffer = OrderService.generate_invoice_pdf(order)

        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_number}.pdf"'

        return response
```

### 3.5 Customer Views

#### CustomerViewSet
```python
# apps/dashboard/ecommerce/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema

class CustomerViewSet(TenantViewSet):
    """
    Customer management endpoints for dashboard
    Follows main backend rules pattern
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    queryset = Customer.objects.select_related('user').all()
    serializer_class = CustomerSerializer
    filterset_fields = ['email_marketing', 'sms_marketing']
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ['created_at', 'total_spent', 'order_count']
    ordering = ['-created_at']

    @extend_schema(
        summary="List Customers",
        description="Get paginated list of store customers",
        responses={200: CustomerSerializer}
    )
    def list(self, request, *args, **kwargs):
        """List customers with filtering and search"""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Get Customer Orders",
        description="Get orders for specific customer",
        responses={200: OrderSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """Get orders for specific customer"""
        customer = self.get_object()

        from services.customer import CustomerService
        orders = CustomerService.get_customer_orders(customer, request.store)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
```

### 3.6 Collection Views

#### CollectionViewSet
```python
# apps/dashboard/ecommerce/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema

class CollectionViewSet(TenantViewSet):
    """
    Collection management endpoints for dashboard
    Follows main backend rules pattern
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    queryset = Collection.objects.select_related('image').prefetch_related('conditions').all()
    serializer_class = CollectionSerializer
    filterset_fields = ['is_smart', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at']
    ordering = ['title']

    @extend_schema(
        summary="List Collections",
        description="Get paginated list of store collections",
        responses={200: CollectionSerializer}
    )
    def list(self, request, *args, **kwargs):
        """List collections with filtering and search"""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Get Collection Products",
        description="Get products in collection",
        responses={200: ProductSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get products in collection using service layer"""
        collection = self.get_object()

        from services.collection import CollectionService
        products = CollectionService.get_products_for_collection(collection)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Add Products to Collection",
        description="Add products to manual collection",
        request=CollectionProductSerializer,
        responses={200: dict}
    )
    @action(detail=True, methods=['post'])
    def add_products(self, request, pk=None):
        """Add products to manual collection using service layer"""
        collection = self.get_object()

        from services.collection import CollectionService
        try:
            CollectionService.add_products_to_collection(
                collection, request.data.get('product_ids', [])
            )

            return Response({'status': 'products_added'})

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Remove Products from Collection",
        description="Remove products from manual collection",
        request=CollectionProductSerializer,
        responses={200: dict}
    )
    @action(detail=True, methods=['post'])
    def remove_products(self, request, pk=None):
        """Remove products from manual collection using service layer"""
        collection = self.get_object()

        from services.collection import CollectionService
        try:
            CollectionService.remove_products_from_collection(
                collection, request.data.get('product_ids', [])
            )

            return Response({'status': 'products_removed'})

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

### 3.7 Coupon Views

#### CouponViewSet
```python
# apps/dashboard/ecommerce/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema

class CouponViewSet(TenantViewSet):
    """
    Coupon management endpoints for dashboard
    Follows main backend rules pattern
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    queryset = Coupon.objects.select_related('campaign').all()
    serializer_class = CouponSerializer
    filterset_fields = ['type', 'is_active', 'campaign']
    search_fields = ['code', 'name']
    ordering_fields = ['created_at', 'used_count']
    ordering = ['-created_at']

    @extend_schema(
        summary="Validate Coupon",
        description="Validate coupon code for cart",
        request=CouponValidateSerializer,
        responses={200: dict}
    )
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """Validate coupon code using service layer"""
        from services.coupon import CouponService

        try:
            result = CouponService.validate_coupon(
                request.data.get('code'),
                request.data.get('cart_total', 0),
                request.user,
                request.store
            )

            return Response(result)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Generate Coupon Codes",
        description="Generate multiple coupon codes",
        request=CouponGenerateSerializer,
        responses={200: dict}
    )
    @action(detail=True, methods=['post'])
    def generate_codes(self, request, pk=None):
        """Generate multiple coupon codes using service layer"""
        coupon = self.get_object()

        from services.coupon import CouponService
        try:
            codes = CouponService.generate_bulk_coupons(
                coupon,
                request.data.get('count', 1),
                request.data.get('prefix', ''),
                request.user
            )

            return Response({'codes': codes})

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
```

### 3.8 Public API Views

#### PublicProductViewSet
```python
class PublicProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public product catalog endpoints
    """
    serializer_class = PublicProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'categories', 'featured']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at', 'price']
    ordering = ['-created_at']

    def get_queryset(self):
        store = self.get_store()
        return Product.objects.filter(
            store=store,
            status='published'
        ).select_related('store').prefetch_related(
            'variants', 'categories', 'images'
        )

    def get_store(self):
        """Get store from subdomain or header"""
        host = self.request.get_host()
        subdomain = host.split('.')[0] if '.' in host else None

        if subdomain:
            try:
                return Store.objects.get(subdomain=subdomain, is_active=True)
            except Store.DoesNotExist:
                return Store.objects.filter(is_default=True, is_active=True).first()

        # Fallback to default store
        return Store.objects.filter(is_default=True, is_active=True).first()

    @action(detail=True, methods=['get'])
    def variants(self, request, pk=None):
        """Get product variants"""
        product = self.get_object()
        variants = product.variants.all()
        serializer = PublicProductVariantSerializer(variants, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        """Get related products"""
        product = self.get_object()

        # Get products from same categories
        category_ids = product.categories.values_list('id', flat=True)
        related = Product.objects.filter(
            store=product.store,
            status='published',
            categories__in=category_ids
        ).exclude(id=product.id).distinct()[:8]

        serializer = self.get_serializer(related, many=True)
        return Response(serializer.data)
```

### 3.8 URL Structure

#### Main Ecommerce URLs
```python
# apps/public/ecommerce/urls.py
from django.urls import include, path

app_name = 'ecommerce'

urlpatterns = [
    path('v2/', include('apps.public.ecommerce.v2.urls')),
]

# apps/customer/ecommerce/urls.py
urlpatterns = [
    path('v2/', include('apps.customer.ecommerce.v2.urls')),
]

# apps/dashboard/ecommerce/urls.py
urlpatterns = [
    path('v2/', include('apps.dashboard.ecommerce.v2.urls')),
]

# Main project URLs
# config/urls.py
urlpatterns = [
    path('v2/api/public/ecommerce/', include('apps.public.ecommerce.urls')),
    path('v2/api/customer/ecommerce/', include('apps.customer.ecommerce.urls')),
    path('v2/api/dashboard/ecommerce/', include('apps.dashboard.ecommerce.urls')),
]
```

#### Individual App URLs
```python
# apps/public/ecommerce/v2/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PublicProductViewSet

router = DefaultRouter()
router.register(r'products', PublicProductViewSet, basename='public-products')

urlpatterns = [
    path('', include(router.urls)),
]

# apps/customer/ecommerce/v2/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomerCartViewSet

router = DefaultRouter()
router.register(r'cart', CustomerCartViewSet, basename='customer-cart')

urlpatterns = [
    path('', include(router.urls)),
]

# apps/dashboard/ecommerce/v2/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import (
    ProductViewSet, OrderViewSet, CustomerViewSet,
    CollectionViewSet, CouponViewSet
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='dashboard-products')
router.register(r'orders', OrderViewSet, basename='dashboard-orders')
router.register(r'customers', CustomerViewSet, basename='dashboard-customers')
router.register(r'collections', CollectionViewSet, basename='dashboard-collections')
router.register(r'coupons', CouponViewSet, basename='dashboard-coupons')

# Nested routes
products_router = routers.NestedDefaultRouter(router, r'products', lookup='product')
products_router.register(r'images', ProductImageViewSet, basename='product-images')
products_router.register(r'variants', ProductVariantViewSet, basename='product-variants')

orders_router = routers.NestedDefaultRouter(router, r'orders', lookup='order')
orders_router.register(r'items', OrderItemViewSet, basename='order-items')
orders_router.register(r'payments', PaymentViewSet, basename='order-payments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(products_router.urls)),
    path('', include(orders_router.urls)),
]
