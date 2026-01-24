"""
Customer account views for Digital Farmers CMS.

Endpoints for customer profile and password management.
"""
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.accounts.models import User
from apps.accounts.v2.serializers import (
    UserSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer
)
from core.permissions import IsStoreUser
from .services import CustomerAccountService


class CustomerProfileView(generics.RetrieveUpdateAPIView):
    """Customer profile management"""
    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer
    
    @extend_schema(
        summary="Get customer profile",
        description="Retrieve the authenticated customer's profile information",
        responses={200: UserSerializer}
    )
    def get(self, request, *args, **kwargs):
        """Get customer profile"""
        profile_data = CustomerAccountService.get_customer_profile(request.user)
        serializer = self.get_serializer(profile_data['user'])
        return Response(serializer.data)
    
    @extend_schema(
        summary="Update customer profile",
        description="Update the authenticated customer's profile information",
        request=UserUpdateSerializer,
        responses={200: UserSerializer}
    )
    def put(self, request, *args, **kwargs):
        """Update customer profile"""
        serializer = self.get_serializer(
            request.user, 
            data=request.data
        )
        if serializer.is_valid():
            user = CustomerAccountService.update_customer_profile(
                request.user, 
                serializer.validated_data
            )
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Partially update customer profile",
        description="Partially update the authenticated customer's profile information",
        request=UserUpdateSerializer,
        responses={200: UserSerializer}
    )
    def patch(self, request, *args, **kwargs):
        """Partially update customer profile"""
        serializer = self.get_serializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            user = CustomerAccountService.update_customer_profile(
                request.user, 
                serializer.validated_data
            )
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerChangePasswordView(generics.GenericAPIView):
    """Customer password change endpoint"""
    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = ChangePasswordSerializer
    
    @extend_schema(
        summary="Change customer password",
        description="Change the authenticated customer's password",
        request=ChangePasswordSerializer,
        responses={200: {"message": "Password changed successfully"}}
    )
    def post(self, request, *args, **kwargs):
        """Change customer password"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        success, message = CustomerAccountService.change_customer_password(
            request.user,
            serializer.validated_data['current_password'],
            serializer.validated_data['new_password']
        )
        
        if success:
            return Response({"message": message}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"current_password": [message]},
                status=status.HTTP_400_BAD_REQUEST
            )


class CustomerDeleteAccountView(generics.GenericAPIView):
    """Customer account deletion endpoint"""
    permission_classes = [IsAuthenticated, IsStoreUser]
    
    @extend_schema(
        summary="Delete customer account",
        description="Delete the authenticated customer's account",
        request={"password": str},
        responses={200: {"message": "Account deleted successfully"}}
    )
    def post(self, request, *args, **kwargs):
        """Delete customer account"""
        password = request.data.get('password')
        
        if not password:
            return Response({
                'error': 'Password is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify password
        if not request.user.check_password(password):
            return Response({
                'error': 'Invalid password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete user
        request.user.delete()
        
        return Response({
            'message': 'Account deleted successfully'
        })
