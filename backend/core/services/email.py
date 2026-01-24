"""
Consolidated Email Service for Digital Farmers CMS.

Handles all email sending including transactional emails and template emails.
Integrates with logging, Celery for async sending, and proper error handling.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db import transaction
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Centralized email service for DFCMS.
    
    Combines transactional emails (password reset, verification, etc.)
    with generic template email functionality.
    """
    
    @staticmethod
    def send_template_email(
        to_email,
        subject,
        template_name,
        context,
        from_email=None,
        html_template=None,
        store=None,
        user=None,
        async_send=True
    ):
        """
        Send email using Django template.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            template_name: Template name (without .txt/.html extension)
            context: Template context dictionary
            from_email: Sender email (optional)
            html_template: HTML template name (optional)
            store: Store instance for logging (optional)
            user: User instance for logging (optional)
            async_send: Whether to send asynchronously (default: True)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if async_send:
            return EmailService._send_template_email_async.delay(
                to_email, subject, template_name, context, from_email, html_template, store, user
            )
        else:
            return EmailService._send_template_email_sync(
                to_email, subject, template_name, context, from_email, html_template, store, user
            )
    
    @staticmethod
    def _send_template_email_sync(
        to_email, subject, template_name, context, from_email, html_template, store, user
    ):
        """Synchronous template email sending"""
        try:
            # Render email content
            text_content = render_to_string(f'emails/{template_name}.txt', context)
            
            if html_template:
                html_content = render_to_string(f'emails/{html_template}.html', context)
            else:
                html_content = render_to_string(f'emails/{template_name}.html', context)
            
            # Send email
            send_mail(
                subject=subject,
                message=text_content,
                from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                html_message=html_content,
                fail_silently=False,
            )
            
            # Log email send
            EmailService._log_email_send(
                event_type='EMAIL_SEND_SUCCESS',
                message=f"Template email sent to {to_email}",
                to_email=to_email,
                template_type=template_name,
                store=store,
                user=user
            )
            
            logger.info(f"Template email sent to {to_email} with template {template_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send template email to {to_email}: {str(e)}", exc_info=True)
            
            # Log email failure
            EmailService._log_email_send(
                event_type='EMAIL_SEND_FAILED',
                message=f"Failed to send template email to {to_email}: {str(e)}",
                to_email=to_email,
                template_type=template_name,
                store=store,
                user=user,
                error=str(e)
            )
            
            return False
    
    @staticmethod
    def send_password_reset_email(user, store, reset_token, async_send=True):
        """
        Send password reset email to user
        
        Args:
            user: User instance
            store: Store instance
            reset_token: Password reset token
            async_send: Whether to send asynchronously (default: True)
        """
        context = {
            'user': user,
            'store': store,
            'reset_token': reset_token,
            'reset_url': f"{settings.FRONTEND_URL}/reset-password/{reset_token}"
        }
        
        return EmailService.send_template_email(
            to_email=user.email,
            subject=f'Password Reset - {store.name}',
            template_name='password_reset',
            context=context,
            store=store,
            user=user,
            async_send=async_send
        )
    
    @staticmethod
    def send_verification_email(user, store, verification_token, async_send=True):
        """
        Send email verification email to user
        
        Args:
            user: User instance
            store: Store instance
            verification_token: Email verification token
            async_send: Whether to send asynchronously (default: True)
        """
        context = {
            'user': user,
            'store': store,
            'verification_token': verification_token,
            'verification_url': f"{settings.FRONTEND_URL}/verify-email/{verification_token}"
        }
        
        return EmailService.send_template_email(
            to_email=user.email,
            subject=f'Email Verification - {store.name}',
            template_name='email_verification',
            context=context,
            store=store,
            user=user,
            async_send=async_send
        )
    
    @staticmethod
    def send_welcome_email(user, store, async_send=True):
        """
        Send welcome email to new user
        
        Args:
            user: User instance
            store: Store instance
            async_send: Whether to send asynchronously (default: True)
        """
        context = {
            'user': user,
            'store': store,
            'login_url': f"{settings.FRONTEND_URL}/login"
        }
        
        return EmailService.send_template_email(
            to_email=user.email,
            subject=f'Welcome to {store.name}!',
            template_name='welcome',
            context=context,
            store=store,
            user=user,
            async_send=async_send
        )
    
    @staticmethod
    def send_order_confirmation_email(user, store, order, async_send=True):
        """
        Send order confirmation email
        
        Args:
            user: User instance
            store: Store instance
            order: Order instance
            async_send: Whether to send asynchronously (default: True)
        """
        context = {
            'user': user,
            'store': store,
            'order': order,
            'order_url': f"{settings.FRONTEND_URL}/orders/{order.id}"
        }
        
        return EmailService.send_template_email(
            to_email=user.email,
            subject=f'Order Confirmation - {store.name}',
            template_name='order_confirmation',
            context=context,
            store=store,
            user=user,
            async_send=async_send
        )
    
    @staticmethod
    def send_shipping_notification_email(user, store, order, tracking_number, async_send=True):
        """
        Send shipping notification email
        
        Args:
            user: User instance
            store: Store instance
            order: Order instance
            tracking_number: Shipping tracking number
            async_send: Whether to send asynchronously (default: True)
        """
        context = {
            'user': user,
            'store': store,
            'order': order,
            'tracking_number': tracking_number,
            'tracking_url': f"{settings.TRACKING_URL}/{tracking_number}"
        }
        
        return EmailService.send_template_email(
            to_email=user.email,
            subject=f'Your Order Has Shipped - {store.name}',
            template_name='shipping_notification',
            context=context,
            store=store,
            user=user,
            async_send=async_send
        )
    
    @staticmethod
    def _log_email_send(
        event_type,
        message,
        to_email,
        template_type,
        store=None,
        user=None,
        error=None
    ):
        """Log email send events"""
        try:
            from apps.logs.tasks import log_event_async
            
            metadata = {
                'to_email': to_email,
                'template_type': template_type,
                'email_type': template_type
            }
            
            if error:
                metadata['error'] = error
            
            log_event_async.delay(
                event_type=event_type,
                message=message,
                store=store,
                user=user,
                metadata=metadata
            )
        except ImportError:
            # Fallback if logs app not available
            logger.info(f"Email log: {event_type} - {message}")
        except Exception as e:
            logger.error(f"Failed to log email event: {e}")


# Celery tasks for async email sending
@shared_task(bind=True, max_retries=3)
def _send_template_email_async(
    self, to_email, subject, template_name, context, from_email, html_template, store, user
):
    """Async task for sending template emails"""
    try:
        return EmailService._send_template_email_sync(
            to_email, subject, template_name, context, from_email, html_template, store, user
        )
    except Exception as exc:
        logger.error(f"Async email send failed: {exc}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        return False
