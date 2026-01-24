"""
Serializers for dashboard accounts API.

Serializers for user management and role assignment.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from apps.accounts.models import User, StoreUser, Role
from core.services.user import UserService


class StoreUserSerializer(serializers.ModelSerializer):
    """Serializer for store user data"""
    user = CustomerProfileSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = StoreUser
        fields = ['id', 'user', 'store', 'role', 'role_display', 'is_active', 'created_at']
        read_only_fields = ['id', 'user', 'store', 'created_at']


class StoreUserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating store user"""
    user = CustomerProfileSerializer()
    
    class Meta:
        model = StoreUser
        fields = ['user', 'role', 'is_active']
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = user_data.pop('password', None)
        
        # Create user using centralized service
        user = UserService.create_user(**user_data)
        if password:
            user.set_password(password)
            user.save()
        
        # Create store user
        store_user = StoreUser.objects.create(
            user=user,
            store=self.context['store'],
            **validated_data
        )
        
        return store_user


class StoreUserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating store user"""
    
    class Meta:
        model = StoreUser
        fields = ['role', 'is_active']


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for role data"""
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class RoleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating role"""
    
    class Meta:
        model = Role
        fields = ['name', 'permissions', 'is_active']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CustomerProfileSerializer(serializers.ModelSerializer):
    """Serializer for customer profile data"""
    preferences = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 
                  'is_active', 'is_verified', 'created_at', 'preferences']
        read_only_fields = ['id', 'is_active', 'is_verified', 'created_at']
    
    def get_preferences(self, obj):
        """Get user preferences"""
        from apps.accounts.models import UserPreferences
        preferences, created = UserPreferences.objects.get_or_create(user=obj)
        return {
            'email_notifications': preferences.email_notifications,
            'push_notifications': preferences.push_notifications,
            'theme': preferences.theme,
            'language': preferences.language,
            'show_email': preferences.show_email,
            'show_online_status': preferences.show_online_status,
        }
