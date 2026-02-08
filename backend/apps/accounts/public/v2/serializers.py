"""
Public accounts serializers.
"""

from apps.accounts.models import User
from rest_framework import serializers

from django.contrib.auth import authenticate


class LoginSerializer(serializers.Serializer):
    """User login serializer - supports both email and username"""

    login = serializers.CharField()  # Can be email or username
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate user credentials"""
        login_field = data["login"]
        password = data["password"]

        # Try to find user by email or username
        user = None
        try:
            if "@" in login_field:
                # Looks like an email
                user = User.objects.get(email=login_field)
            else:
                # Treat as username
                user = User.objects.get(username=login_field)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials")

        # Store user in validated data for use in view
        data["user"] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """User serializer for API responses"""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_active",
            "is_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer"""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]

    def validate(self, data):
        """Validate registration data"""
        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError("Email already registered")

        if User.objects.filter(username=data["username"]).exists():
            raise serializers.ValidationError("Username already taken")

        return data

    def create(self, validated_data):
        """Create new user"""
        from apps.accounts.models import User

        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


class PasswordResetSerializer(serializers.Serializer):
    """Password reset serializer"""

    email = serializers.EmailField()

    def validate_email(self, value):
        """Validate email exists"""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email not found")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Password reset confirmation serializer"""

    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    new_password_confirm = serializers.CharField()

    def validate(self, data):
        """Validate password reset"""
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError("Passwords don't match")
        return data
