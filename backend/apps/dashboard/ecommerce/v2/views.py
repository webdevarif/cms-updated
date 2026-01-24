"""
Dashboard API views for ecommerce v2.
"""
from django.db.models import Q, Count, Sum, F, Avg
from django.utils import timezone
from datetime import timedelta, datetime
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from django_filters.rest_framework import DjangoFilterBackend

from core.permissions import IsStoreOwner, IsStoreAdmin
from apps.public.ecommerce.models import (
    Product, ProductVariant, Order, OrderItem, Cart, CartItem, 
    Customer, Collection, Coupon, Inventory, InventoryTransaction
)
from . import serializers
from .services import DashboardProductService, DashboardOrderService, DashboardInventoryService


class DashboardProductViewSet(viewsets.ModelViewSet):
    """
    Dashboard product management endpoints with advanced filtering and search.
    """
    permission_classes = [IsAuthenticated, IsStoreOwner | IsStoreAdmin]
    serializer_class = serializers.DashboardProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'product_type', 'vendor', 'is_available', 'is_featured']
    search_fields = ['title', 'description', 'tags', 'sku', 'barcode']
    ordering_fields = ['created_at', 'updated_at', 'price', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return products for the current store with filtering options."""
        queryset = Product.objects.filter(store=self.request.store)
        
        # Filter by collection
        collection_id = self.request.query_params.get('collection_id')
        if collection_id:
            queryset = queryset.filter(collections__id=collection_id)
            
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        # Filter by stock status
        in_stock = self.request.query_params.get('in_stock')
        if in_stock == 'true':
            queryset = queryset.filter(
                variants__inventory_management=False | 
                Q(variants__inventory_management=True, variants__inventory_quantity__gt=0)
            )
        
        return queryset.distinct()
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'create':
            return serializers.DashboardProductCreateSerializer
        elif self.action == 'update':
            return serializers.DashboardProductUpdateSerializer
        return self.serializer_class
    
    @extend_schema(
        summary="List Products",
        description="List all products with filtering, searching and ordering options.",
        parameters=[
            OpenApiParameter(
                name='collection_id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                description='Filter by collection ID',
                required=False
            ),
            OpenApiParameter(
                name='min_price',
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                description='Filter by minimum price',
                required=False
            ),
            OpenApiParameter(
                name='max_price',
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                description='Filter by maximum price',
                required=False
            ),
            OpenApiParameter(
                name='in_stock',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter by in-stock status',
                required=False
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Product",
        description="Create a new product with variants.",
        request=serializers.DashboardProductCreateSerializer,
        responses={201: serializers.DashboardProductSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Create a new product with variants."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            product = DashboardProductService.create_product(
                store=request.store,
                user=request.user,
                data=serializer.validated_data
            )
            
            output_serializer = serializers.DashboardProductSerializer(
                product,
                context={'request': request}
            )
            
            return Response(
                output_serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="Update Product",
        description="Update an existing product and its variants.",
        request=serializers.DashboardProductUpdateSerializer,
        responses={200: serializers.DashboardProductSerializer}
    )
    def update(self, request, *args, **kwargs):
        """Update a product and its variants."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Ensure the product belongs to the current store
        if instance.store_id != request.store.id:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        try:
            product = DashboardProductService.update_product(
                product=instance,
                user=request.user,
                data=serializer.validated_data
            )
            
            output_serializer = serializers.DashboardProductSerializer(
                product,
                context={'request': request}
            )
            
            return Response(output_serializer.data)
            
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="Bulk Update Products",
        description="Update multiple products at once.",
        request=serializers.DashboardProductBulkUpdateSerializer,
        responses={200: {'description': 'Bulk update successful'}}
    )
    @action(detail=False, methods=['patch'])
    def bulk_update(self, request, *args, **kwargs):
        """Update multiple products at once."""
        serializer = serializers.DashboardProductBulkUpdateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        try:
            updated_count = Product.objects.filter(
                id__in=serializer.validated_data['ids'],
                store=request.store
            ).update(**serializer.validated_data['data'])
            
            return Response({
                'detail': f'Successfully updated {updated_count} products.',
                'count': updated_count
            })
            
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="Get Product Metrics",
        description="Get metrics and statistics for products.",
        responses={
            200: serializers.DashboardProductMetricsSerializer
        }
    )
    @action(detail=False, methods=['get'])
    def metrics(self, request, *args, **kwargs):
        """Get product metrics and statistics."""
        from django.db.models.functions import TruncDay, TruncMonth, TruncYear
        
        # Date range for metrics (default: last 30 days)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # Time series data for products created
        time_series = (
            Product.objects
            .filter(store=request.store, created_at__range=(start_date, end_date))
            .annotate(period=TruncDay('created_at'))
            .values('period')
            .annotate(count=Count('id'))
            .order_by('period')
        )
        
        # Product counts by status
        status_counts = (
            Product.objects
            .filter(store=request.store)
            .values('status')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Top selling products
        top_selling = (
            OrderItem.objects
            .filter(order__store=request.store)
            .values('product__title')
            .annotate(
                total_quantity=Sum('quantity'),
                total_revenue=Sum(F('quantity') * F('price'))
            )
            .order_by('-total_quantity')[:10]
        )
        
        # Inventory status
        inventory_status = {
            'in_stock': ProductVariant.objects.filter(
                product__store=request.store,
                inventory_management=True,
                inventory_quantity__gt=0
            ).count(),
            'low_stock': ProductVariant.objects.filter(
                product__store=request.store,
                inventory_management=True,
                inventory_quantity__gt=0,
                inventory_quantity__lte=10
            ).count(),
            'out_of_stock': ProductVariant.objects.filter(
                product__store=request.store,
                inventory_management=True,
                inventory_quantity=0
            ).count(),
            'no_tracking': ProductVariant.objects.filter(
                product__store=request.store,
                inventory_management=False
            ).count()
        }
        
        # Prepare response data
        data = {
            'time_series': list(time_series),
            'status_counts': list(status_counts),
            'top_selling': list(top_selling),
            'inventory_status': inventory_status,
            'total_products': Product.objects.filter(store=request.store).count(),
            'total_variants': ProductVariant.objects.filter(product__store=request.store).count(),
            'period': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
        
        serializer = serializers.DashboardProductMetricsSerializer(data)
        return Response(serializer.data)


class DashboardOrderViewSet(viewsets.ModelViewSet):
    """
    Dashboard order management endpoints with advanced filtering and search.
    """
    permission_classes = [IsAuthenticated, IsStoreOwner | IsStoreAdmin]
    serializer_class = serializers.DashboardOrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'status', 'financial_status', 'fulfillment_status', 
        'payment_status', 'shipping_status', 'customer'
    ]
    search_fields = [
        'order_number', 'customer__email', 'shipping_address__first_name',
        'shipping_address__last_name', 'billing_address__first_name',
        'billing_address__last_name'
    ]
    ordering_fields = ['created_at', 'updated_at', 'total_price', 'order_number']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return orders for the current store with related data."""
        queryset = Order.objects.filter(store=self.request.store)
        
        # Apply date range filter
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
            
        # Filter by total price range
        min_total = self.request.query_params.get('min_total')
        max_total = self.request.query_params.get('max_total')
        if min_total:
            queryset = queryset.filter(total_price__gte=min_total)
        if max_total:
            queryset = queryset.filter(total_price__lte=max_total)
            
        # Filter by product
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(line_items__product_id=product_id)
            
        return queryset.distinct()
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'create':
            return serializers.DashboardOrderCreateSerializer
        elif self.action == 'update':
            return serializers.DashboardOrderUpdateSerializer
        elif self.action == 'create_fulfillment':
            return serializers.DashboardFulfillmentCreateSerializer
        elif self.action == 'create_refund':
            return serializers.DashboardRefundCreateSerializer
        return self.serializer_class
    
    @extend_schema(
        summary="List Orders",
        description="List all orders with filtering, searching and ordering options.",
        parameters=[
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter by order date (greater than or equal to)',
                required=False
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter by order date (less than or equal to)',
                required=False
            ),
            OpenApiParameter(
                name='min_total',
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                description='Filter by minimum order total',
                required=False
            ),
            OpenApiParameter(
                name='max_total',
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                description='Filter by maximum order total',
                required=False
            ),
            OpenApiParameter(
                name='product_id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                description='Filter by product ID',
                required=False
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Order",
        description="Create a new order manually.",
        request=serializers.DashboardOrderCreateSerializer,
        responses={201: serializers.DashboardOrderSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Create a new order manually."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            order = DashboardOrderService.create_order(
                store=request.store,
                user=request.user,
                data=serializer.validated_data
            )
            
            output_serializer = serializers.DashboardOrderSerializer(
                order,
                context={'request': request}
            )
            
            return Response(
                output_serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="Update Order Status",
        description="Update an order's status and optionally notify the customer.",
        request={
            'application/json': {
                'status': 'string',
                'notify_customer': 'boolean',
                'comment': 'string'
            }
        },
        responses={200: serializers.DashboardOrderSerializer},
    )
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update order status and optionally notify customer."""
        order = self.get_object()
        new_status = request.data.get('status')
        notify_customer = request.data.get('notify_customer', False)
        comment = request.data.get('comment', '')
        
        if not new_status:
            return Response(
                {'detail': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            order = DashboardOrderService.update_order_status(
                order=order,
                status=new_status,
                user=request.user
            )
            
            # Add order note
            if comment:
                order.notes.create(
                    user=request.user,
                    note=comment,
                    is_customer_notified=notify_customer
                )
            
            # Notify customer if requested
            if notify_customer and order.customer and order.customer.email:
                from core.services.notification import NotificationService
                NotificationService.send_order_update_notification(order, 'status_updated')
            
            serializer = self.get_serializer(order)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="Create Fulfillment",
        description="Create a fulfillment for an order.",
        request=serializers.DashboardFulfillmentCreateSerializer,
        responses={201: serializers.DashboardOrderSerializer}
    )
    @action(detail=True, methods=['post'])
    def create_fulfillment(self, request, pk=None):
        """Create a fulfillment for an order."""
        order = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            fulfillment = DashboardOrderService.create_fulfillment(
                order=order,
                user=request.user,
                data=serializer.validated_data
            )
            
            # Refresh order data
            order.refresh_from_db()
            
            output_serializer = serializers.DashboardOrderSerializer(
                order,
                context={'request': request}
            )
            
            return Response(
                output_serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="Create Refund",
        description="Create a refund for an order.",
        request=serializers.DashboardRefundCreateSerializer,
        responses={201: serializers.DashboardOrderSerializer}
    )
    @action(detail=True, methods=['post'])
    def create_refund(self, request, pk=None):
        """Create a refund for an order."""
        order = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            refund = DashboardOrderService.create_refund(
                order=order,
                user=request.user,
                data=serializer.validated_data
            )
            
            # Refresh order data
            order.refresh_from_db()
            
            output_serializer = serializers.DashboardOrderSerializer(
                order,
                context={'request': request}
            )
            
            return Response(
                output_serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="Get Order Metrics",
        description="Get metrics and statistics for orders.",
        responses={
            200: serializers.DashboardOrderMetricsSerializer
        }
    )
    @action(detail=False, methods=['get'])
    def metrics(self, request, *args, **kwargs):
        """Get order metrics and statistics."""
        from django.db.models.functions import TruncDay, TruncMonth, TruncYear
        
        # Date range for metrics (default: last 30 days)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # Time series data for orders
        time_series = (
            Order.objects
            .filter(store=request.store, created_at__range=(start_date, end_date))
            .annotate(period=TruncDay('created_at'))
            .values('period')
            .annotate(
                order_count=Count('id'),
                total_sales=Sum('total_price')
            )
            .order_by('period')
        )
        
        # Order counts by status
        status_counts = (
            Order.objects
            .filter(store=request.store)
            .values('status')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Sales by product
        sales_by_product = (
            OrderItem.objects
            .filter(order__store=request.store)
            .values('product__title')
            .annotate(
                quantity_sold=Sum('quantity'),
                total_revenue=Sum(F('quantity') * F('price'))
            )
            .order_by('-total_revenue')[:10]
        )
        
        # Sales by customer
        sales_by_customer = (
            Order.objects
            .filter(store=request.store)
            .values('customer__email')
            .annotate(
                order_count=Count('id'),
                total_spent=Sum('total_price')
            )
            .order_by('-total_spent')[:10]
        )
        
        # Prepare response data
        data = {
            'time_series': list(time_series),
            'status_counts': list(status_counts),
            'sales_by_product': list(sales_by_product),
            'sales_by_customer': list(sales_by_customer),
            'total_orders': Order.objects.filter(store=request.store).count(),
            'total_sales': Order.objects.filter(store=request.store).aggregate(
                total=Sum('total_price')
            )['total'] or 0,
            'average_order_value': Order.objects.filter(store=request.store).aggregate(
                avg=Avg('total_price')
            )['avg'] or 0,
            'period': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
        
        serializer = serializers.DashboardOrderMetricsSerializer(data)
        return Response(serializer.data)
