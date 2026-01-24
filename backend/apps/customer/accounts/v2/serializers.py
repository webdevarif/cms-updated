"""
Serializers for customer accounts API.

Serializers for customer profile and preferences management.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from apps.accounts.models import User, UserPreferences


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
        preferences, created = UserPreferences.objects.get_or_create(user=obj)
        return {
            'email_notifications': preferences.email_notifications,
            'push_notifications': preferences.push_notifications,
            'theme': preferences.theme,
            'language': preferences.language,
            'show_email': preferences.show_email,
            'show_online_status': preferences.show_online_status,
        }


class CustomerProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating customer profile"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CustomerPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for customer preferences"""
    
    class Meta:
        model = UserPreferences
        fields = ['email_notifications', 'push_notifications', 'theme', 
                  'language', 'show_email', 'show_online_status']


class CustomerChangePasswordSerializer(serializers.Serializer):
    """Serializer for customer password change"""
    current_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        
        # Validate password strength
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        
        return attrs


class CustomerDeleteAccountSerializer(serializers.Serializer):
    """Serializer for customer account deletion"""
    password = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate_password(self, value):
        """Validate password is correct"""
        if not self.context['request'].user.check_password(value):
            raise ValidationError("Invalid password")
        return value
