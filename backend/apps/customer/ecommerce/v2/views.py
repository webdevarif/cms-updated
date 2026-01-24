"""
Customer API views for ecommerce.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from rest_framework import viewsets
from core.permissions import IsStoreUser
from apps.public.ecommerce.models import Cart, CartItem, Order, Product, ProductVariant
from apps.public.ecommerce.v2.serializers import CartSerializer, OrderSerializer, CartItemSerializer


class CustomerCartViewSet(viewsets.ModelViewSet):
    """
    Customer cart management endpoints
    """
    permission_classes = [IsAuthenticated, IsStoreUser]
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(store=self.request.store, user=self.request.user)
    
    @extend_schema(
        summary="Get Customer Cart",
        responses={200: CartSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        """Get or create cart for customer"""
        from ..v2.services import CartService
        
        cart = CartService.get_or_create_cart(
            store=request.store,
            user=request.user
        )
        
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Add Item to Cart",
        request=None,
        responses={201: CartItemSerializer}
    )
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart"""
        from apps.public.ecommerce.models import Product, ProductVariant
        from apps.public.ecommerce.v2.services import CartService
        
        product_id = request.data.get('product_id')
        variant_id = request.data.get('variant_id')
        quantity = request.data.get('quantity', 1)
        
        product = Product.objects.get(id=product_id)
        variant = ProductVariant.objects.filter(id=variant_id).first()
        
        cart = CartService.get_or_create_cart(
            store=request.store,
            user=request.user
        )
        
        item = CartService.add_item(cart, product, variant, quantity)
        
        serializer = CartItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Remove Item from Cart",
        responses={204: None}
    )
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove item from cart"""
        from apps.public.ecommerce.models import Product, ProductVariant
        from apps.public.ecommerce.v2.services import CartService
        
        product_id = request.data.get('product_id')
        variant_id = request.data.get('variant_id')
        
        product = Product.objects.get(id=product_id)
        variant = ProductVariant.objects.filter(id=variant_id).first()
        
        cart = CartService.get_or_create_cart(
            store=request.store,
            user=request.user
        )
        
        CartService.remove_item(cart, product, variant)
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerOrderViewSet(viewsets.ModelViewSet):
    """
    Customer order management endpoints
    """
    permission_classes = [IsAuthenticated, IsStoreUser]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(store=self.request.store, user=self.request.user)
