"""
Customer ecommerce API.
"""
from apps.ecommerce.models.cart import Cart, CartItem
from apps.ecommerce.models.collections import ProductCollection
from apps.ecommerce.models.coupons import Coupon, CouponCampaign
from apps.ecommerce.models.customers import CustomerProfile
from apps.ecommerce.models.orders import Order, OrderItem
from apps.ecommerce.models.payments import Payment, PaymentMethod
from apps.ecommerce.models.products import Product, ProductCategory, ProductVariant
from apps.ecommerce.services.ecommerce_service import EcommerceService
from core.permissions import IsStoreUser
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    CartCustomerSerializer,
    CartItemCustomerSerializer,
    CollectionCustomerSerializer,
    CouponCustomerSerializer,
    CustomerProfileCustomerSerializer,
    OrderCustomerSerializer,
    OrderItemCustomerSerializer,
    PaymentCustomerSerializer,
    PaymentMethodCustomerSerializer,
    ProductCategoryCustomerSerializer,
    ProductCustomerSerializer,
)


class ProductCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer product viewing endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = ProductCustomerSerializer

    def get_queryset(self):
        """Filter by current user's store"""
        return Product.objects.filter(store=self.request.store, status="active").select_related(
            "store", "category"
        )


class ProductCategoryCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer product category viewing endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = ProductCategoryCustomerSerializer

    def get_queryset(self):
        """Filter by current user's store"""
        return ProductCategory.objects.filter(
            store=self.request.store, is_active=True
        ).select_related("parent")


class CartCustomerViewSet(viewsets.ModelViewSet):
    """
    Customer cart management endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = CartCustomerSerializer

    def get_queryset(self):
        """Filter by current user"""
        return Cart.objects.filter(user=self.request.user, store=self.request.store).select_related(
            "store"
        )

    def get_object(self):
        """Get or create customer cart"""
        cart, created = Cart.objects.get_or_create(user=self.request.user, store=self.request.store)
        return cart

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        """Add item to cart"""
        cart = self.get_object()
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        try:
            product = Product.objects.get(id=product_id, store=self.request.store)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={"quantity": quantity, "unit_price": product.price},
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return Response({"message": "Item added to cart"})
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"])
    def remove_item(self, request):
        """Remove item from cart"""
        cart = self.get_object()
        item_id = request.data.get("item_id")

        try:
            item = cart.items.get(id=item_id)
            item.delete()
            return Response({"message": "Item removed from cart"})
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"])
    def clear_cart(self, request):
        """Clear cart"""
        cart = self.get_object()
        cart.items.all().delete()
        return Response({"message": "Cart cleared"})


class OrderCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer order viewing endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = OrderCustomerSerializer

    def get_queryset(self):
        """Filter by current user's orders"""
        return Order.objects.filter(
            customer=self.request.user, store=self.request.store
        ).select_related("store")

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel order"""
        order = self.get_object()
        if order.can_cancel:
            order.status = "cancelled"
            order.save()
            return Response({"message": "Order cancelled"})
        return Response({"error": "Order cannot be cancelled"}, status=status.HTTP_400_BAD_REQUEST)


class CollectionCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer collection viewing endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = CollectionCustomerSerializer

    def get_queryset(self):
        """Filter by current user's store"""
        return ProductCollection.objects.filter(
            store=self.request.store, is_active=True
        ).select_related("store")


class CustomerProfileCustomerViewSet(viewsets.ModelViewSet):
    """
    Customer profile management endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = CustomerProfileCustomerSerializer

    def get_object(self):
        """Get or create customer profile"""
        profile, created = CustomerProfile.objects.get_or_create(
            user=self.request.user, defaults={"phone": "", "address": "", "city": "", "country": ""}
        )
        return profile


class CouponCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer coupon viewing endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = CouponCustomerSerializer

    def get_queryset(self):
        """Filter by current user's coupons"""
        return Coupon.objects.filter(customer=self.request.user, status="active").select_related(
            "campaign"
        )


class PaymentMethodCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer payment method viewing endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = PaymentMethodCustomerSerializer

    def get_queryset(self):
        """Filter by active payment methods"""
        return PaymentMethod.objects.filter(store=self.request.store, is_active=True)


class PaymentCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer payment viewing endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = PaymentCustomerSerializer

    def get_queryset(self):
        """Filter by current user's payments"""
        return Payment.objects.filter(order__customer=self.request.user).select_related(
            "order", "payment_method"
        )


class ReviewCustomerViewSet(viewsets.ModelViewSet):
    """Customer review API - manage own reviews and replies"""

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = ReviewCustomerSerializer

    def get_queryset(self):
        """Get reviews for current user"""
        return Review.objects.filter(
            user=self.request.user, parent__isnull=True  # Only top-level reviews, not replies
        ).select_related("product", "user")

    def perform_create(self, serializer):
        """Create review is handled in serializer"""
        pass

    def update(self, request, *args, **kwargs):
        """Update own review"""
        instance = self.get_object()

        # Check ownership
        if instance.user != request.user:
            return Response(
                {"error": "You can only edit your own reviews"}, status=status.HTTP_403_FORBIDDEN
            )

        # Check if already approved (can't edit approved reviews)
        if instance.is_approved:
            return Response(
                {"error": "Cannot edit approved reviews"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Delete own review"""
        instance = self.get_object()

        # Check ownership
        if instance.user != request.user:
            return Response(
                {"error": "You can only delete your own reviews"}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            from apps.ecommerce.services.review_service import ReviewService

            ReviewService.delete_review(instance, request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def reply(self, request, pk=None):
        """Reply to a review (if user is seller/admin)"""
        parent_review = self.get_object()

        # Check if user can reply
        if not parent_review.can_reply(request.user):
            return Response(
                {"error": "You cannot reply to this review"}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = ReplyCreateSerializer(
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
        response_serializer = ReviewCustomerSerializer(reply, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def helpful(self, request, pk=None):
        """Mark review as helpful"""
        review = self.get_object()

        try:
            from apps.ecommerce.services.review_service import ReviewService

            ReviewService.add_helpful_vote(review, request.user, helpful=True)
            return Response({"message": "Review marked as helpful"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
