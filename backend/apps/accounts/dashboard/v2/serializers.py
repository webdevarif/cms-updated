"""
Dashboard accounts serializers.
"""

from apps.accounts.models.store_user import StoreUser
from apps.accounts.models.user import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """User serializer for dashboard context"""

    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "created_at",
            "updated_at",
            "owner_email",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "owner_email"]


class UserUpdateSerializer(serializers.ModelSerializer):
    """User update serializer for dashboard context"""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "is_active", "is_staff"]


class StoreUserSerializer(serializers.ModelSerializer):
    """Store user serializer for dashboard context"""

    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = StoreUser
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "role",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
