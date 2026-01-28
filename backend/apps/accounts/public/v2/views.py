"""
Public accounts API.
"""
from apps.accounts.models.user import User
from apps.accounts.services.account_service import PublicAuthService
from core.permissions import AllowAnyPublicRead
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import (
    LoginSerializer,
    PasswordResetSerializer,
    RegistrationSerializer,
    UserSerializer,
)


class PublicLoginView(generics.GenericAPIView):
    """
    Public login endpoint.
    """

    permission_classes = [AllowAnyPublicRead]
    serializer_class = LoginSerializer

    @extend_schema(summary="User login", description="Authenticate user and return JWT token")
    def post(self, request):
        """Authenticate user and return JWT token"""
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data["email"])

        if not user.check_password(serializer.validated_data["password"]):
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT token
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            }
        )


class PublicRegistrationView(generics.GenericAPIView):
    """
    Public registration endpoint.
    """

    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    @extend_schema(summary="User registration", description="Register new user account")
    def post(self, request):
        """Register new user"""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = PublicAuthService.create_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            first_name=serializer.validated_data.get("first_name", ""),
            last_name=serializer.validated_data.get("last_name", ""),
        )

        return Response(
            {"user": UserSerializer(user).data, "message": "Registration successful"},
            status=status.HTTP_201_CREATED,
        )


class ForgotPasswordView(generics.GenericAPIView):
    """
    Public forgot password endpoint.
    """

    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    @extend_schema(summary="Forgot password", description="Send password reset email")
    def post(self, request):
        """Send password reset email"""
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        PublicAuthService.send_password_reset_email(serializer.validated_data["email"])

        return Response({"message": "Password reset email sent"})


class ResetPasswordView(generics.GenericAPIView):
    """
    Public reset password endpoint.
    """

    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    @extend_schema(summary="Reset password", description="Reset password with token")
    def post(self, request):
        """Reset password with token"""
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        PublicAuthService.reset_password(
            token=serializer.validated_data["token"],
            new_password=serializer.validated_data["new_password"],
        )

        return Response({"message": "Password reset successful"})
