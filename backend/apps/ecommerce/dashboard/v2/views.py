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
from apps.ecommerce.models.reviews import Review
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
    ReviewDashboardSerializer,
)


class DashboardProductViewSet(viewsets.ModelViewSet):
    """
    Dashboard product management endpoints with advanced filtering and search.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = DashboardProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description", "sku"]
    ordering_fields = ["created_at", "name", "price"]

    def get_queryset(self):
        """Filter by current user's stores"""
        return Product.objects.filter(
            store__in=self.request.user.stores_owned.all()
        ).select_related("store")

    @extend_schema(
        summary="List products", description="List all products with filtering and search"
    )
    def list(self, request, *args, **kwargs):
        """List products"""
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Create product", description="Create new product")
    def create(self, request, *args, **kwargs):
        """Create product"""
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Get product", description="Get product details")
    def retrieve(self, request, *args, **kwargs):
        """Get product"""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Update product", description="Update product details")
    def update(self, request, *args, **kwargs):
        """Update product"""
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Partial update product", description="Partially update product details")
    def partial_update(self, request, *args, **kwargs):
        """Partial update product"""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary="Delete product", description="Delete product")
    def destroy(self, request, *args, **kwargs):
        """Delete product"""
        return super().destroy(request, *args, **kwargs)

    @extend_schema(summary="Toggle product status", description="Activate or deactivate product")
    @action(detail=True, methods=["post"])
    def toggle_status(self, request, pk=None):
        """Toggle product active status"""
        product = self.get_object()
        product.is_active = not product.is_active
        product.save()
        return Response(
            {
                "is_active": product.is_active,
                "message": f'Product {"activated" if product.is_active else "deactivated"} successfully',
            }
        )

    @extend_schema(summary="Get product analytics", description="Get product analytics data")
    @action(detail=True, methods=["get"])
    def analytics(self, request, pk=None):
        """Get product analytics"""
        product = self.get_object()

        # Calculate analytics
        from apps.ecommerce.models.cart import CartItem
        from django.db.models import Sum

        total_revenue = (
            CartItem.objects.filter(product=product, cart__status="completed").aggregate(
                total=Sum("price")
            )["total"]
            or 0
        )

        total_orders = CartItem.objects.filter(product=product, cart__status="completed").count()

        return Response(
            {
                "total_revenue": total_revenue,
                "total_orders": total_orders,
                "average_order_value": total_revenue / total_orders if total_orders > 0 else 0,
            }
        )


class DashboardInventoryViewSet(viewsets.ModelViewSet):
    """
    Dashboard inventory management endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = DashboardInventorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["product__name", "product__sku"]
    ordering_fields = ["product__name", "quantity", "updated_at"]

    def get_queryset(self):
        """Filter by current user's stores"""
        return Inventory.objects.filter(
            product__store__in=self.request.user.stores_owned.all()
        ).select_related("product", "product__store")

    @extend_schema(summary="List inventory", description="List all inventory records")
    def list(self, request, *args, **kwargs):
        """List inventory"""
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Update inventory", description="Update inventory quantity")
    @action(detail=True, methods=["post"])
    def update_quantity(self, request, pk=None):
        """Update inventory quantity"""
        inventory = self.get_object()
        new_quantity = request.data.get("quantity")

        if new_quantity is not None and new_quantity >= 0:
            inventory.quantity = new_quantity
            inventory.save()

        serializer = self.get_serializer(inventory)
        return Response(serializer.data)

    @extend_schema(summary="Low stock alert", description="Get low stock items")
    @action(detail=False, methods=["get"])
    def low_stock(self, request):
        """Get low stock items"""
        low_stock = self.get_queryset().filter(quantity__lte=F("product__low_stock_threshold"))

        serializer = self.get_serializer(low_stock, many=True)
        return Response(serializer.data)


class DashboardCollectionViewSet(viewsets.ModelViewSet):
    """
    Dashboard collection management endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        """Filter by current user's stores"""
        return ProductCollection.objects.filter(
            store__in=self.request.user.stores_owned.all()
        ).select_related("store")

    @extend_schema(summary="List collections", description="List all collections")
    def list(self, request, *args, **kwargs):
        """List collections"""
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Create collection", description="Create new collection")
    def create(self, request, *args, **kwargs):
        """Create collection"""
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Get collection", description="Get collection details")
    def retrieve(self, request, *args, **kwargs):
        """Get collection"""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Update collection", description="Update collection")
    def update(self, request, *args, **kwargs):
        """Update collection"""
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Partial update collection", description="Partially update collection")
    def partial_update(self, request, *args, **kwargs):
        """Partial update collection"""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary="Delete collection", description="Delete collection")
    def destroy(self, request, *args, **kwargs):
        """Delete collection"""
        return super().destroy(request, *args, **kwargs)


class ProductCategoryDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard product category management endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = ProductCategoryDashboardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "position", "created_at"]

    def get_queryset(self):
        """Filter by current user's store"""
        return ProductCategory.objects.filter(store=self.request.store).select_related("parent")

    def perform_create(self, serializer):
        """Set store when creating category"""
        serializer.save(store=self.request.store)


class ProductVariantDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard product variant management endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = ProductVariantDashboardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "sku"]
    ordering_fields = ["position", "title", "price"]

    def get_queryset(self):
        """Filter by current user's store"""
        return ProductVariant.objects.filter(product__store=self.request.store).select_related(
            "product"
        )


class CartDashboardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Dashboard cart viewing endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = CartDashboardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["user__email", "user__username"]
    ordering_fields = ["created_at", "updated_at"]

    def get_queryset(self):
        """Filter by current user's store"""
        return Cart.objects.filter(store=self.request.store).select_related("user", "store")


class OrderDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard order management endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = OrderDashboardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["order_number", "customer_email", "customer_phone"]
    ordering_fields = ["created_at", "order_number", "status"]
    filterset_fields = ["status"]

    def get_queryset(self):
        """Filter by current user's store"""
        return Order.objects.filter(store=self.request.store).select_related("customer", "store")

    def perform_create(self, serializer):
        """Set store when creating order"""
        serializer.save(store=self.request.store)

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        """Update order status"""
        order = self.get_object()
        new_status = request.data.get("status")

        if new_status in [
            "pending",
            "confirmed",
            "processing",
            "shipped",
            "delivered",
            "cancelled",
        ]:
            order.status = new_status
            order.save()
            return Response({"message": f"Order status updated to {new_status}"})

        return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)


class OrderItemDashboardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Dashboard order item viewing endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = OrderItemDashboardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["product__title", "product__sku"]
    ordering_fields = ["created_at", "unit_price", "quantity"]

    def get_queryset(self):
        """Filter by current user's store"""
        return OrderItem.objects.filter(order__store=self.request.store).select_related(
            "product", "order"
        )


class CouponCampaignDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard coupon campaign management endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = CouponCampaignDashboardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "name", "starts_at"]
    filterset_fields = ["discount_type", "is_active"]

    def get_queryset(self):
        """Filter by current user's store"""
        return CouponCampaign.objects.filter(store=self.request.store).select_related("store")

    def perform_create(self, serializer):
        """Set store when creating campaign"""
        serializer.save(store=self.request.store)

    @action(detail=True, methods=["post"])
    def generate_coupons(self, request, pk=None):
        """Generate coupons for campaign"""
        campaign = self.get_object()
        count = request.data.get("count", 1)

        coupons = []
        for i in range(count):
            coupon = Coupon.objects.create(
                campaign=campaign, code=f"{campaign.name.upper()}-{i+1:03d}"
            )
            coupons.append(coupon)

        return Response(
            {
                "message": f"Generated {count} coupons",
                "coupons": CouponDashboardSerializer(coupons, many=True).data,
            }
        )


class CouponDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard coupon management endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = CouponDashboardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["code"]
    ordering_fields = ["created_at", "used_at"]
    filterset_fields = ["status"]

    def get_queryset(self):
        """Filter by current user's store"""
        return Coupon.objects.filter(campaign__store=self.request.store).select_related(
            "campaign", "customer", "order"
        )


class PaymentMethodDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard payment method management endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = PaymentMethodDashboardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "display_name"]
    ordering_fields = ["name", "method_type", "created_at"]
    filterset_fields = ["method_type", "is_active"]

    def get_queryset(self):
        """Filter by current user's store"""
        return PaymentMethod.objects.filter(store=self.request.store).select_related("store")

    def perform_create(self, serializer):
        """Set store when creating payment method"""
        serializer.save(store=self.request.store)


class PaymentDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard payment management endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = PaymentDashboardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["gateway_transaction_id", "customer_email"]
    ordering_fields = ["created_at", "amount", "status"]
    filterset_fields = ["status", "payment_method"]

    def get_queryset(self):
        """Filter by current user's store"""
        return Payment.objects.filter(order__store=self.request.store).select_related(
            "order", "payment_method"
        )

    @action(detail=True, methods=["post"])
    def refund(self, request, pk=None):
        """Process refund"""
        payment = self.get_object()
        amount = request.data.get("amount")
        reason = request.data.get("reason", "")

        try:
            payment.refund(amount, reason)
            return Response({"message": "Refund processed successfully"})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CustomerProfileDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard customer profile management endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = CustomerProfileDashboardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["user__email", "user__username", "phone"]
    ordering_fields = ["created_at", "user__email"]

    def get_queryset(self):
        """Filter by current user's store"""
        return CustomerProfile.objects.filter(
            user__orders__store=self.request.store
        ).select_related("user")


class EcommerceAnalyticsViewSet(viewsets.ViewSet):
    """
    Ecommerce analytics and reporting endpoints.
    Provides comprehensive business intelligence for store performance.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]

    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get comprehensive ecommerce analytics with time-range filtering"""
        store = getattr(request, "store", None)
        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        # Parse time range parameters
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        date_filter = {}
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                date_filter["created_at__gte"] = start_dt
            except ValueError:
                return Response(
                    {"error": "Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                date_filter["created_at__lte"] = end_dt
            except ValueError:
                return Response(
                    {"error": "Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            # Revenue and order analytics
            orders = Order.objects.filter(store=store, **date_filter)
            total_orders = orders.count()
            completed_orders = orders.filter(status="completed")
            total_revenue = completed_orders.aggregate(total=Sum("total_amount"))["total"] or 0

            avg_order_value = completed_orders.aggregate(avg=Avg("total_amount"))["avg"] or 0

            # Product analytics
            products = Product.objects.filter(store=store)
            total_products = products.count()
            published_products = products.filter(status="published").count()
            out_of_stock = products.filter(inventory__quantity__lte=0).distinct().count()

            # Customer analytics
            customers = CustomerProfile.objects.filter(
                user__orders__store=store, **date_filter
            ).distinct()
            total_customers = customers.count()

            new_customers = (
                customers.filter(created_at__range=[start_date, end_date])
                if start_date and end_date
                else 0
            )

            # Category performance
            category_sales = (
                OrderItem.objects.filter(
                    order__store=store,
                    order__status="completed",
                    order__created_at__range=[start_date, end_date]
                    if start_date and end_date
                    else [timezone.now() - timedelta(days=30), timezone.now()],
                )
                .values("product__categories__name")
                .annotate(
                    revenue=Sum(F("quantity") * F("price")), orders=Count("order", distinct=True)
                )
                .order_by("-revenue")[:10]
            )

            categories = []
            for cat in category_sales:
                if cat["product__categories__name"]:
                    categories.append(
                        {
                            "name": cat["product__categories__name"],
                            "revenue": float(cat["revenue"] or 0),
                            "orders": cat["orders"],
                        }
                    )

            # Top products
            top_products = (
                OrderItem.objects.filter(
                    order__store=store,
                    order__status="completed",
                    order__created_at__range=[start_date, end_date]
                    if start_date and end_date
                    else [timezone.now() - timedelta(days=30), timezone.now()],
                )
                .values("product__name", "product__id")
                .annotate(
                    revenue=Sum(F("quantity") * F("price")),
                    units_sold=Sum("quantity"),
                    orders=Count("order", distinct=True),
                )
                .order_by("-revenue")[:10]
            )

            products_data = []
            for prod in top_products:
                products_data.append(
                    {
                        "id": prod["product__id"],
                        "name": prod["product__name"],
                        "revenue": float(prod["revenue"] or 0),
                        "units_sold": prod["units_sold"],
                        "orders": prod["orders"],
                    }
                )

            # Revenue trends (daily)
            revenue_trends = []
            if start_date and end_date:
                from django.db.models.functions import TruncDate

                daily_revenue = (
                    completed_orders.annotate(date=TruncDate("created_at"))
                    .values("date")
                    .annotate(revenue=Sum("total_amount"), orders=Count("id"))
                    .order_by("date")
                )

                revenue_trends = [
                    {
                        "date": str(item["date"]),
                        "revenue": float(item["revenue"] or 0),
                        "orders": item["orders"],
                    }
                    for item in daily_revenue
                ]

            analytics_data = {
                "overview": {
                    "total_orders": total_orders,
                    "completed_orders": completed_orders.count(),
                    "total_revenue": float(total_revenue),
                    "avg_order_value": float(avg_order_value),
                    "total_products": total_products,
                    "published_products": published_products,
                    "out_of_stock_products": out_of_stock,
                    "total_customers": total_customers,
                    "new_customers": new_customers
                    if isinstance(new_customers, int)
                    else new_customers.count(),
                },
                "revenue": {
                    "total": float(total_revenue),
                    "average_order_value": float(avg_order_value),
                    "trends": revenue_trends,
                },
                "products": {
                    "top_performers": products_data,
                    "out_of_stock_count": out_of_stock,
                    "publish_rate": (published_products / total_products * 100)
                    if total_products > 0
                    else 0,
                },
                "categories": categories,
                "customers": {
                    "total": total_customers,
                    "new": new_customers
                    if isinstance(new_customers, int)
                    else new_customers.count(),
                    "avg_orders_per_customer": total_orders / total_customers
                    if total_customers > 0
                    else 0,
                },
                "time_range": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "has_date_filter": bool(start_date or end_date),
                },
            }

            return Response(analytics_data)

        except Exception as e:
            return Response(
                {"error": f"Analytics failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ReviewDashboardViewSet(viewsets.ModelViewSet):
    """Dashboard review API - full moderation and analytics"""

    permission_classes = [IsAuthenticated, IsStoreAdmin]
    serializer_class = ReviewDashboardSerializer

    def get_queryset(self):
        """Get all reviews for moderation"""
        store_id = self.request.query_params.get("store")
        queryset = Review.objects.all()
        if store_id:
            queryset = queryset.filter(product__store_id=store_id)
        return queryset.select_related("user", "product")

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "moderate":
            return ReviewModerationSerializer
        elif self.action == "analytics":
            return ReviewAnalyticsSerializer
        elif self.action == "reply_as_seller":
            return ReplyAsSellerSerializer
        return ReviewDashboardSerializer

    def list(self, request, *args, **kwargs):
        """List reviews with filtering options"""
        queryset = self.get_queryset()

        # Filter by approval status
        approved = request.query_params.get("approved")
        if approved is not None:
            queryset = queryset.filter(is_approved=approved.lower() == "true")

        # Filter by featured status
        featured = request.query_params.get("featured")
        if featured is not None:
            queryset = queryset.filter(is_featured=featured.lower() == "true")

        # Filter by product
        product_id = request.query_params.get("product_id")
        if product_id:
            queryset = queryset.filter(product_id=product_id)

        # Filter by rating
        rating = request.query_params.get("rating")
        if rating:
            queryset = queryset.filter(rating=rating)

        # Filter by date range
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        # Order by creation date (newest first)
        queryset = queryset.order_by("-created_at")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Moderate review (approve/reject/feature)"""
        instance = self.get_object()
        action = request.data.get("action")

        try:
            from apps.ecommerce.services.review_service import ReviewService

            if action == "approve":
                ReviewService.approve_review(instance, request.user)
            elif action == "reject":
                reason = request.data.get("reason", "Rejected by moderator")
                ReviewService.reject_review(instance, request.user, reason)
            elif action == "feature":
                instance.is_featured = True
                instance.save(update_fields=["is_featured"])
            elif action == "unfeature":
                instance.is_featured = False
                instance.save(update_fields=["is_featured"])
            else:
                return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Hard delete review (admin only)"""
        instance = self.get_object()

        try:
            from apps.ecommerce.services.review_service import ReviewService

            ReviewService.delete_review(instance, request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def moderate(self, request):
        """Bulk moderation actions"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data["action"]
        review_ids = serializer.validated_data["review_ids"]
        reason = serializer.validated_data.get("reason")

        try:
            from apps.ecommerce.services.review_service import ReviewService

            moderated_count = 0
            for review_id in review_ids:
                try:
                    review = Review.objects.get(id=review_id)

                    if action == "approve":
                        ReviewService.approve_review(review, request.user)
                    elif action == "reject":
                        ReviewService.reject_review(review, request.user, reason)
                    elif action == "feature":
                        review.is_featured = True
                        review.save(update_fields=["is_featured"])
                    elif action == "unfeature":
                        review.is_featured = False
                        review.save(update_fields=["is_featured"])
                    elif action == "delete":
                        ReviewService.delete_review(review, request.user)

                    moderated_count += 1

                except Review.DoesNotExist:
                    continue

            return Response(
                {
                    "message": f"Successfully moderated {moderated_count} reviews",
                    "action": action,
                    "moderated_count": moderated_count,
                }
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get comprehensive review analytics"""
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        days = serializer.validated_data.get("days", 30)
        approved_only = serializer.validated_data.get("approved_only", False)

        # Parse date filters
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        try:
            from apps.ecommerce.services.review_service import ReviewService
            from django.db.models import Avg, Count, Q
            from django.utils import timezone

            store = getattr(request.user, "store", None)

            # Base analytics from service
            analytics = ReviewService.get_review_analytics(store=store, days=days)

            # Enhanced analytics with date filtering and additional metrics
            start_dt = None
            end_dt = None

            if start_date:
                start_dt = timezone.datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            if end_date:
                end_dt = timezone.datetime.fromisoformat(end_date.replace("Z", "+00:00"))

            # If custom date range provided, override days
            if start_dt or end_dt:
                if not start_dt:
                    start_dt = timezone.now() - timezone.timedelta(days=30)
                if not end_dt:
                    end_dt = timezone.now()

                # Recalculate analytics for custom date range
                queryset = Review.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt)
                if store:
                    queryset = queryset.filter(product__store=store)

                analytics = {
                    "total_reviews": queryset.count(),
                    "approved_reviews": queryset.filter(is_approved=True).count(),
                    "pending_reviews": queryset.filter(moderation_status="pending").count(),
                    "rejected_reviews": queryset.filter(moderation_status="rejected").count(),
                    "verified_reviews": queryset.filter(verified_purchase=True).count(),
                    "featured_reviews": queryset.filter(is_featured=True).count(),
                    "average_rating": round(
                        queryset.filter(is_approved=True).aggregate(avg=Avg("rating"))["avg"] or 0,
                        1,
                    ),
                    "reviews_by_day": queryset.extra(select={"day": "DATE(created_at)"})
                    .values("day")
                    .annotate(count=Count("id"))
                    .order_by("day"),
                    "rating_distribution": {
                        star: queryset.filter(rating=star, is_approved=True).count()
                        for star in range(1, 6)
                    },
                }

            # Add top reviewers
            top_reviewers = (
                Review.objects.filter(
                    product__store=store if store else Q(),
                    is_approved=True,
                    created_at__gte=timezone.now() - timezone.timedelta(days=days),
                )
                .values("user__username", "user__get_display_name")
                .annotate(review_count=Count("id"), avg_rating=Avg("rating"))
                .order_by("-review_count")[:10]
            )

            # Add top products by reviews
            top_products = (
                Review.objects.filter(
                    product__store=store if store else Q(),
                    is_approved=True,
                    created_at__gte=timezone.now() - timezone.timedelta(days=days),
                )
                .values("product__title", "product__id")
                .annotate(
                    review_count=Count("id"),
                    avg_rating=Avg("rating"),
                    verified_reviews=Count("id", filter=Q(verified_purchase=True)),
                )
                .order_by("-review_count")[:10]
            )

            # Add moderation statistics
            moderation_stats = {
                "pending_review": Review.objects.filter(
                    product__store=store if store else Q(),
                    moderation_status="pending",
                    created_at__gte=timezone.now() - timezone.timedelta(days=days),
                ).count(),
                "recently_approved": Review.objects.filter(
                    product__store=store if store else Q(),
                    moderation_status="approved",
                    approved_at__gte=timezone.now() - timezone.timedelta(days=days),
                ).count(),
                "recently_rejected": Review.objects.filter(
                    product__store=store if store else Q(),
                    moderation_status="rejected",
                    updated_at__gte=timezone.now() - timezone.timedelta(days=days),
                ).count(),
                "featured_reviews": Review.objects.filter(
                    product__store=store if store else Q(),
                    is_featured=True,
                    created_at__gte=timezone.now() - timezone.timedelta(days=days),
                ).count(),
            }

            # Add rating trend analysis
            rating_trends = []
            for i in range(days, 0, -7):  # Weekly data points
                week_start = timezone.now() - timezone.timedelta(days=i - 7)
                week_end = (
                    timezone.now() - timezone.timedelta(days=i - 14) if i > 7 else timezone.now()
                )

                week_reviews = Review.objects.filter(
                    product__store=store if store else Q(),
                    is_approved=True,
                    created_at__gte=week_start,
                    created_at__lte=week_end,
                )

                if week_reviews.exists():
                    avg_rating = week_reviews.aggregate(avg=Avg("rating"))["avg"]
                    rating_trends.append(
                        {
                            "week_start": week_start.date().isoformat(),
                            "week_end": week_end.date().isoformat(),
                            "review_count": week_reviews.count(),
                            "average_rating": round(avg_rating, 1) if avg_rating else 0,
                        }
                    )

            # Filter approved-only if requested
            if approved_only:
                analytics = {
                    k: v
                    for k, v in analytics.items()
                    if "approved" in k.lower() or "total" in k.lower() or "average" in k.lower()
                }

            # Combine all analytics
            full_analytics = {
                **analytics,
                "top_reviewers": list(top_reviewers),
                "top_products": list(top_products),
                "moderation_stats": moderation_stats,
                "rating_trends": rating_trends,
                "time_range": {
                    "start_date": (
                        start_dt or (timezone.now() - timezone.timedelta(days=days))
                    ).isoformat(),
                    "end_date": (end_dt or timezone.now()).isoformat(),
                    "days": days,
                    "has_custom_range": bool(start_date or end_date),
                },
            }

            return Response(full_analytics)

        except Exception as e:
            return Response(
                {"error": f"Analytics failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def reply_as_seller(self, request, pk=None):
        """Reply to a review as seller/admin (auto-approved)"""
        parent_review = self.get_object()

        # Check if user can reply
        if not parent_review.can_reply(request.user):
            return Response(
                {"error": "You cannot reply to this review"}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(
            data=request.data,
            context={
                "request": request,
                "parent_id": parent_review.id,
                "product_id": parent_review.product.id,
            },
        )
        serializer.is_valid(raise_exception=True)
        reply = serializer.save()

        # Return the created reply
        response_serializer = ReviewDashboardSerializer(reply, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def pending(self, request):
        """Get all pending reviews for moderation"""
        queryset = Review.objects.filter(moderation_status="pending").select_related(
            "user", "product"
        )

        # Filter by store if specified
        store_id = request.query_params.get("store")
        if store_id:
            queryset = queryset.filter(product__store_id=store_id)

        # Order by creation date (oldest first for moderation priority)
        queryset = queryset.order_by("created_at")

        # Add pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a pending review"""
        review = self.get_object()

        try:
            from apps.ecommerce.services.review_service import ReviewService

            ReviewService.moderate_review(review, "approve", request.user)

            # Get updated review with moderation history
            serializer = self.get_serializer(review)
            response_data = serializer.data
            response_data["moderation_history"] = [
                {
                    "action": "approved",
                    "moderator": request.user.get_display_name(),
                    "timestamp": review.approved_at.isoformat() if review.approved_at else None,
                    "reason": None,
                }
            ]

            return Response(response_data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject a review with optional reason"""
        review = self.get_object()
        reason = request.data.get("reason", "Rejected by moderator")

        try:
            from apps.ecommerce.services.review_service import ReviewService

            ReviewService.moderate_review(review, "reject", request.user, reason)

            # Get updated review with moderation history
            serializer = self.get_serializer(review)
            response_data = serializer.data
            response_data["moderation_history"] = [
                {
                    "action": "rejected",
                    "moderator": request.user.get_display_name(),
                    "timestamp": timezone.now().isoformat(),
                    "reason": reason,
                }
            ]

            return Response(response_data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def feature(self, request, pk=None):
        """Feature or unfeature a review"""
        review = self.get_object()
        action = request.data.get("action", "feature")  # 'feature' or 'unfeature'

        try:
            if action == "feature":
                review.is_featured = True
                action_name = "featured"
            elif action == "unfeature":
                review.is_featured = False
                action_name = "unfeatured"
            else:
                return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

            review.save(update_fields=["is_featured"])

            # Get updated review with moderation history
            serializer = self.get_serializer(review)
            response_data = serializer.data
            response_data["moderation_history"] = [
                {
                    "action": action_name,
                    "moderator": request.user.get_display_name(),
                    "timestamp": timezone.now().isoformat(),
                    "reason": None,
                }
            ]

            return Response(response_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def bulk_moderate(self, request):
        """Bulk moderate multiple reviews"""
        serializer = ReviewModerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data["action"]
        review_ids = serializer.validated_data["review_ids"]
        reason = serializer.validated_data.get("reason")

        try:
            from apps.ecommerce.services.review_service import ReviewService
            from django.utils import timezone

            moderated_reviews = []
            moderation_history = []

            for review_id in review_ids:
                try:
                    review = Review.objects.get(id=review_id)
                    ReviewService.moderate_review(review, action, request.user, reason)

                    moderated_reviews.append(review)
                    moderation_history.append(
                        {
                            "review_id": review.id,
                            "action": action,
                            "moderator": request.user.get_display_name(),
                            "timestamp": timezone.now().isoformat(),
                            "reason": reason,
                        }
                    )

                except Review.DoesNotExist:
                    continue
                except ValidationError:
                    continue

            return Response(
                {
                    "message": f"Successfully moderated {len(moderated_reviews)} reviews",
                    "action": action,
                    "moderated_count": len(moderated_reviews),
                    "moderation_history": moderation_history,
                }
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def bulk_mark_spam(self, request):
        """Bulk mark multiple reviews as spam"""
        serializer = ReviewModerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review_ids = serializer.validated_data["review_ids"]
        reason = serializer.validated_data.get("reason", "Marked as spam by moderator")

        try:
            from apps.ecommerce.services.review_service import ReviewService
            from django.utils import timezone

            marked_reviews = []
            moderation_history = []

            for review_id in review_ids:
                try:
                    review = Review.objects.get(id=review_id)
                    # Mark as spam (similar to comments - set is_spam=True, is_approved=False)
                    review.is_spam = True
                    review.is_approved = False
                    review.save(update_fields=["is_spam", "is_approved"])

                    marked_reviews.append(review)
                    moderation_history.append(
                        {
                            "review_id": review.id,
                            "action": "marked_spam",
                            "moderator": request.user.get_display_name(),
                            "timestamp": timezone.now().isoformat(),
                            "reason": reason,
                        }
                    )

                except Review.DoesNotExist:
                    continue
                except ValidationError:
                    continue

            return Response(
                {
                    "message": f"Successfully marked {len(marked_reviews)} reviews as spam",
                    "marked_count": len(marked_reviews),
                    "moderation_history": moderation_history,
                }
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def moderation_queue(self, request):
        """Get pending reviews for moderation"""
        queryset = Review.objects.filter(moderation_status="pending")

        # Filter by store if specified
        store_id = request.query_params.get("store")
        if store_id:
            queryset = queryset.filter(product__store_id=store_id)

        # Order by creation date (oldest first for moderation priority)
        queryset = queryset.order_by("created_at")

        # Add pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a pending review"""
        review = self.get_object()

        try:
            from apps.ecommerce.services.review_service import ReviewService

            ReviewService.moderate_review(review, "approve", request.user)
            serializer = self.get_serializer(review)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject a review with optional reason"""
        review = self.get_object()
        reason = request.data.get("reason", "Rejected by moderator")

        try:
            from apps.ecommerce.services.review_service import ReviewService

            ReviewService.moderate_review(review, "reject", request.user, reason)
            serializer = self.get_serializer(review)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
