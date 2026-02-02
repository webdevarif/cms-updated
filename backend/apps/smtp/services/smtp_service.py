"""
Services for SMTP app.
"""

from apps.analytics.services.event_service import EventService
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail as django_send_mail
from django.template.loader import render_to_string
from django.utils import timezone


def send_email(
    store,
    *,
    template_slug=None,
    to_email=None,
    context=None,
    subject=None,
    html_content=None,
    text_content=None,
    async_=True,
    user=None,
):
    """
    Unified email sending interface.

    Args:
        store: Store object for SMTP configuration and scoping
        template_slug: EmailTemplate slug/name for template-based emails
        to_email: Recipient email address (required)
        context: Template context variables for rendering
        subject: Email subject (overrides template subject)
        html_content: HTML content (overrides template content)
        text_content: Text content (overrides template content)
        async_: Send via Celery (default True) or synchronously
        user: User object for logging context

    Returns:
        dict: Email log ID and status information

    Raises:
        ValueError: If required parameters are missing
        Exception: If email sending fails
    """
    if not to_email:
        raise ValueError("to_email is required")

    if not store:
        raise ValueError("store is required")

    # Initialize log data
    log_data = {
        "to_email": to_email,
        "template_slug": template_slug,
        "store_id": str(store.id),
        "user_id": str(user.id) if user else None,
    }

    try:
        # Handle template-based emails
        if template_slug:
            template = _get_email_template(store, template_slug)
            if not template:
                raise ValueError(f"Email template '{template_slug}' not found for store")

            # Render template if context provided
            if context:
                subject = subject or template.subject
                html_content = html_content or render_to_string(
                    f"smtp/emails/{template_slug}.html", context
                )
                text_content = text_content or render_to_string(
                    f"smtp/emails/{template_slug}.txt", context
                )
            else:
                subject = subject or template.subject
                html_content = html_content or template.html_content
                text_content = text_content or template.text_content
        else:
            # Direct content emails
            if not subject:
                raise ValueError("subject is required when not using template")

        # Create EmailLog entry
        email_log = _create_email_log(
            store=store,
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            template_slug=template_slug,
            user=user,
        )

        log_data["email_log_id"] = str(email_log.id)

        # Send email
        if async_:
            # Enqueue via Celery
            result = _send_email_task.delay(
                store_id=str(store.id),
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                template_slug=template_slug,
                context=context,
                user_id=str(user.id) if user else None,
                email_log_id=str(email_log.id),
            )
            email_log.status = "queued"
            email_log.save(update_fields=["status"])
        else:
            # Send synchronously
            result = _send_email_core(
                store=store,
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                smtp_config_id=None,
                template_slug=template_slug,
                context=context,
                user=user,
                email_log=email_log,
            )

        return {
            "success": True,
            "email_log_id": str(email_log.id),
            "status": "queued" if async_ else "sent",
            "message": f"Email {'queued' if async_ else 'sent'} to {to_email}",
        }

    except Exception as e:
        # Update email log with error
        if "email_log" in locals():
            email_log.status = "failed"
            email_log.error_message = str(e)
            email_log.save(update_fields=["status", "error_message"])

        # Log failure
        EventService.log_event(
            event_type="EMAIL_SEND_FAILED",
            event_name=f"Failed to send email to {to_email}: {str(e)}",
            properties={
                "to_email": to_email,
                "subject": subject,
                "error": str(e),
                "level": "ERROR",
            },
            store=store,
        )
        raise


def _send_email_core(
    store,
    to_email,
    subject,
    html_content,
    text_content,
    smtp_config_id=None,
    template_slug=None,
    context=None,
    user=None,
    email_log=None,
):
    """
    Core email sending logic used by both sync and async paths.
    """
    # Get SMTP configuration
    smtp_config = _get_smtp_config(smtp_config_id, store)

    # Log email sending attempt
    EventService.log_event(
        event_type="EMAIL_SEND_ATTEMPT",
        event_name=f"Sending email to {to_email}",
        properties={
            "to_email": to_email,
            "subject": subject,
            "from_email": getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        },
        store=store,
    )

    # Send email
    result = django_send_mail(
        subject=subject,
        message=text_content,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        recipient_list=[to_email],
        html_message=html_content,
        fail_silently=False,
        auth_user=smtp_config.username if smtp_config else None,
        auth_password=smtp_config.get_decrypted_password() if smtp_config else None,
        connection=smtp_config.get_connection() if smtp_config else None,
    )

    # Update email log on success
    if email_log:
        email_log.status = "sent"
        email_log.sent_at = timezone.now()
        email_log.message_id = getattr(result, "message_id", None)
        email_log.save(update_fields=["status", "sent_at", "message_id"])

    # Log success
    EventService.log_event(
        event_type="EMAIL_SEND_SUCCESS",
        event_name=f"Email sent to {to_email}",
        properties={
            "to_email": to_email,
            "subject": subject,
            "message_id": getattr(result, "message_id", None),
        },
        store=store,
    )

    return {"success": True, "message_id": getattr(result, "message_id", None)}


def _get_email_template(store, template_slug):
    """Get email template by store and slug."""
    from .models import EmailTemplate

    try:
        return EmailTemplate.objects.get(store=store, name=template_slug, is_active=True)
    except EmailTemplate.DoesNotExist:
        try:
            return EmailTemplate.objects.get(
                store=store, template_type=template_slug, is_active=True
            )
        except EmailTemplate.DoesNotExist:
            return None


def _create_email_log(store, to_email, subject, html_content, text_content, template_slug, user):
    """Create EmailLog entry."""
    from .models import EmailLog

    return EmailLog.objects.create(
        store=store,
        to_email=to_email,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
        status="queued",
        tracking_id=timezone.now(),
        template=_get_email_template(store, template_slug) if template_slug else None,
        user=user,
    )


@shared_task(bind=True, max_retries=3)
def _send_email_task(
    self,
    store_id,
    to_email,
    subject,
    html_content,
    text_content,
    template_slug=None,
    context=None,
    user_id=None,
    email_log_id=None,
):
    """
    Unified Celery task for email sending.

    Accepts serialized payload from unified send_email API.
    Calls into core logic used by sync path for identical behavior.
    """
    try:
        # Get objects from IDs
        from django.contrib.auth import get_user_model

        from .models import EmailLog, Store

        User = get_user_model()
        store = Store.objects.get(id=store_id)
        user = User.objects.get(id=user_id) if user_id else None
        email_log = EmailLog.objects.get(id=email_log_id) if email_log_id else None

        # Call core logic
        return _send_email_core(
            store=store,
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            smtp_config_id=None,
            template_slug=template_slug,
            context=context,
            user=user,
            email_log=email_log,
        )

    except Exception as exc:
        self.retry(exc=exc, countdown=60 * (2**self.request.retries))


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
        Send email using specified SMTP configuration with full logging.

        DEPRECATED: Use the unified send_email() function instead.
        This method is kept for backward compatibility.
        """
        import warnings

        warnings.warn(
            "SmtpEmailService.send_email() is deprecated. Use send_email() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        return send_email(
            store=store,
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            from_email=from_email,
            smtp_config_id=smtp_config_id,
            template_slug=template_id,
            context=context,
            async_=False,
            user=user,
        )

    @staticmethod
    @shared_task(bind=True, max_retries=3)
    def send_email_async(self, email_data):
        """Celery task for async email sending"""
        import warnings

        warnings.warn(
            "SmtpEmailService.send_email_async() is deprecated. Use send_email(async_=True) instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        try:
            return send_email(**email_data)
        except Exception as exc:
            self.retry(exc=exc, countdown=60 * (2**self.request.retries))

    @staticmethod
    def _get_smtp_config(smtp_config_id, store):
        """Get SMTP configuration"""
        from .models import SmtpConfiguration

        if smtp_config_id:
            return SmtpConfiguration.objects.get(id=smtp_config_id)

        return SmtpConfiguration.objects.filter(store=store, is_active=True).first()
