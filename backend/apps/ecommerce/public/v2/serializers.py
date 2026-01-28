"""
Public ecommerce serializers.
"""
from apps.ecommerce.models.cart import Cart, CartItem
from apps.ecommerce.models.collections import ProductCollection
from apps.ecommerce.models.customers import CustomerProfile
from apps.ecommerce.models.products import Product, ProductCategory, ProductVariant
from apps.ecommerce.models.review import Review
from rest_framework import serializers


class ProductCategoryPublicSerializer(serializers.ModelSerializer):
    """Public product category serializer"""

    class Meta:
        model = ProductCategory
        fields = ["id", "name", "slug", "description", "image", "parent"]


class ProductPublicSerializer(serializers.ModelSerializer):
    """Public product serializer"""

    category_name = serializers.CharField(source="category.name", read_only=True)
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "price",
            "compare_at_price",
            "sku",
            "category",
            "category_name",
            "is_featured",
            "tags",
            "avg_rating",
            "review_count",
            "created_at",
            "updated_at",
        ]

    def get_avg_rating(self, obj):
        """Get average rating for the product"""
        from apps.ecommerce.services.review_service import ReviewService

        summary = ReviewService.get_product_rating_summary(obj)
        return summary["average_rating"]

    def get_review_count(self, obj):
        """Get total approved review count"""
        from apps.ecommerce.services.review_service import ReviewService

        summary = ReviewService.get_product_rating_summary(obj)
        return summary["total_reviews"]


class ProductVariantPublicSerializer(serializers.ModelSerializer):
    """Public product variant serializer"""

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "title",
            "price",
            "compare_at_price",
            "sku",
            "quantity",
            "options",
            "effective_price",
        ]


class CartPublicSerializer(serializers.ModelSerializer):
    """Public cart serializer"""

    items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "session_key", "items", "total", "created_at", "updated_at"]

    def get_items(self, obj):
        return CartItemPublicSerializer(obj.items.all(), many=True).data


class ReviewPublicSerializer(serializers.ModelSerializer):
    """Public review serializer for read-only list and create operations"""

    user_display_name = serializers.CharField(source="user.get_display_name", read_only=True)
    verified_purchase = serializers.BooleanField(read_only=True)
    helpful_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "rating",
            "title",
            "content",
            "user_display_name",
            "verified_purchase",
            "helpful_votes",
            "total_votes",
            "helpful_percentage",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user_display_name",
            "verified_purchase",
            "helpful_votes",
            "total_votes",
            "helpful_percentage",
            "created_at",
        ]

    def get_helpful_percentage(self, obj):
        """Get helpfulness percentage"""
        return obj.helpful_percentage

    def create(self, validated_data):
        """Create a new review using ReviewService"""
        from apps.ecommerce.models.products import Product
        from apps.ecommerce.services.review_service import ReviewService

        request = self.context.get("request")
        product_id = self.context.get("product_id")

        if not product_id:
            raise serializers.ValidationError("Product ID is required")

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")

        # Extract additional data from request
        user_ip = self._get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        referrer = request.META.get("HTTP_REFERER", "")

        review = ReviewService.create_review(
            product=product,
            user=request.user,
            rating=validated_data["rating"],
            title=validated_data["title"],
            content=validated_data["content"],
            user_ip=user_ip,
            user_agent=user_agent,
            referrer=referrer,
        )

        return review

    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class CartItemPublicSerializer(serializers.ModelSerializer):
    """Public cart item serializer"""

    product_name = serializers.CharField(source="product.title", read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_name", "quantity", "unit_price", "total_price"]


class CollectionPublicSerializer(serializers.ModelSerializer):
    """Public collection serializer"""

    class Meta:
        model = ProductCollection
        fields = ["id", "title", "slug", "description", "is_featured", "created_at", "updated_at"]


class CustomerProfilePublicSerializer(serializers.ModelSerializer):
    """Public customer profile serializer"""

    class Meta:
        model = CustomerProfile
        fields = ["id", "user", "first_name", "last_name", "phone", "created_at", "updated_at"]
