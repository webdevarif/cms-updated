"""
Public ecommerce API.
"""

from apps.ecommerce.models.cart import Cart, CartItem
from apps.ecommerce.models.collections import ProductCollection
from apps.ecommerce.models.customers import CustomerProfile
from apps.ecommerce.models.products import Product, ProductCategory, ProductVariant

# Review model import removed - model doesn't exist
from drf_spectacular.utils import extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import (
    CartItemPublicSerializer,
    CartPublicSerializer,
    CollectionPublicSerializer,
    CustomerProfilePublicSerializer,
    ProductCategoryPublicSerializer,
    ProductPublicSerializer,
    ProductVariantPublicSerializer,
    ReviewPublicSerializer,
)


class ProductPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public product API - no authentication required.
    Provides read-only access to published products for browsing.
    """

    permission_classes = [AllowAny]
    serializer_class = ProductPublicSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "sku"]
    ordering_fields = ["title", "created_at", "price"]

    def get_queryset(self):
        """Filter by active products"""
        return Product.objects.filter(status="active").select_related("store", "category")

    @extend_schema(summary="List products", description="List available products for browsing")
    def list(self, request, *args, **kwargs):
        """List products"""
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Get product", description="Get product details")
    def retrieve(self, request, *args, **kwargs):
        """Get product"""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Get product variants", description="Get product variants")
    @action(detail=True, methods=["get"])
    def variants(self, request, pk=None):
        """Get product variants"""
        product = self.get_object()
        variants = product.variants.all()
        serializer = ProductVariantPublicSerializer(variants, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Get featured products", description="Get featured products")
    @action(detail=False, methods=["get"])
    def featured(self, request):
        """Get featured products"""
        featured_products = self.get_queryset().filter(is_featured=True)[:10]
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)


class ProductCategoryPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public product category API - no authentication required.
    """

    permission_classes = [AllowAny]
    serializer_class = ProductCategoryPublicSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "position"]

    def get_queryset(self):
        """Filter by active categories"""
        return ProductCategory.objects.filter(is_active=True).select_related("parent")


class CartPublicViewSet(viewsets.ModelViewSet):
    """
    Public cart API - session-based cart management.
    """

    permission_classes = [AllowAny]
    serializer_class = CartPublicSerializer

    def get_queryset(self):
        """Filter by session key"""
        session_key = self.request.session.session_key
        return Cart.objects.filter(session_key=session_key)

    def perform_create(self, serializer):
        """Create cart with session key"""
        serializer.save(session_key=self.request.session.session_key)


class CollectionPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public collection API - no authentication required.
    """

    permission_classes = [AllowAny]
    serializer_class = CollectionPublicSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        """Filter by active collections"""
        return ProductCollection.objects.filter(is_active=True).select_related("store")


class CustomerProfilePublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public customer profile API - read-only.
    """

    permission_classes = [AllowAny]
    serializer_class = CustomerProfilePublicSerializer

    def get_queryset(self):
        """No public access to customer profiles"""
        return CustomerProfile.objects.none()

    @extend_schema(summary="Get customer profile", description="Get customer profile (read-only)")
    def retrieve(self, request, *args, **kwargs):
        """Get customer profile"""
        # For public viewing, customer profiles are not accessible
        return Response(
            {"detail": "Customer profiles require authentication"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class ReviewPublicViewSet(viewsets.GenericViewSet):
    """Public review API - read-only list and create reviews"""

    permission_classes = [AllowAny]
    serializer_class = ReviewPublicSerializer

    def get_queryset(self):
        """Get reviews for a specific product"""
        product_id = self.kwargs.get("product_pk")
        if product_id:
            return Review.objects.filter(
                product_id=product_id,
                is_approved=True,
                parent__isnull=True,  # Only top-level reviews
            ).select_related("user", "product")
        return Review.objects.none()

    @extend_schema(
        summary="List product reviews",
        description="List approved reviews for a specific product",
    )
    def list(self, request, product_pk=None):
        """List approved reviews for a product"""
        from apps.ecommerce.services.review_service import ReviewService

        product = Product.objects.get(id=product_pk)
        reviews = ReviewService.get_product_reviews(product, approved_only=True)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def vote_helpful(self, request, pk=None):
        """Vote that a review is helpful"""
        review = self.get_object()

        if not review.is_approved:
            return Response({"error": "Cannot vote on unapproved reviews"}, status=400)

        # Check if user already voted (simple implementation - in production you'd use a separate Vote model)
        # For now, we'll just increment the vote count
        review.total_votes += 1
        review.helpful_votes += 1
        review.save(update_fields=["total_votes", "helpful_votes"])

        return Response(
            {
                "helpful_votes": review.helpful_votes,
                "total_votes": review.total_votes,
                "helpfulness_percentage": review.helpfulness_percentage,
            }
        )

    @action(detail=True, methods=["post"])
    def report_abuse(self, request, pk=None):
        """Report a review for abuse"""
        review = self.get_object()

        # Increment abuse reports count
        review.abuse_reports_count += 1
        review.save(update_fields=["abuse_reports_count"])

        # Optionally hide review if it reaches a threshold
        if review.abuse_reports_count >= 5:  # Configurable threshold
            review.is_hidden = True
            review.save(update_fields=["is_hidden"])

            # Send notification to moderators
            from apps.notifications.services import NotificationService

            try:
                NotificationService.create_notification(
                    user=None,  # System notification to all moderators
                    notification_type="review_abuse",
                    title="Review hidden due to abuse reports",
                    message=f'Review "{review.title}" has been hidden due to {review.abuse_reports_count} abuse reports',
                    data={
                        "review_id": review.id,
                        "product_id": review.product.id,
                        "abuse_reports_count": review.abuse_reports_count,
                    },
                    store=review.product.store,
                )
            except Exception as e:
                print(f"Failed to send abuse notification: {e}")

        return Response(
            {
                "message": "Abuse report submitted",
                "abuse_reports_count": review.abuse_reports_count,
                "is_hidden": review.is_hidden,
            }
        )

    @extend_schema(
        summary="Create product review",
        description="Create a new review for a product (goes to moderation queue)",
    )
    def create(self, request, product_pk=None):
        """Create a new review on a product"""
        from apps.ecommerce.models.products import Product

        try:
            product = Product.objects.get(id=product_pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if product is active
        if product.status != "active":
            return Response(
                {"error": "Cannot review inactive products"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(
            data=request.data, context={"request": request, "product_id": product.id}
        )
        serializer.is_valid(raise_exception=True)
        review = serializer.save()

        # Return the created review
        response_serializer = self.get_serializer(review)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
