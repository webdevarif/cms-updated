"""
Custom authentication backend to allow login with email or username
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authentication backend that allows users to login with either email or username
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user with email or username
        """
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)

        # Try to find user by email first
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # If not found by email, try username
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None

        # Check password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def get_user(self, user_id):
        """
        Get user by ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
