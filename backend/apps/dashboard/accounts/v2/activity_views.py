"""
User activity views for Digital Farmers CMS.

Endpoints for tracking and viewing user activity.
"""
from rest_framework import status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema

from apps.accounts.models import StoreUser
from core.permissions import IsStoreAdmin


class UserActivityViewSet(ModelViewSet):
    """
    API endpoint for managing user activity logs.
    Accessible by store admins only.
    """
    permission_classes = [IsAuthenticated, IsStoreAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['action', 'ip_address']
    ordering_fields = ['created_at', 'action']
    ordering = ['-created_at']

    def get_queryset(self):
        """Get activity logs for the current store"""
        from apps.accounts.models import UserActivity
        
        return UserActivity.objects.filter(
            store_user__store=self.request.store
        ).select_related('store_user__user')

    def list(self, request, *args, **kwargs):
        """List user activities"""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create activity log",
        description="Log a user activity",
        responses={201: dict}
    )
    def create(self, request, *args, **kwargs):
        """Create activity log"""
        from apps.accounts.models import UserActivity
        
        store_user_id = request.data.get('store_user_id')
        action = request.data.get('action')
        details = request.data.get('details', {})
        ip_address = request.META.get('REMOTE_ADDR')
        
        if not store_user_id or not action:
            return Response({
                'error': 'store_user_id and action are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            store_user = StoreUser.objects.get(
                id=store_user_id,
                store=self.request.store
            )
            
            activity = UserActivity.objects.create(
                store_user=store_user,
                action=action,
                details=details,
                ip_address=ip_address
            )
            
            return Response({
                'id': activity.id,
                'action': activity.action,
                'created_at': activity.created_at
            }, status=status.HTTP_201_CREATED)
            
        except StoreUser.DoesNotExist:
            return Response({
                'error': 'Store user not found'
            }, status=status.HTTP_404_NOT_FOUND)
