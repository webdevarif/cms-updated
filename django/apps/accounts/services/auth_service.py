from allauth.socialaccount.models import SocialAccount
from rest_framework.exceptions import ValidationError

from django.contrib.auth import get_user_model

User = get_user_model()


class AuthService:
    """Service for handling authentication operations"""

    @staticmethod
    def get_or_create_social_user(provider, uid, email, name=None):
        """
        Get or create user from social account
        """
        try:
            social_account = SocialAccount.objects.get(provider=provider, uid=uid)
            return social_account.user
        except SocialAccount.DoesNotExist:
            # Create new user
            user = User.objects.create_user(
                email=email,
                username=email.split("@")[0] if email else f"user_{provider}_{uid}",
                first_name=name.split(" ")[0] if name else "",
                last_name=" ".join(name.split(" ")[1:]) if name and " " in name else "",
            )
            return user

    @staticmethod
    def link_social_account(user, provider, uid, extra_data=None):
        """
        Link social account to existing user
        """
        from allauth.socialaccount.models import SocialApp, SocialToken

        social_account = SocialAccount.objects.create(
            user=user, provider=provider, uid=uid, extra_data=extra_data or {}
        )
        return social_account

    @staticmethod
    def validate_social_provider(provider):
        """Validate that provider is supported"""
        supported_providers = ["google", "github", "facebook"]
        if provider not in supported_providers:
            raise ValidationError(f"Provider '{provider}' is not supported")
        return True
