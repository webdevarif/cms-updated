"""
API views for gift cards module with schema documentation and lifecycle actions.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.permissions import IsStoreOwner
from ..models import GiftCard, GiftCardHistory
from .serializers import (
    GiftCardSerializer,
    GiftCardHistorySerializer,
    GiftCardRedeemSerializer,
    GiftCardActivateSerializer,
    GiftCardVoidSerializer,
)
from .schema import (
    gift_card_schema,
    gift_card_list_schema,
    gift_card_detail_schema,
    gift_card_redeem_schema,
    gift_card_balance_schema,
    gift_card_activate_schema,
    gift_card_void_schema,
    gift_card_history_schema,
)
from ..services import GiftCardService
from ...ecommerce.models import Order


@gift_card_schema
@extend_schema_view(
    list=extend_schema(summary="List gift cards"),
    retrieve=extend_schema(summary="Retrieve gift card"),
    create=extend_schema(summary="Create gift card"),
    update=extend_schema(summary="Update gift card"),
    partial_update=extend_schema(summary="Partially update gift card"),
    destroy=extend_schema(summary="Delete gift card"),
)
class GiftCardViewSet(viewsets.ModelViewSet):
    """Gift card management endpoints."""

    permission_classes = [IsAuthenticated, IsStoreOwner]
    queryset = GiftCard.objects.all()
    serializer_class = GiftCardSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'recipient_email', 'recipient_name', 'sender_email', 'sender_name']
    ordering_fields = ['created_at', 'expires_at', 'current_balance']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset().filter(store=self.request.store)

        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        card_type = self.request.query_params.get('gift_card_type') or self.request.query_params.get('type')
        if card_type:
            queryset = queryset.filter(gift_card_type=card_type)

        expires_before = self.request.query_params.get('expires_before')
        if expires_before:
            queryset = queryset.filter(expires_at__lte=expires_before)

        return queryset

    def perform_create(self, serializer):
        serializer.save(store=self.request.store, created_by=self.request.user)

    @extend_schema(
        summary="Redeem a gift card",
        request=GiftCardRedeemSerializer,
        responses={201: GiftCardSerializer}
    )
    @action(detail=False, methods=['post'], url_path='redeem')
    def redeem(self, request):
        """Redeem a gift card."""
        serializer = GiftCardRedeemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = None
            order_id = serializer.validated_data.get('order_id')
            if order_id:
                order = Order.objects.get(id=order_id, store=request.store)

            gift_card = GiftCardService.redeem_gift_card(
                code=serializer.validated_data['code'],
                amount=serializer.validated_data['amount'],
                user=request.user,
                order=order,
                method=serializer.validated_data.get('method', 'online'),
            )

            return Response(GiftCardSerializer(gift_card).data)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:  # noqa: BLE001
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Get gift card balance",
        responses={200: GiftCardSerializer}
    )
    @action(detail=False, methods=['get'], url_path='balance')
    def balance(self, request):
        """Get gift card balance."""
        code = request.query_params.get('code')
        if not code:
            return Response({'error': 'code parameter required'}, status=status.HTTP_400_BAD_REQUEST)

        balance = GiftCardService.get_gift_card_balance(code)
        if balance:
            return Response(balance)

        return Response({'error': 'Gift card not found'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Activate a gift card",
        request=GiftCardActivateSerializer,
        responses={200: GiftCardSerializer}
    )
    @action(detail=True, methods=['post'], url_path='activate')
    def activate(self, request, pk=None):
        """Activate a gift card."""
        gift_card = self.get_object()
        serializer = GiftCardActivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            gift_card = GiftCardService.activate_gift_card(
                gift_card=gift_card,
                activated_by=request.user,
                **serializer.validated_data,
            )
            return Response(GiftCardSerializer(gift_card).data)
        except Exception as exc:  # noqa: BLE001
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Void a gift card",
        request=GiftCardVoidSerializer,
        responses={200: GiftCardSerializer}
    )
    @action(detail=True, methods=['post'], url_path='void')
    def void(self, request, pk=None):
        """Void a gift card."""
        gift_card = self.get_object()
        serializer = GiftCardVoidSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            gift_card = GiftCardService.void_gift_card(
                gift_card=gift_card,
                voided_by=request.user,
                **serializer.validated_data,
            )
            return Response(GiftCardSerializer(gift_card).data)
        except Exception as exc:  # noqa: BLE001
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Get Gift Card History",
        description="Retrieve the history of actions for a specific gift card.",
        responses={200: GiftCardHistorySerializer(many=True)},
    )
    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        """Get history for a gift card."""
        gift_card = self.get_object()
        history_qs = gift_card.history.all().order_by('-created_at')
        page = self.paginate_queryset(history_qs)

        serializer = GiftCardHistorySerializer(page or history_qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


@extend_schema(tags=['Gift Cards'])
class GiftCardHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Gift card history endpoints."""

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = GiftCardHistorySerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = GiftCardHistory.objects.filter(gift_card__store=self.request.store)

        gift_card_id = self.request.query_params.get('gift_card_id')
        if gift_card_id:
            queryset = queryset.filter(gift_card_id=gift_card_id)

        action_param = self.request.query_params.get('action')
        if action_param:
            queryset = queryset.filter(action=action_param)

        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        return queryset.order_by('-created_at')
