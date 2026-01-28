"""
Customer account views for Digital Farmers CMS.

Endpoints for customer profile and password management.
"""
from apps.accounts.models.user import User
from apps.accounts.services.account_service import CustomerAccountService
from core.permissions import IsStoreUser
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import ChangePasswordSerializer, UserSerializer, UserUpdateSerializer


class CustomerUserViewSet(viewsets.GenericViewSet):
    """
    Customer user profile management endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = UserSerializer

    def get_object(self):
        """Get user object for current user"""
        return self.request.user

    @extend_schema(summary="Get user profile", description="Get current user profile")
    def retrieve(self, request, *args, **kwargs):
        """Get current user profile"""
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @extend_schema(summary="Update user profile", description="Update current user profile")
    def partial_update(self, request, *args, **kwargs):
        """Update user profile"""
        user = self.get_object()
        serializer = UserUpdateSerializer(instance=user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(summary="Change password", description="Change user password")
    @action(detail=False, methods=["post"])
    def change_password(self, request):
        """Change user password"""
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Verify old password
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"detail": "Invalid old password"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data["new_password"])
        return Response({"detail": "Password changed successfully"})
