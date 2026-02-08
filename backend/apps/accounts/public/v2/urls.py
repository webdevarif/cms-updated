"""
URL configuration for accounts public API v2.
"""

from apps.accounts.public.v2.oauth_views import (
    FacebookOAuthView,
    GithubOAuthView,
    GoogleOAuthView,
    OAuthCallbackView,
)
from apps.accounts.public.v2.views import (
    ForgotPasswordView,
    PublicLoginView,
    PublicRegistrationView,
    ResetPasswordView,
    TokenRefreshView,
    UserProfileView,
)

from django.urls import path

urlpatterns = [
    path("login/", PublicLoginView.as_view(), name="login"),
    path("register/", PublicRegistrationView.as_view(), name="register"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", UserProfileView.as_view(), name="user_profile"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    # OAuth endpoints
    path("oauth/google/", GoogleOAuthView.as_view(), name="google_oauth"),
    path("oauth/facebook/", FacebookOAuthView.as_view(), name="facebook_oauth"),
    path("oauth/github/", GithubOAuthView.as_view(), name="github_oauth"),
    path("oauth/<str:provider>/callback/", OAuthCallbackView.as_view(), name="oauth_callback"),
]
