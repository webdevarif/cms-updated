"""
Services for SMTP app.
"""
from apps.logs.tasks import log_event_async
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail as django_send_mail
from django.template.loader import render_to_string
from django.utils import timezone


class SmtpEmailService:
    """SMTP-specific email service with logging integration"""

    @classmethod
    def send_email(
        cls,
        to_email: str,
        subject: str,
        html_content: str = "",
        text_content: str = "",
        from_email: str = None,
        smtp_config_id: str = None,
        store=None,
        user=None,
        template_id: str = None,
        context: dict = None,
    ) -> dict:
        """
        Send email using specified SMTP configuration with full logging
        """
        log_data = {
            "to_email": to_email,
            "subject": subject,
            "template_id": str(template_id) if template_id else None,
            "smtp_config_id": str(smtp_config_id) if smtp_config_id else None,
            "store_id": str(store.id) if store else None,
            "user_id": str(user.id) if user else None,
        }

        try:
            # Get SMTP config
            smtp_config = cls._get_smtp_config(smtp_config_id, store)

            # Log email sending attempt
            log_event_async.delay(
                event_type="EMAIL_SEND_ATTEMPT",
                message=f"Sending email to {to_email}",
                store=store,
                user=user,
                metadata=log_data,
            )

            # Send email
            result = django_send_mail(
                subject=subject,
                message=text_content,
                from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                html_message=html_content,
                fail_silently=False,
                auth_user=smtp_config.username,
                auth_password=smtp_config.password,
                connection=smtp_config.get_connection(),
            )

            # Log success
            log_event_async.delay(
                event_type="EMAIL_SEND_SUCCESS",
                message=f"Email sent to {to_email}",
                store=store,
                user=user,
                metadata={
                    **log_data,
                    "message_id": result.message_id if hasattr(result, "message_id") else None,
                },
            )

            return {"success": True, "message_id": getattr(result, "message_id", None)}

        except Exception as e:
            # Log failure
            log_event_async.delay(
                event_type="EMAIL_SEND_FAILED",
                message=f"Failed to send email to {to_email}: {str(e)}",
                level="ERROR",
                store=store,
                user=user,
                metadata={**log_data, "error": str(e), "error_type": e.__class__.__name__},
            )
            raise

    @staticmethod
    def _get_smtp_config(smtp_config_id, store):
        """Get SMTP configuration"""
        from .models import SmtpConfiguration

        if smtp_config_id:
            return SmtpConfiguration.objects.get(id=smtp_config_id)

        return SmtpConfiguration.objects.filter(store=store, is_default=True).first()

    @staticmethod
    @shared_task(bind=True, max_retries=3)
    def send_email_async(self, email_data):
        """Celery task for async email sending"""
        try:
            return SmtpEmailService.send_email(**email_data)
        except Exception as exc:
            self.retry(exc=exc, countdown=60 * (2**self.request.retries))
