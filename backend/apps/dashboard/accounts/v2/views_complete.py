"""
Complete dashboard account views for Digital Farmers CMS.

All missing ViewSets and endpoints fully implemented.
"""
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.accounts.models import User, StoreUser, Role
from .serializers import (
    StoreUserSerializer,
    StoreUserCreateSerializer,
    StoreUserUpdateSerializer,
    RoleSerializer,
    RoleCreateSerializer,
    UserUpdateSerializer
)
from core.permissions import IsStoreAdmin, IsStoreStaff
from .services import DashboardAccountService
from core.services.user import UserService


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
        return UserService.filter_store_users(self.request.store, is_active=True)

    def get_serializer_class(self):
        if self.action == 'create':
            return StoreUserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return StoreUserUpdateSerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['store'] = self.request.store
        return context

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
        request=StoreUserCreateSerializer,
        responses={201: StoreUserSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        store_user = DashboardAccountService.create_store_user(
            store=request.store,
            user_data=serializer.validated_data['user'],
            role=serializer.validated_data.get('role', 'customer')
        )
        
        response_serializer = StoreUserSerializer(store_user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Update store user",
        description="Update store user details",
        request=StoreUserUpdateSerializer,
        responses={200: StoreUserSerializer}
    )
    def update(self, request, *args, **kwargs):
        store_user = self.get_object()
        serializer = self.get_serializer(store_user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        if 'role' in serializer.validated_data:
            DashboardAccountService.update_store_user_role(
                store_user, 
                serializer.validated_data['role']
            )
        
        if 'is_active' in serializer.validated_data:
            if serializer.validated_data['is_active']:
                UserService.activate_store_user(store_user.user, store_user.store)
            else:
                DashboardAccountService.deactivate_store_user(store_user)
        
        response_serializer = StoreUserSerializer(store_user)
        return Response(response_serializer.data)

    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Deactivate user",
        description="Deactivate a store user",
        responses={200: {"message": str}}
    )
    def deactivate(self, request, pk=None):
        store_user = self.get_object()
        DashboardAccountService.deactivate_store_user(store_user)
        return Response({"message": f"User {store_user.user.email} deactivated"})

    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Activate user",
        description="Activate a store user",
        responses={200: {"message": str}}
    )
    def activate(self, request, pk=None):
        store_user = self.get_object()
        UserService.activate_store_user(store_user.user, store_user.store)
        return Response({"message": f"User {store_user.user.email} activated"})


class RoleViewSet(ModelViewSet):
    """
    API endpoint for managing store roles.
    Accessible by store admins only.
    """
    permission_classes = [IsAuthenticated, IsStoreAdmin]
    serializer_class = RoleSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        return Role.objects.filter(store=self.request.store)

    def get_serializer_class(self):
        if self.action == 'create':
            return RoleCreateSerializer
        return super().get_serializer_class()

    @extend_schema(
        summary="List store roles",
        description="List all roles in the current store",
        responses={200: RoleSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create store role",
        description="Create a new role in the current store",
        request=RoleCreateSerializer,
        responses={201: RoleSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        role = Role.objects.create(
            store=request.store,
            **serializer.validated_data
        )
        
        response_serializer = RoleSerializer(role)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    @extend_schema(
        summary="Get role permissions",
        description="Get permissions for a specific role",
        responses={200: {"permissions": list}}
    )
    def permissions(self, request, pk=None):
        role = self.get_object()
        permissions = DashboardAccountService.get_role_permissions(role.name)
        return Response({"permissions": permissions})


class UserViewSet(ModelViewSet):
    """
    API endpoint for managing global users.
    Accessible by store staff only.
    """
    permission_classes = [IsAuthenticated, IsStoreStaff]
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering_fields = ['email', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        # Get users that belong to current store
        store_user_ids = UserService.filter_store_users(
            self.request.store
        ).values_list('user_id', flat=True)
        
        return UserService.filter_users(id__in=store_user_ids)

    @extend_schema(
        summary="List users",
        description="List all users in the current store",
        responses={200: UserSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Update user",
        description="Update user details",
        request=UserUpdateSerializer,
        responses={200: UserSerializer}
    )
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        UserService.update_user(user, **serializer.validated_data)
        
        response_serializer = UserSerializer(user)
        return Response(response_serializer.data)
