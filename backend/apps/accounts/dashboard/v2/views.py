"""
Dashboard account views for Digital Farmers CMS.

Endpoints for admin user and role management.
"""

from apps.accounts.models.store_user import StoreUser
from apps.accounts.models.user import User
from apps.accounts.services.account_service import DashboardAccountService
from core.permissions import IsStoreOwner
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .serializers import StoreUserSerializer, UserSerializer, UserUpdateSerializer


class DashboardUserViewSet(ModelViewSet):
    """
    Dashboard user management endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["created_at", "username", "email"]

    def get_queryset(self):
        """Filter by current user's stores"""
        return User.objects.filter(
            id__in=StoreUser.objects.filter(
                store=self.request.store, role__in=["owner", "admin"]
            ).values_list("user_id", flat=True)
        )

    @extend_schema(summary="List users", description="List all users in user's stores")
    def list(self, request, *args, **kwargs):
        """List users"""
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Create user", description="Create new user in store")
    def create(self, request, *args, **kwargs):
        """Create user"""
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Retrieve user", description="Get user details")
    def retrieve(self, request, *args, **kwargs):
        """Get user"""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Update user", description="Update user details")
    def update(self, request, *args, **kwargs):
        """Update user"""
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Partial update user", description="Partially update user details")
    def partial_update(self, request, *args, **kwargs):
        """Partial update user"""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary="Delete user", description="Delete user")
    def destroy(self, request, *args, **kwargs):
        """Delete user"""
        return super().destroy(request, *args, **kwargs)

    @extend_schema(summary="Activate user", description="Activate user account")
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate user"""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({"detail": "User activated successfully"})

    @extend_schema(summary="Deactivate user", description="Deactivate user account")
    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate user"""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({"detail": "User deactivated successfully"})


class DashboardStoreUserViewSet(ModelViewSet):
    """
    Dashboard store user management endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = StoreUserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["user__username", "user__email", "role"]
    ordering_fields = ["created_at", "user__username", "role"]

    def get_queryset(self):
        """Filter by current user's stores"""
        return StoreUser.objects.filter(store=self.request.store)

    @extend_schema(summary="List store users", description="List all store users")
    def list(self, request, *args, **kwargs):
        """List store users"""
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Create store user", description="Create new store user")
    def create(self, request, *args, **kwargs):
        """Create store user"""
        return super().create(request, *args, **kwargs)
