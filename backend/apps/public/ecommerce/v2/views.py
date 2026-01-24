"""
Public API views for ecommerce.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from rest_framework import viewsets
from ..models import Product, Cart, CartItem, Order
from .serializers import ProductSerializer, CartSerializer, OrderSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    Public API for products
    """
    permission_classes = [AllowAny]
    queryset = Product.objects.filter(status='active', is_available=True)
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(store=self.request.store)
    
    @extend_schema(
        summary="Get Product by Slug",
        responses={200: ProductSerializer}
    )
    @action(detail=False, methods=['get'])
    def by_slug(self, request):
        """Get product by slug"""
        slug = request.query_params.get('slug')
        if not slug:
            return Response(
                {'error': 'slug parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product = self.get_queryset().filter(slug=slug).first()
        if not product:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(product)
        return Response(serializer.data)


class CartViewSet(viewsets.ModelViewSet):
    """
    Public API for cart operations
    """
    permission_classes = [AllowAny]
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(store=self.request.store)
    
    @extend_schema(
        summary="Get Cart",
        responses={200: CartSerializer}
    )
    @action(detail=False, methods=['get'])
    def get_cart(self, request):
        """Get or create cart"""
        from ..v2.services import CartService
        
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.get('cart_session_key') if not user else None
        
        cart = CartService.get_or_create_cart(
            store=request.store,
            user=user,
            session_key=session_key
        )
        
        serializer = self.get_serializer(cart)
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    """
    Public API for orders
    """
    permission_classes = [AllowAny]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(store=self.request.store)
