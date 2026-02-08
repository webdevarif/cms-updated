from apps.accounts.permissions import IsStoreAdminOrOwner, IsStoreMember, IsStoreOwner
from apps.accounts.permissions_api_keys import (
    HasStoreAPIKey,
    HasStoreAPIKeyOrIsAuthenticated,
    can_manage_products_via_api,
    can_manage_settings_via_api,
    can_manage_staff_via_api,
    can_view_orders_via_api,
)
from apps.accounts.serializers import (
    StoreAPIKeyCreateNestedSerializer,
    StoreAPIKeyCreateSerializer,
    StoreAPIKeyNestedSerializer,
    StoreAPIKeySerializer,
    StoreDetailSerializer,
    StoreMembershipSerializer,
    StoreRoleNestedSerializer,
    StoreRoleSerializer,
    StoreSerializer,
    StoreUserRoleSerializer,
)
from apps.accounts.services.roles import APIKeyService, RoleService
from apps.stores.services import StoreService
from apps.stores.utils import StoreScopedMixin
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.contrib.auth import get_user_model

from .models import Store, StoreAPIKey, StoreMembership, StoreRole, StoreUserRole

User = get_user_model()


class StoreMembershipViewSet(viewsets.ModelViewSet):
    """Store membership management"""

    serializer_class = StoreMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StoreMembership.objects.all()


class StoreViewSet(viewsets.ModelViewSet):
    """Store CRUD operations"""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StoreService.get_user_stores(self.request.user)

    def get_serializer_class(self):
        if self.action in ["retrieve", "members"]:
            return StoreDetailSerializer
        return StoreSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            self.permission_classes = [permissions.IsAuthenticated, IsStoreOwner]
        elif self.action == "members":
            self.permission_classes = [permissions.IsAuthenticated, IsStoreAdminOrOwner]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Create store with current user as owner"""
        store = StoreService.create_store(
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
            owner=self.request.user,
        )
        serializer.instance = store

    @action(detail=True, methods=["get", "post"])
    def members(self, request, pk=None):
        """Manage store members"""
        store = self.get_object()

        if request.method == "GET":
            memberships = store.memberships.all()
            serializer = StoreMembershipSerializer(memberships, many=True)
            return Response(serializer.data)

        # POST - Add member
        user_id = request.data.get("user_id")
        role = request.data.get("role")

        try:
            membership = StoreService.add_member(store, user_id, role)
            serializer = StoreMembershipSerializer(membership)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StoreRoleViewSet(StoreScopedMixin, viewsets.ModelViewSet):
    """Store role management"""

    serializer_class = StoreRoleNestedSerializer
    permission_classes = [permissions.IsAuthenticated, IsStoreAdminOrOwner]

    def get_queryset(self):
        """Filter roles by store"""
        return StoreRole.objects.filter(store=self.store)

    def get_serializer_class(self):
        """Use different serializer for nested vs standalone"""
        if "store_pk" in self.kwargs:
            return StoreRoleNestedSerializer
        return StoreRoleSerializer

    def perform_create(self, serializer):
        """Set store and created_by"""
        serializer.save(store=self.store)

    @action(detail=True, methods=["get"])
    def users(self, request, store_pk=None, pk=None):
        """Get users assigned to this role"""
        role = self.get_object()
        user_roles = role.user_assignments.select_related("user")
        serializer = StoreUserRoleSerializer(user_roles, many=True)
        return Response(serializer.data)


class StoreUserRoleViewSet(StoreScopedMixin, viewsets.ModelViewSet):
    """Store user role assignment management"""

    serializer_class = StoreUserRoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsStoreAdminOrOwner]

    def get_queryset(self):
        """Filter user roles by store"""
        return StoreUserRole.objects.filter(store=self.store).select_related("user", "role")

    def perform_create(self, serializer):
        """Set store and assigned_by"""
        serializer.save(store=self.store, assigned_by=self.request.user)


class StoreAPIKeyViewSet(StoreScopedMixin, viewsets.ModelViewSet):
    """Store API key management"""

    permission_classes = [permissions.IsAuthenticated, IsStoreAdminOrOwner]

    def get_serializer_class(self):
        """Use different serializer for creation to return the key"""
        if self.action == "create":
            return StoreAPIKeyCreateNestedSerializer
        return StoreAPIKeyNestedSerializer

    def get_queryset(self):
        """Filter API keys by store"""
        return StoreAPIKey.objects.filter(store=self.store)

    def perform_create(self, serializer):
        """Set store and created_by"""
        serializer.save(store=self.store, created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def revoke(self, request, store_pk=None, pk=None):
        """Revoke an API key"""
        api_key = self.get_object()
        APIKeyService.revoke_api_key(api_key)
        return Response({"message": "API key revoked"})

    @action(detail=False, methods=["get"])
    def available_actions(self, request, store_pk=None):
        """Get list of available actions for API keys"""
        return Response({"actions": RoleService.AVAILABLE_ACTIONS})
