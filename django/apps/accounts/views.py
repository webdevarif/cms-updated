from allauth.socialaccount.models import SocialAccount
from apps.stores.models import StoreMembership
from rest_framework import exceptions, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.contrib.auth import get_user_model

from .serializers import StoreMembershipSerializer, UserProfileSerializer, UserSerializer
from .services import AuthService

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """User profile and management with full CRUD operations"""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Admin can see all users, regular users only see themselves"""
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def get_serializer_class(self):
        if self.action == "profile":
            return UserProfileSerializer
        return UserSerializer

    def get_permissions(self):
        """Only superusers can create/delete users, users can update themselves"""
        if self.action in ["create", "destroy"]:
            self.permission_classes = [permissions.IsAdminUser]
        elif self.action in ["update", "partial_update"]:
            # Allow users to update themselves, admins can update anyone
            if self.kwargs.get("pk") and str(self.kwargs.get("pk")) != str(self.request.user.id):
                self.permission_classes = [permissions.IsAdminUser]
            else:
                self.permission_classes = [permissions.IsAuthenticated]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Only admins can create users"""
        if not self.request.user.is_superuser:
            raise exceptions.PermissionDenied("Only administrators can create users")
        serializer.save()

    def perform_update(self, serializer):
        """Allow users to update themselves, admins can update anyone"""
        user = self.get_object()
        if user != self.request.user and not self.request.user.is_superuser:
            raise exceptions.PermissionDenied("You can only update your own profile")
        serializer.save()

    def perform_destroy(self, instance):
        """Only admins can delete users"""
        if not self.request.user.is_superuser:
            raise exceptions.PermissionDenied("Only administrators can delete users")
        instance.delete()

    @action(detail=False, methods=["get", "patch", "put"])
    def profile(self, request):
        """Get or update current user profile"""
        if request.method == "GET":
            serializer = UserProfileSerializer(request.user)
            return Response(serializer.data)

        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a user (admin only)"""
        if not request.user.is_superuser:
            raise exceptions.PermissionDenied("Only administrators can activate users")

        try:
            user = self.get_object()
            user.is_active = True
            user.save()
            return Response(
                {
                    "message": "User activated successfully",
                    "user_id": user.id,
                    "email": user.email,
                    "is_active": user.is_active,
                },
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found", "user_id": pk}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a user (admin only)"""
        if not request.user.is_superuser:
            raise exceptions.PermissionDenied("Only administrators can deactivate users")

        try:
            user = self.get_object()
            user.is_active = False
            user.save()
            return Response(
                {
                    "message": "User deactivated successfully",
                    "user_id": user.id,
                    "email": user.email,
                    "is_active": user.is_active,
                },
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found", "user_id": pk}, status=status.HTTP_404_NOT_FOUND
            )


class SocialAuthViewSet(viewsets.ViewSet):
    """Social authentication endpoints"""

    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["post"], url_path="(?P<provider>[^/.]+)")
    def social_login(self, request, provider=None):
        """Handle social login"""
        AuthService.validate_social_provider(provider)

        uid = request.data.get("uid")
        email = request.data.get("email")
        name = request.data.get("name")

        if not uid or not email:
            return Response(
                {"error": "uid and email are required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = AuthService.get_or_create_social_user(provider, uid, email, name)

            # Link social account
            AuthService.link_social_account(user, provider, uid, request.data)

            # Generate tokens (you might want to use SimpleJWT here)
            from rest_framework_simplejwt.tokens import RefreshToken

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSerializer(user).data,
                }
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
