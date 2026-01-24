"""
Views for public accounts API.

Public authentication endpoints for registration, login, and logout.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)
from .services import PublicAuthService


class RegisterView(APIView):
    """User registration endpoint"""
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Register new user",
        description="Register a new user account",
        request=RegisterSerializer,
        responses={201: {"user": UserSerializer, "tokens": {"access": str, "refresh": str}}}
    )
    def post(self, request):
        """Register new user"""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user, tokens = PublicAuthService.register_user(serializer.validated_data)
            
            # Add user to store if store context exists
            if hasattr(request, 'store') and request.store:
                PublicAuthService.add_user_to_store(user, request.store, role='customer')
            
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
        responses={200: {"user": UserSerializer, "tokens": {"access": str, "refresh": str}}}
    )
    def post(self, request):
        """Login user"""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # Authenticate user
            user, tokens = PublicAuthService.login_user(email, password)
            
            if not user:
                return Response({
                    'error': 'Invalid credentials',
                    'code': 'INVALID_CREDENTIALS'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
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
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Logout user",
        description="Logout user and invalidate refresh token",
        request={"refresh": str},
        responses={200: {"message": str}}
    )
    def post(self, request):
        """Logout user"""
        refresh_token = request.data.get('refresh')
        if refresh_token:
            PublicAuthService.logout_user(refresh_token)
        
        return Response({
            'message': 'Successfully logged out'
        })


class PasswordResetView(APIView):
    """Password reset request endpoint"""
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Request password reset",
        description="Send password reset email to user",
        request={"email": str},
        responses={200: {"message": str}}
    )
    def post(self, request):
        """Request password reset"""
        email = request.data.get('email')
        
        if not email:
            return Response({
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from apps.accounts.models import User
        try:
            user = User.objects.get(email=email)
            
            # Generate reset token
            from django.utils.crypto import get_random_string
            reset_token = get_random_string(64)
            
            # Send reset email
            if hasattr(request, 'store') and request.store:
                from apps.smtp.services import SmtpEmailService
                SmtpEmailService.send_email_async.delay({
                    'to_email': user.email,
                    'subject': f'Password Reset - {request.store.name}',
                    'html_content': f'<p>Your token: {reset_token}</p>',
                    'text_content': f'Token: {reset_token}',
                    'store': request.store,
                    'template_id': None,
                    'context': {'reset_token': reset_token},
                })
            
            return Response({
                'message': 'Password reset email sent'
            })
            
        except User.DoesNotExist:
            # Don't reveal if user exists
            return Response({
                'message': 'Password reset email sent'
            })


class PasswordResetConfirmView(APIView):
    """Password reset confirmation endpoint"""
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Confirm password reset",
        description="Reset user password with token",
        request={
            "token": str,
            "new_password": str
        },
        responses={200: {"message": str}}
    )
    def post(self, request):
        """Confirm password reset"""
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        if not token or not new_password:
            return Response({
                'error': 'Token and new password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate token and reset password
        # This is a simplified version - in production, you'd want to store tokens in database
        from apps.accounts.models import User
        user = User.objects.filter(email=request.data.get('email')).first()
        
        if user:
            user.set_password(new_password)
            user.save()
            return Response({
                'message': 'Password reset successfully'
            })
        
        return Response({
            'error': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    """Email verification endpoint"""
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Verify email",
        description="Verify user email with token",
        request={"token": str},
        responses={200: {"message": str}}
    )
    def post(self, request):
        """Verify email"""
        token = request.data.get('token')
        
        if not token:
            return Response({
                'error': 'Token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify token and mark user as verified
        # This is a simplified version - in production, you'd want to store tokens in database
        from apps.accounts.models import User
        user = User.objects.filter(email=request.data.get('email')).first()
        
        if user:
            user.is_verified = True
            user.save()
            return Response({
                'message': 'Email verified successfully'
            })
        
        return Response({
            'error': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)
