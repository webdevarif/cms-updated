"""
Dashboard account views for Digital Farmers CMS.

Endpoints for admin user and role management.
"""
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.accounts.models import User, StoreUser
from apps.accounts.v2.serializers import (
    UserSerializer,
    StoreUserSerializer,
    UserUpdateSerializer
)
from core.permissions import IsStoreAdmin
from .services import DashboardAccountService


class StoreUserViewSet(ModelViewSet):
    """
    API endpoint for managing store users.
    Accessible by store admins only.
    """
    permission_classes = [IsAuthenticated, IsStoreAdmin]
    serializer_class = StoreUserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['user__email', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return DashboardAccountService.get_store_users(self.request.store)

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return super().get_serializer_class()

    @extend_schema(
        summary="List store users",
        description="List all users in the current store",
        responses={200: StoreUserSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create store user",
        description="Create a new user in the current store",
        request=UserUpdateSerializer,
        responses={201: StoreUserSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Update store user",
        description="Update a user in the current store",
        request=UserUpdateSerializer,
        responses={200: StoreUserSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Deactivate user",
        description="Deactivate a user in the current store",
        responses={200: {"detail": "User deactivated successfully"}}
    )
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        store_user = self.get_object()
        try:
            DashboardAccountService.deactivate_store_user(store_user)
            return Response(
                {"detail": "User deactivated successfully"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class RoleViewSet(ModelViewSet):
    """
    API endpoint for managing store roles.
    Accessible by store owners and admins only.
    """
    permission_classes = [IsAuthenticated, IsStoreAdmin]
    serializer_class = StoreUserSerializer

    def get_queryset(self):
        return DashboardAccountService.get_store_users(self.request.store)

    @extend_schema(
        summary="List roles",
        description="List all available roles in the store",
        responses={200: [{"role": "owner"}, {"role": "admin"}, {"role": "manager"}, {"role": "staff"}, {"role": "customer"}]}
    )
    def list(self, request, *args, **kwargs):
        roles = [
            {'role': 'owner', 'display_name': 'Owner'},
            {'role': 'admin', 'display_name': 'Admin'},
            {'role': 'manager', 'display_name': 'Manager'},
            {'role': 'staff', 'display_name': 'Staff'},
            {'role': 'customer', 'display_name': 'Customer'},
        ]
        return Response(roles)

    @extend_schema(
        summary="Get role permissions",
        description="Get permissions for a specific role",
        parameters=[
            OpenApiParameter(name='role', description='Role name', required=True, type=str)
        ],
        responses={200: {"role": str, "permissions": list}}
    )
    @action(detail=False, methods=['get'])
    def permissions(self, request):
        role = request.query_params.get('role')
        
        if not role:
            return Response(
                {"error": "Role parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        permissions = DashboardAccountService.get_role_permissions(role)
        
        return Response({'role': role, 'permissions': permissions})
