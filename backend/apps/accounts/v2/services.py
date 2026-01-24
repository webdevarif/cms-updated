"""
Authentication services for Digital Farmers CMS.

Shared authentication service for JWT token management.
"""
from django.contrib.auth import login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Shared authentication service"""
    
    @staticmethod
    def generate_token(user):
        """Generate JWT token for user"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    @staticmethod
    def verify_token(token):
        """Verify JWT token"""
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token)
            return access_token.payload
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    @staticmethod
    def send_password_reset_email(user, store):
        """Send password reset email"""
        from apps.smtp.services import SmtpEmailService
        token = AuthService.generate_reset_token(user)
        SmtpEmailService.send_email_async.delay({
            'to_email': user.email,
            'subject': f'Password Reset - {store.name}',
            'html_content': f'<p>Your token: {token}</p>',
            'text_content': f'Token: {token}',
            'store': store,
            'template_id': None,
            'context': {'reset_token': token},
        })
    
    @staticmethod
    def generate_reset_token(user):
        """Generate password reset token"""
        from django.utils.crypto import get_random_string
        return get_random_string(64)
