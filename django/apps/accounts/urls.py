from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import SocialAuthViewSet, UserViewSet

# Main router
router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    # Djoser auth endpoints (includes JWT)
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    # Social auth
    path("auth/social/", SocialAuthViewSet.as_view({"post": "social_login"}), name="social-login"),
    # API endpoints
    path("", include(router.urls)),
]


# Authentication:
# POST /auth/users/                    - Register user
# POST /auth/jwt/create/               - Login
# POST /auth/jwt/refresh/             - Refresh token
# GET  /auth/users/me/                 - Current user
# POST /auth/users/set_password/       - Change password

# User Management:
# GET    /users/                        - List users
# POST   /users/                        - Create user (admin)
# GET    /users/{id}/                   - Get user
# PATCH  /users/{id}/                   - Update user
# DELETE /users/{id}/                   - Delete user (admin)
# GET    /users/profile/                - Current user profile
# PATCH  /users/profile/                - Update profile
# POST   /users/{id}/activate/          - Activate user (admin)
# POST   /users/{id}/deactivate/        - Deactivate user (admin)
