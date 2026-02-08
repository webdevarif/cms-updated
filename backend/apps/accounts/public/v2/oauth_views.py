"""
OAuth views for social authentication.
"""

from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .serializers import UserSerializer

User = get_user_model()


@method_decorator(csrf_exempt, name="dispatch")
class GoogleOAuthView(generics.GenericAPIView):
    """
    Google OAuth login endpoint.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="google_oauth_login",
        summary="Google OAuth login",
        description="Redirect to Google OAuth for authentication",
        responses={302: {"description": "Redirect to Google OAuth"}},
    )
    def get(self, request):
        """Redirect to Google OAuth"""
        if not settings.GOOGLE_CLIENT_ID:
            return Response(
                {"error": "Google OAuth not configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # In a real implementation, you would use django-allauth or social-auth-app-django
        # For now, return a placeholder response
        return Response(
            {
                "message": "Google OAuth endpoint - needs implementation",
                "client_id": settings.GOOGLE_CLIENT_ID,
                "redirect_url": f"{settings.FRONTEND_URL}/auth/callback/google",
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class FacebookOAuthView(generics.GenericAPIView):
    """
    Facebook OAuth login endpoint.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="facebook_oauth_login",
        summary="Facebook OAuth login",
        description="Redirect to Facebook OAuth for authentication",
        responses={302: {"description": "Redirect to Facebook OAuth"}},
    )
    def get(self, request):
        """Redirect to Facebook OAuth"""
        if not settings.FACEBOOK_APP_ID:
            return Response(
                {"error": "Facebook OAuth not configured"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # In a real implementation, you would use django-allauth or social-auth-app-django
        # For now, return a placeholder response
        return Response(
            {
                "message": "Facebook OAuth endpoint - needs implementation",
                "app_id": settings.FACEBOOK_APP_ID,
                "redirect_url": f"{settings.FRONTEND_URL}/auth/callback/facebook",
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class GithubOAuthView(generics.GenericAPIView):
    """
    GitHub OAuth login endpoint.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="github_oauth_login",
        summary="GitHub OAuth login",
        description="Redirect to GitHub OAuth for authentication",
        responses={302: {"description": "Redirect to GitHub OAuth"}},
    )
    def get(self, request):
        """Redirect to GitHub OAuth"""
        if not settings.GITHUB_CLIENT_ID:
            return Response(
                {"error": "GitHub OAuth not configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # In a real implementation, you would use django-allauth or social-auth-app-django
        # For now, return a placeholder response
        return Response(
            {
                "message": "GitHub OAuth endpoint - needs implementation",
                "client_id": getattr(settings, "GITHUB_CLIENT_ID", None),
                "redirect_url": f"{settings.FRONTEND_URL}/auth/callback/github",
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class OAuthCallbackView(generics.GenericAPIView):
    """
    OAuth callback handler for social authentication.
    """

    permission_classes = [AllowAny]
    serializer_class = UserSerializer  # Add serializer class to fix drf-spectacular error

    @extend_schema(
        operation_id="oauth_callback",
        summary="OAuth callback handler",
        description="Handle OAuth callback from social providers",
        responses={200: UserSerializer},
    )
    def post(self, request, provider):
        """Handle OAuth callback"""
        try:
            # Get the OAuth token from the request
            token = request.data.get("token")
            if not token:
                return Response(
                    {"error": "OAuth token is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            # In a real implementation, you would:
            # 1. Verify the OAuth token with the provider
            # 2. Get user information from the provider
            # 3. Create or update the user in your database
            # 4. Generate JWT tokens

            # For now, create a mock user response
            mock_user_data = {
                "id": 1,
                "email": f"user@{provider}.com",
                "username": f"{provider}_user",
                "first_name": "Test",
                "last_name": "User",
                "is_active": True,
                "is_verified": True,
                "created_at": "2026-02-05T02:17:32Z",
                "updated_at": "2026-02-05T02:17:32Z",
            }

            # Generate JWT tokens
            refresh = RefreshToken.for_user(User(**mock_user_data))

            return Response(
                {
                    "user": mock_user_data,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "expires_in": 3600,
                }
            )

        except Exception as e:
            return Response(
                {"error": f"OAuth authentication failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
