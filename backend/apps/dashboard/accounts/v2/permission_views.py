"""
Dashboard permission views for Digital Farmers CMS.

Endpoints for managing user permissions.
"""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.accounts.models import StoreUser
from core.permissions import IsStoreAdmin
from .services import DashboardAccountService


class PermissionViewSet(ModelViewSet):
    """
    API endpoint for managing user permissions.
    Accessible by store owners and admins only.
    """
    permission_classes = [IsAuthenticated, IsStoreAdmin]
    
    def get_queryset(self):
        return DashboardAccountService.get_store_users(self.request.store)

    @extend_schema(
        summary="Get user permissions",
        description="Get permissions for a specific user in the store",
        parameters=[
            OpenApiParameter(name='user_id', description='User ID', required=True, type=int)
        ],
        responses={200: {"user_id": int, "role": str, "permissions": list}}
    )
    @action(detail=False, methods=['get'])
    def user_permissions(self, request):
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {"error": "user_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            store_user = StoreUser.objects.get(
                user_id=user_id,
                store=request.store,
                is_active=True
            )
            
            permissions = DashboardAccountService.get_role_permissions(
                store_user.role
            )
            
            return Response({
                'user_id': user_id,
                'role': store_user.role,
                'permissions': permissions
            })
            
        except StoreUser.DoesNotExist:
            return Response(
                {"error": "User not found in this store"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Check user permission",
        description="Check if a user has a specific permission",
        parameters=[
            OpenApiParameter(name='user_id', description='User ID', required=True, type=int),
            OpenApiParameter(name='permission', description='Permission to check', required=True, type=str)
        ],
        responses={200: {"user_id": int, "permission": str, "has_permission": bool}}
    )
    @action(detail=False, methods=['get'])
    def check_permission(self, request):
        user_id = request.query_params.get('user_id')
        permission = request.query_params.get('permission')
        
        if not user_id or not permission:
            return Response(
                {"error": "user_id and permission parameters are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            has_permission = DashboardAccountService.check_user_permission(
                user_id=request.user.id,
                store=request.store,
                permission=permission
            )
            
            return Response({
                'user_id': user_id,
                'permission': permission,
                'has_permission': has_permission
            })
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
