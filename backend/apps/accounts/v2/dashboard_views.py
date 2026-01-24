"""
Dashboard views for Digital Farmers CMS accounts API.

Store user management endpoints for dashboard.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from core.permissions import IsStoreStaff
from apps.accounts.models import StoreUser
from apps.accounts.v2.serializers import (
    StoreUserSerializer,
    StoreUserCreateSerializer,
    UserUpdateSerializer,
)


class StoreUserViewSet(viewsets.ModelViewSet):
    """
    Store User Management API - Dashboard
    Store-scoped user management for dashboard
    """
    
    permission_classes = [IsAuthenticated, IsStoreStaff]
    filterset_fields = ['role', 'is_active']
    search_fields = ['user__email', 'user__username', 'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'user__email']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter by current store"""
        if hasattr(self.request, 'store') and self.request.store:
            return StoreUser.objects.filter(store=self.request.store)
        return StoreUser.objects.none()
    
    def get_serializer_class(self):
        """Return appropriate serializer"""
        if self.action == 'create':
            return StoreUserCreateSerializer
        return StoreUserSerializer
    
    def get_serializer_context(self):
        """Add store to context"""
        context = super().get_serializer_context()
        if hasattr(self.request, 'store'):
            context['store'] = self.request.store
        return context
    
    @extend_schema(
        summary="List Store Users",
        description="Get paginated list of store users",
        responses={200: StoreUserSerializer}
    )
    def list(self, request, *args, **kwargs):
        """List users with filtering and search"""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Store User",
        description="Create new user in store",
        request=StoreUserCreateSerializer,
        responses={201: StoreUserSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Create user with automatic store assignment"""
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Store User",
        description="Update store user details",
        request=UserUpdateSerializer,
        responses={200: StoreUserSerializer}
    )
    def update(self, request, *args, **kwargs):
        """Update user with validation"""
        return super().update(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Deactivate User",
        description="Deactivate user account",
        responses={200: dict}
    )
    def deactivate(self, request, pk=None):
        """Deactivate user"""
        store_user = self.get_object()
        
        if store_user.role == 'owner':
            return Response({
                'error': 'Cannot deactivate store owner',
                'code': 'CANNOT_DEACTIVATE_OWNER'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from core.services.user import UserService
        UserService.deactivate_user(store_user.user, store_user.store)
        
        return Response({
            'message': f'User {store_user.user.email} deactivated successfully'
        })
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Change User Role",
        description="Update user role and permissions",
        request=dict,
        responses={200: dict}
    )
    def change_role(self, request, pk=None):
        """Change user role"""
        store_user = self.get_object()
        
        if store_user.role == 'owner':
            return Response({
                'error': 'Cannot change store owner role',
                'code': 'CANNOT_CHANGE_OWNER_ROLE'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        new_role = request.data.get('role')
        if not new_role:
            return Response({
                'error': 'Role is required',
                'code': 'ROLE_REQUIRED'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from core.services.user import UserService
        try:
            UserService.update_user_role(store_user.user, store_user.store, new_role)
            
            return Response({
                'message': f'User {store_user.user.email} role updated successfully',
                'new_role': new_role
            })
        except Exception as e:
            return Response({
                'error': str(e),
                'code': 'ROLE_UPDATE_FAILED'
            }, status=status.HTTP_400_BAD_REQUEST)
