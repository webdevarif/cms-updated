"""
Public accounts API.
"""

from apps.accounts.models import User
from apps.accounts.services.account_service import PublicAuthService
from core.permissions import AllowAnyPublicRead
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    RegistrationSerializer,
    UserSerializer,
)


class PublicLoginView(generics.GenericAPIView):
    """
    Public login endpoint.
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        summary="User login",
        description="Authenticate user with email or username and return JWT token",
    )
    def post(self, request):
        """Authenticate user and return JWT token"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get user from serializer validation
        user = serializer.validated_data["user"]

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

        user = serializer.save()

        # Generate JWT tokens
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
                "message": "Registration successful",
            },
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
    serializer_class = PasswordResetConfirmSerializer

    @extend_schema(summary="Reset password", description="Reset password with token")
    def post(self, request):
        """Reset password with token"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = PublicAuthService.reset_password(
            token=serializer.validated_data["token"],
            new_password=serializer.validated_data["new_password"],
        )

        if result["success"]:
            return Response({"message": result["message"]})
        else:
            return Response({"detail": result["error"]}, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(generics.GenericAPIView):
    """
    JWT token refresh endpoint.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Refresh JWT token", description="Refresh access token using refresh token"
    )
    def post(self, request):
        """Refresh JWT token"""
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            return Response(
                {
                    "access": access_token,
                    "refresh": str(refresh),  # New refresh token if rotation is enabled
                }
            )
        except InvalidToken:
            return Response(
                {"detail": "Invalid or expired refresh token"}, status=status.HTTP_401_UNAUTHORIZED
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile endpoint for authenticated users.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        """Get current user"""
        return self.request.user

    @extend_schema(summary="Get user profile", description="Get current user profile")
    def get(self, request, *args, **kwargs):
        """Get current user profile"""
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @extend_schema(summary="Update user profile", description="Update current user profile")
    def patch(self, request, *args, **kwargs):
        """Update user profile"""
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
