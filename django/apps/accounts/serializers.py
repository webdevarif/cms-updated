from apps.stores.models import Store, StoreAPIKey, StoreMembership, StoreRole, StoreUserRole
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()


class UserCreateSerializer(DjoserUserCreateSerializer):
    """User registration serializer for Djoser"""

    class Meta(DjoserUserCreateSerializer.Meta):
        model = User
        fields = ("id", "email", "username", "password", "first_name", "last_name")


class UserSerializer(serializers.ModelSerializer):
    """User profile serializer with password support"""

    display_name = serializers.ReadOnlyField()
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "display_name",
            "password",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """Create user with password"""
        password = validated_data.pop("password", None)
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        """Update user with password handling"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class StoreSerializer(serializers.ModelSerializer):
    """Store CRUD serializer"""

    owner_name = serializers.CharField(source="owner.display_name", read_only=True)
    memberships_count = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "owner",
            "owner_name",
            "status",
            "access_code",
            "created_at",
            "updated_at",
            "memberships_count",
        ]
        read_only_fields = ["id", "access_code", "owner", "created_at", "updated_at"]

    def get_memberships_count(self, obj):
        return obj.memberships.count()

    def create(self, validated_data):
        """Set owner to current user when creating store"""
        request = self.context.get("request")
        if request and request.user:
            validated_data["owner"] = request.user
        return super().create(validated_data)

    def validate_slug(self, value):
        """Check if slug is already taken"""
        if Store.objects.filter(slug=value).exists():
            raise serializers.ValidationError(
                "A store with this slug already exists. Please choose a different slug."
            )
        return value


class StoreMembershipSerializer(serializers.ModelSerializer):
    """Store membership management serializer"""

    user_email = serializers.CharField(source="user.email", read_only=True)
    store_name = serializers.CharField(source="store.name", read_only=True)

    class Meta:
        model = StoreMembership
        fields = ["id", "store", "user", "role", "joined_at", "user_email", "store_name"]
        read_only_fields = ["id", "joined_at"]


class StoreRoleSerializer(serializers.ModelSerializer):
    """Store role management serializer"""

    users_count = serializers.SerializerMethodField()

    class Meta:
        model = StoreRole
        fields = [
            "id",
            "store",
            "name",
            "slug",
            "description",
            "actions",
            "created_at",
            "updated_at",
            "users_count",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def get_users_count(self, obj):
        return obj.user_assignments.count()

    def validate_actions(self, value):
        """Validate actions against available actions"""
        from .services.roles import RoleService

        invalid_actions = set(value) - set(RoleService.AVAILABLE_ACTIONS)
        if invalid_actions:
            raise serializers.ValidationError(f"Invalid actions: {list(invalid_actions)}")
        return value

    def create(self, validated_data):
        """Generate slug when creating role"""
        from django.utils.text import slugify

        name = validated_data["name"]
        store = validated_data["store"]

        # Generate unique slug
        base_slug = slugify(name)
        slug = base_slug
        counter = 1

        while StoreRole.objects.filter(store=store, slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        validated_data["slug"] = slug
        return super().create(validated_data)


class StoreRoleNestedSerializer(StoreRoleSerializer):
    """Nested role serializer for store endpoints"""

    class Meta(StoreRoleSerializer.Meta):
        read_only_fields = StoreRoleSerializer.Meta.read_only_fields + ["store"]


class StoreUserRoleSerializer(serializers.ModelSerializer):
    """Store user role assignment serializer"""

    user_email = serializers.CharField(source="user.email", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)
    assigned_by_email = serializers.CharField(source="assigned_by.email", read_only=True)

    class Meta:
        model = StoreUserRole
        fields = [
            "id",
            "user",
            "store",
            "role",
            "assigned_at",
            "assigned_by",
            "user_email",
            "role_name",
            "assigned_by_email",
        ]
        read_only_fields = ["id", "assigned_at", "assigned_by"]


class StoreAPIKeySerializer(serializers.ModelSerializer):
    """Store API key management serializer"""

    created_by_email = serializers.CharField(source="created_by.email", read_only=True)

    class Meta:
        model = StoreAPIKey
        fields = [
            "id",
            "store",
            "name",
            "actions",
            "created",
            "last_used_at",
            "created_by",
            "created_by_email",
            "revoked",
        ]
        read_only_fields = ["id", "created", "last_used_at", "created_by"]

    def validate_actions(self, value):
        """Validate actions against available actions"""
        from .services.roles import RoleService

        invalid_actions = set(value) - set(RoleService.AVAILABLE_ACTIONS)
        if invalid_actions:
            raise serializers.ValidationError(f"Invalid actions: {list(invalid_actions)}")
        return value


class StoreAPIKeyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating API keys (returns the key)"""

    api_key = serializers.CharField(write_only=True)

    class Meta:
        model = StoreAPIKey
        fields = ["id", "store", "name", "actions", "api_key", "created"]
        read_only_fields = ["id", "created", "api_key"]

    def validate_actions(self, value):
        """Validate actions against available actions"""
        from .services.roles import RoleService

        invalid_actions = set(value) - set(RoleService.AVAILABLE_ACTIONS)
        if invalid_actions:
            raise serializers.ValidationError(f"Invalid actions: {list(invalid_actions)}")
        return value

    def create(self, validated_data):
        """Create API key and return the key value"""
        from .services.roles import APIKeyService

        store = validated_data["store"]
        name = validated_data["name"]
        actions = validated_data["actions"]
        request = self.context.get("request")
        created_by = request.user if request else None

        api_key, key = APIKeyService.create_api_key(store, name, actions, created_by)

        # Include the key in the response for creation only
        validated_data["api_key"] = key
        return api_key


class StoreAPIKeyNestedSerializer(StoreAPIKeySerializer):
    """Nested API key serializer for store endpoints"""

    class Meta(StoreAPIKeySerializer.Meta):
        read_only_fields = StoreAPIKeySerializer.Meta.read_only_fields + ["store"]


class StoreAPIKeyCreateNestedSerializer(serializers.ModelSerializer):
    """Nested API key creation serializer for store endpoints"""

    api_key = serializers.CharField(read_only=True)  # Make it read-only, set in create method

    class Meta:
        model = StoreAPIKey
        fields = ["id", "store", "name", "actions", "api_key", "created"]
        read_only_fields = ["id", "created", "api_key", "store"]

    def validate_actions(self, value):
        """Validate actions against available actions"""
        from .services.roles import RoleService

        invalid_actions = set(value) - set(RoleService.AVAILABLE_ACTIONS)
        if invalid_actions:
            raise serializers.ValidationError(f"Invalid actions: {list(invalid_actions)}")
        return value

    def create(self, validated_data):
        """Create API key and return the key value"""
        from .services.roles import APIKeyService

        # Get store from context (set in perform_create)
        store = validated_data.pop("store", None)
        name = validated_data["name"]
        actions = validated_data["actions"]
        request = self.context.get("request")
        created_by = request.user if request else None

        api_key, key = APIKeyService.create_api_key(store, name, actions, created_by)

        # Return the API key instance with the key
        api_key.api_key = key  # Temporarily set for response
        return api_key


class StoreDetailSerializer(StoreSerializer):
    """Detailed store information with roles and API keys"""

    roles = StoreRoleSerializer(many=True, read_only=True)
    api_keys = StoreAPIKeySerializer(many=True, read_only=True)
    user_roles = StoreUserRoleSerializer(many=True, read_only=True)

    class Meta(StoreSerializer.Meta):
        fields = StoreSerializer.Meta.fields + ["roles", "api_keys", "user_roles"]


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile with stores and roles"""

    stores = StoreSerializer(many=True, read_only=True)
    user_roles = StoreUserRoleSerializer(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["stores", "user_roles"]


class SafeTokenRefreshSerializer(TokenRefreshSerializer):
    """
    JWT refresh serializer that handles the case where the user referenced
    in the refresh token no longer exists in the database.

    Instead of raising a 500 error, returns a proper JSON validation error.
    """

    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except ObjectDoesNotExist:
            # This happens when the user from the token no longer exists
            raise serializers.ValidationError(
                {"detail": "User account not found for this token.", "code": "user_not_found"}
            )
