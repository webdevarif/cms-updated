"""
Dashboard API views for ecommerce v2.
"""

from datetime import datetime, timedelta

from apps.ecommerce.models.cart import Cart, CartItem
from apps.ecommerce.models.collections import ProductCollection
from apps.ecommerce.models.coupons import Coupon, CouponCampaign
from apps.ecommerce.models.customers import CustomerProfile
from apps.ecommerce.models.inventory import Inventory
from apps.ecommerce.models.orders import Order, OrderItem
from apps.ecommerce.models.payments import Payment, PaymentMethod
from apps.ecommerce.models.products import Product, ProductCategory, ProductVariant
from core.permissions import IsStoreAdmin, IsStoreOwner
from django.db.models import Avg, Count, F, Q, Sum
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    CartDashboardSerializer,
    CartItemDashboardSerializer,
    CouponCampaignDashboardSerializer,
    CouponDashboardSerializer,
    CustomerProfileDashboardSerializer,
    DashboardCollectionSerializer,
    DashboardInventorySerializer,
    DashboardProductSerializer,
    OrderDashboardSerializer,
    OrderItemDashboardSerializer,
    PaymentDashboardSerializer,
    PaymentMethodDashboardSerializer,
    ProductCategoryDashboardSerializer,
    ProductVariantDashboardSerializer,
)


class ProductDashboardViewSet(viewsets.ModelViewSet):
    """Dashboard product management endpoints"""

    permission_classes = [IsAuthenticated, IsStoreAdmin]
    serializer_class = DashboardProductSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "status", "store"]
    search_fields = ["title", "description", "sku"]
    ordering_fields = ["created_at", "updated_at", "price", "title"]

    def get_queryset(self):
        """Filter by current user's store"""
        return Product.objects.filter(store=self.request.store).select_related("category", "store")

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        """Duplicate a product"""
        product = self.get_object()

        # Create new product with same data
        new_product = Product.objects.create(
            title=f"{product.title} (Copy)",
            description=product.description,
            price=product.price,
            category=product.category,
            store=product.store,
            status="draft",
            sku=f"{product.sku}-copy",
        )

        serializer = self.get_serializer(new_product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductCategoryDashboardViewSet(viewsets.ModelViewSet):
    """Dashboard product category management endpoints"""

    permission_classes = [IsAuthenticated, IsStoreAdmin]
    serializer_class = ProductCategoryDashboardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["store", "is_active", "parent"]
    search_fields = ["name", "description"]

    def get_queryset(self):
        """Filter by current user's store"""
        return ProductCategory.objects.filter(store=self.request.store).select_related(
            "parent", "store"
        )


class CartDashboardViewSet(viewsets.ReadOnlyModelViewSet):
    """Dashboard cart viewing endpoints"""

    permission_classes = [IsAuthenticated, IsStoreAdmin]
    serializer_class = CartDashboardSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["store", "status"]

    def get_queryset(self):
        """Filter by current user's store"""
        return (
            Cart.objects.filter(store=self.request.store)
            .select_related("user", "store")
            .prefetch_related("items")
        )

    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get cart analytics"""
        store = request.store

        # Basic cart statistics
        total_carts = Cart.objects.filter(store=store).count()
        active_carts = Cart.objects.filter(store=store, status="active").count()
        abandoned_carts = Cart.objects.filter(store=store, status="abandoned").count()

        # Cart value analytics
        from django.db.models import Avg, Sum

        avg_cart_value = (
            Cart.objects.filter(store=store, status="active").aggregate(avg=Avg("total_value"))[
                "avg"
            ]
            or 0
        )

        total_cart_value = (
            Cart.objects.filter(store=store, status="active").aggregate(total=Sum("total_value"))[
                "total"
            ]
            or 0
        )

        return Response(
            {
                "total_carts": total_carts,
                "active_carts": active_carts,
                "abandoned_carts": abandoned_carts,
                "abandonment_rate": (
                    (abandoned_carts / total_carts * 100) if total_carts > 0 else 0
                ),
                "average_cart_value": round(avg_cart_value, 2),
                "total_cart_value": round(total_cart_value, 2),
            }
        )


class OrderDashboardViewSet(viewsets.ReadOnlyModelViewSet):
    """Dashboard order management endpoints"""

    permission_classes = [IsAuthenticated, IsStoreAdmin]
    serializer_class = OrderDashboardSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["store", "status", "payment_status"]
    search_fields = ["customer__username", "customer__email", "order_number"]
    ordering_fields = ["created_at", "updated_at", "total_amount"]

    def get_queryset(self):
        """Filter by current user's store"""
        return (
            Order.objects.filter(store=self.request.store)
            .select_related("customer", "store")
            .prefetch_related("items")
        )

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        """Update order status"""
        order = self.get_object()
        new_status = request.data.get("status")

        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get order analytics"""
        store = request.store

        # Order statistics
        total_orders = Order.objects.filter(store=store).count()
        pending_orders = Order.objects.filter(store=store, status="pending").count()
        completed_orders = Order.objects.filter(store=store, status="completed").count()

        # Revenue analytics
        from django.db.models import Avg, Sum

        total_revenue = (
            Order.objects.filter(store=store, status="completed").aggregate(
                total=Sum("total_amount")
            )["total"]
            or 0
        )

        avg_order_value = (
            Order.objects.filter(store=store, status="completed").aggregate(
                avg=Avg("total_amount")
            )["avg"]
            or 0
        )

        return Response(
            {
                "total_orders": total_orders,
                "pending_orders": pending_orders,
                "completed_orders": completed_orders,
                "completion_rate": (
                    (completed_orders / total_orders * 100) if total_orders > 0 else 0
                ),
                "total_revenue": round(total_revenue, 2),
                "average_order_value": round(avg_order_value, 2),
            }
        )


class CollectionDashboardViewSet(viewsets.ModelViewSet):
    """Dashboard collection management endpoints"""

    permission_classes = [IsAuthenticated, IsStoreAdmin]
    serializer_class = DashboardCollectionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["store", "is_active"]
    search_fields = ["name", "description"]

    def get_queryset(self):
        """Filter by current user's store"""
        return ProductCollection.objects.filter(store=self.request.store).select_related("store")


class CustomerProfileDashboardViewSet(viewsets.ReadOnlyModelViewSet):
    """Dashboard customer profile viewing endpoints"""

    permission_classes = [IsAuthenticated, IsStoreAdmin]
    serializer_class = CustomerProfileDashboardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["store"]
    search_fields = ["user__username", "user__email", "phone"]

    def get_queryset(self):
        """Filter by current user's store"""
        return CustomerProfile.objects.filter(store=self.request.store).select_related(
            "user", "store"
        )

    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get customer analytics"""
        store = request.store

        total_customers = CustomerProfile.objects.filter(store=store).count()

        # New customers in last 30 days
        from django.utils import timezone

        thirty_days_ago = timezone.now() - timedelta(days=30)
        new_customers = CustomerProfile.objects.filter(
            store=store, user__date_joined__gte=thirty_days_ago
        ).count()

        return Response(
            {
                "total_customers": total_customers,
                "new_customers_30_days": new_customers,
                "customer_growth_rate": (
                    (new_customers / total_customers * 100) if total_customers > 0 else 0
                ),
            }
        )


class CouponDashboardViewSet(viewsets.ModelViewSet):
    """Dashboard coupon management endpoints"""

    permission_classes = [IsAuthenticated, IsStoreAdmin]
    serializer_class = CouponDashboardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["store", "status", "campaign"]
    search_fields = ["code", "name"]

    def get_queryset(self):
        """Filter by current user's store"""
        return Coupon.objects.filter(store=self.request.store).select_related("campaign", "store")


class CouponCampaignDashboardViewSet(viewsets.ModelViewSet):
    """Dashboard coupon campaign management endpoints"""

    permission_classes = [IsAuthenticated, IsStoreAdmin]
    serializer_class = CouponCampaignDashboardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["store", "is_active"]
    search_fields = ["name", "description"]

    def get_queryset(self):
        """Filter by current user's store"""
        return CouponCampaign.objects.filter(store=self.request.store).select_related("store")


class PaymentMethodDashboardViewSet(viewsets.ModelViewSet):
    """Dashboard payment method management endpoints"""

    permission_classes = [IsAuthenticated, IsStoreAdmin]
    serializer_class = PaymentMethodDashboardSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["store", "is_active"]

    def get_queryset(self):
        """Filter by current user's store"""
        return PaymentMethod.objects.filter(store=self.request.store).select_related("store")


class PaymentDashboardViewSet(viewsets.ReadOnlyModelViewSet):
    """Dashboard payment viewing endpoints"""

    permission_classes = [IsAuthenticated, IsStoreAdmin]
    serializer_class = PaymentDashboardSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["store", "status", "payment_method"]
    search_fields = ["order__customer__username", "transaction_id"]
    ordering_fields = ["created_at", "amount"]

    def get_queryset(self):
        """Filter by current user's store"""
        return Payment.objects.filter(store=self.request.store).select_related(
            "order", "payment_method", "order__customer"
        )

    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get payment analytics"""
        store = request.store

        # Payment statistics
        total_payments = Payment.objects.filter(store=store).count()
        successful_payments = Payment.objects.filter(store=store, status="completed").count()
        failed_payments = Payment.objects.filter(store=store, status="failed").count()

        # Revenue analytics
        from django.db.models import Sum

        total_revenue = (
            Payment.objects.filter(store=store, status="completed").aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )

        return Response(
            {
                "total_payments": total_payments,
                "successful_payments": successful_payments,
                "failed_payments": failed_payments,
                "success_rate": (
                    (successful_payments / total_payments * 100) if total_payments > 0 else 0
                ),
                "total_revenue": round(total_revenue, 2),
            }
        )


class InventoryDashboardViewSet(viewsets.ModelViewSet):
    """Dashboard inventory management endpoints"""

    permission_classes = [IsAuthenticated, IsStoreAdmin]
    serializer_class = DashboardInventorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["store", "product"]
    search_fields = ["product__title", "product__sku"]

    def get_queryset(self):
        """Filter by current user's store"""
        return Inventory.objects.filter(store=self.request.store).select_related("product", "store")

    @action(detail=False, methods=["get"])
    def low_stock(self, request):
        """Get low stock items"""
        store = request.store
        threshold = request.query_params.get("threshold", 10)

        low_stock_items = Inventory.objects.filter(
            store=store, quantity__lte=threshold
        ).select_related("product")

        serializer = self.get_serializer(low_stock_items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get inventory analytics"""
        store = request.store

        total_products = Inventory.objects.filter(store=store).count()
        low_stock_products = Inventory.objects.filter(store=store, quantity__lte=10).count()
        out_of_stock_products = Inventory.objects.filter(store=store, quantity=0).count()

        return Response(
            {
                "total_products": total_products,
                "low_stock_products": low_stock_products,
                "out_of_stock_products": out_of_stock_products,
                "stock_health_rate": (
                    (
                        (total_products - low_stock_products - out_of_stock_products)
                        / total_products
                        * 100
                    )
                    if total_products > 0
                    else 0
                ),
            }
        )


class ProductVariantDashboardViewSet(viewsets.ModelViewSet):
    """Dashboard product variant management endpoints"""

    permission_classes = [IsAuthenticated, IsStoreAdmin]
    serializer_class = ProductVariantDashboardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["store", "product", "is_active"]
    search_fields = ["title", "sku", "product__title"]

    def get_queryset(self):
        """Filter by current user's store"""
        return ProductVariant.objects.filter(store=self.request.store).select_related(
            "product", "store"
        )
