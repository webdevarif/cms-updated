"""
Public gift cards views - read-only interface for gift card balance checks.
Architectural + real implementation for public gift cards interface.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.giftcards.models import GiftCard
from apps.giftcards.services.giftcard_service import GiftCardService
from .serializers import PublicGiftCardSerializer, PublicGiftCardBalanceSerializer


class PublicGiftCardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public gift cards API - read-only access to gift card information.
    Architectural + real implementation for public gift cards interface.
    
    Provides:
    - Retrieve gift card by code
    - Check gift card balance
    - Limited gift card information
    """
    
    permission_classes = []  # AllowAny
    queryset = GiftCard.objects.filter(status='active').select_related('store')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['code']
    ordering_fields = ['created_at', 'expires_at', 'current_balance']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        return PublicGiftCardSerializer
    
    def get_queryset(self):
        """Filter to active gift cards only."""
        queryset = super().get_queryset()
        store = getattr(self.request, 'store', None)
        if store:
            queryset = queryset.filter(store=store)
        return queryset
    
    @action(detail=False, methods=['get'])
    def balance(self, request):
        """
        Check gift card balance by code.
        
        Args:
            code: Gift card code to check
            
        Returns:
            Balance information for the gift card
        """
        code = request.query_params.get('code')
        if not code:
            return Response(
                {'error': 'code parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        balance_info = GiftCardService.get_gift_card_balance(code)
        if balance_info:
            return Response(balance_info)
        
        return Response(
            {'error': 'Gift card not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=False, methods=['get'], url_path='check/(?P<code>[^/.]+)')
    def check_by_code(self, request, code=None):
        """
        Check gift card by code in URL.
        
        Args:
            code: Gift card code from URL
            
        Returns:
            Gift card information if found and active
        """
        if not code:
            return Response(
                {'error': 'code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            store = getattr(self.request, 'store', None)
            gift_card = GiftCard.objects.get(
                code=code.upper(),
                status='active',
                store=store if store else None
            )
            
            serializer = self.get_serializer(gift_card)
            return Response(serializer.data)
            
        except GiftCard.DoesNotExist:
            return Response(
                {'error': 'Gift card not found or inactive'},
                status=status.HTTP_404_NOT_FOUND
            )
