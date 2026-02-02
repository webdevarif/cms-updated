"""
Email service for Digital Farmers CMS.
Provides comprehensive email sending functionality with templates, logging, and async support.
"""

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class EmailService:
    """Shared email management service"""

    @staticmethod
    def send_email(
        subject,
        message,
        from_email=None,
        to_email=None,
        recipient_list=None,
        html_message=None,
        fail_silently=False,
    ):
        """
        Send email using Django's send_mail function
        """
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                to_email=to_email,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=fail_silently,
            )
            logger.info(f"Email sent successfully to {to_email or recipient_list}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

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
        async_send=True,
    ):
        """
        Send email using Django templates
        """
        if async_send:
            # Send asynchronously via Celery
            from .tasks import _send_template_email_async

            _send_template_email_async.delay(
                to_email=to_email,
                subject=subject,
                template_name=template_name,
                context=context,
                from_email=from_email,
                html_template=html_template,
                store=store,
                user=user,
            )
            return True
        else:
            # Send synchronously
            return EmailService._send_template_email_sync(
                to_email=to_email,
                subject=subject,
                template_name=template_name,
                context=context,
                from_email=from_email,
                html_template=html_template,
                store=store,
                user=user,
            )

    @staticmethod
    def _send_template_email_sync(
        to_email,
        subject,
        template_name,
        context,
        from_email=None,
        html_template=None,
        store=None,
        user=None,
    ):
        """Synchronous template email sending"""
        try:
            # Render email content
            text_content = render_to_string(f"emails/{template_name}.txt", context)

            if html_template:
                html_content = render_to_string(f"emails/{html_template}.html", context)
            else:
                html_content = render_to_string(f"emails/{template_name}.html", context)

            # Send email
            send_mail(
                subject=subject,
                message=text_content,
                from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                html_message=html_content,
                fail_silently=False,
            )

            logger.info(f"Template email sent to {to_email} with template {template_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to send template email to {to_email}: {str(e)}", exc_info=True)
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
            "user": user,
            "store": store,
            "reset_token": reset_token,
            "reset_url": f"{settings.FRONTEND_URL}/reset-password/{reset_token}",
        }

        return EmailService.send_template_email(
            to_email=user.email,
            subject=f"Password Reset - {store.name}",
            template_name="password_reset",
            context=context,
            store=store,
            user=user,
            async_send=async_send,
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
            "user": user,
            "store": store,
            "verification_token": verification_token,
            "verification_url": f"{settings.FRONTEND_URL}/verify-email/{verification_token}",
        }

        return EmailService.send_template_email(
            to_email=user.email,
            subject=f"Email Verification - {store.name}",
            template_name="email_verification",
            context=context,
            store=store,
            user=user,
            async_send=async_send,
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
            "user": user,
            "store": store,
            "login_url": f"{settings.FRONTEND_URL}/login",
        }

        return EmailService.send_template_email(
            to_email=user.email,
            subject=f"Welcome to {store.name}!",
            template_name="welcome",
            context=context,
            store=store,
            user=user,
            async_send=async_send,
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
            "user": user,
            "store": store,
            "order": order,
            "order_url": f"{settings.FRONTEND_URL}/orders/{order.id}",
        }

        return EmailService.send_template_email(
            to_email=user.email,
            subject=f"Order Confirmation - {store.name}",
            template_name="order_confirmation",
            context=context,
            store=store,
            user=user,
            async_send=async_send,
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
            "user": user,
            "store": store,
            "order": order,
            "tracking_number": tracking_number,
            "tracking_url": f"{settings.TRACKING_URL}/{tracking_number}",
        }

        return EmailService.send_template_email(
            to_email=user.email,
            subject=f"Your Order Has Shipped - {store.name}",
            template_name="shipping_notification",
            context=context,
            store=store,
            user=user,
            async_send=async_send,
        )


# Celery tasks for async email sending
@shared_task(bind=True, max_retries=3)
def _send_template_email_async(
    self,
    to_email,
    subject,
    template_name,
    context,
    from_email,
    html_template,
    store,
    user,
):
    """Async task for sending template emails"""
    try:
        return EmailService._send_template_email_sync(
            to_email,
            subject,
            template_name,
            context,
            from_email,
            html_template,
            store,
            user,
        )
    except Exception as exc:
        logger.error(f"Async email send failed: {exc}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        return False
