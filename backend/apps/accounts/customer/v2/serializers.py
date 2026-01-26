"""
Customer accounts serializers.
"""
from rest_framework import serializers
from apps.accounts.models.user import User


class UserSerializer(serializers.ModelSerializer):
    """User serializer for customer context"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class UserUpdateSerializer(serializers.ModelSerializer):
    """User update serializer for customer context"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """Password change serializer"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
