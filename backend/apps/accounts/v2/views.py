"""
Views for Digital Farmers CMS accounts API.

Public authentication endpoints for registration, login, and logout.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.contrib.auth import authenticate
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    UserSerializer,
)
from .services import AuthService


class RegisterView(APIView):
    """User registration endpoint"""
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Register new user",
        description="Register a new user account",
        request=RegisterSerializer,
        responses={201: UserSerializer}
    )
    def post(self, request):
        """Register new user"""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT tokens
            tokens = AuthService.generate_token(user)
            
            # Add user to store if store context exists
            if hasattr(request, 'store') and request.store:
                from core.services.user import UserService
                UserService.add_user_to_store(user, request.store, role='customer')
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'error': 'Validation failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """User login endpoint"""
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Login user",
        description="Authenticate user and return JWT tokens",
        request=LoginSerializer,
        responses={200: dict}
    )
    def post(self, request):
        """Login user"""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # Authenticate user
            user = authenticate(username=email, password=password)
            
            if not user:
                return Response({
                    'error': 'Invalid credentials',
                    'code': 'INVALID_CREDENTIALS'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            if not user.is_active:
                return Response({
                    'error': 'Account is inactive',
                    'code': 'ACCOUNT_INACTIVE'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Generate JWT tokens
            tokens = AuthService.generate_token(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': tokens
            })
        
        return Response({
            'error': 'Validation failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """User logout endpoint"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Logout user",
        description="Logout user and invalidate refresh token",
        responses={200: dict}
    )
    def post(self, request):
        """Logout user"""
        try:
            # Get refresh token from request
            refresh_token = request.data.get('refresh')
            if refresh_token:
                from rest_framework_simplejwt.tokens import RefreshToken
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'message': 'Successfully logged out'
            })
        except Exception:
            return Response({
                'message': 'Logout successful'
            })


class ChangePasswordView(APIView):
    """Change password endpoint"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Change password",
        description="Change user password",
        request=ChangePasswordSerializer,
        responses={200: dict, 400: dict}
    )
    def post(self, request):
        """Change user password"""
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Verify current password
            if not user.check_password(serializer.validated_data['current_password']):
                return Response({
                    'error': 'Current password is incorrect',
                    'code': 'INVALID_CURRENT_PASSWORD'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save(update_fields=['password'])
            
            return Response({
                'message': 'Password changed successfully'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """User profile endpoint"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        """Return current user"""
        return self.request.user
    
    @extend_schema(
        summary="Get user profile",
        description="Get current user profile information",
        responses={200: UserSerializer}
    )
    def get(self, request, *args, **kwargs):
        """Get user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Update user profile",
        description="Update current user profile",
        request=UserUpdateSerializer,
        responses={200: UserSerializer}
    )
    def patch(self, request, *args, **kwargs):
        """Update user profile"""
        serializer = self.get_serializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
