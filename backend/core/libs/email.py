"""
Email utilities for core module.
"""
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_email(subject, template=None, context=None, to=None, text_content=None, from_email=None):
    """
    Centralized email sending function (API-only, no HTML)

    Args:
        subject: Email subject
        template: Template name for rendering
        context: Template context dictionary
        to: Recipient email(s) - string or list
        text_content: Direct text content (overrides template)
        from_email: Sender email (optional)

    Returns:
        bool: True if email sent successfully
    """
    try:
        # Handle recipients
        if isinstance(to, str):
            to = [to]
        elif not to:
            raise ValueError("Recipients (to) must be provided")

        # Set default from email
        if not from_email:
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")

        # Prepare content
        if text_content:
            # Use provided content directly
            text_body = text_content
        elif template and context:
            # Render from template
            text_body = render_to_string(template, context)
        else:
            raise ValueError("Either template+context or text_content must be provided")

        # Send email
        send_mail(
            subject=subject,
            message=text_body,
            from_email=from_email,
            recipient_list=to,
            fail_silently=False,
        )

        logger.info(f"Email sent successfully to {to}: {subject}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")
        return False


class EmailService:
    """
    Centralized email service for sending emails.
    """

    @staticmethod
    def send_template_email(to_email, subject, template_name, context, from_email=None):
        """
        Send email using template

        Args:
            to_email: Recipient email address
            subject: Email subject
            template_name: Template name
            context: Template context
            from_email: Sender email (optional)

        Returns:
            bool: True if email sent successfully
        """
        try:
            # Render text template
            text_content = render_to_string(template_name, context)

            # Send email
            return send_email(
                subject=subject, to=to_email, text_content=text_content, from_email=from_email
            )

        except Exception as e:
            logger.error(f"Failed to send template email to {to_email}: {e}")
            return False

    @staticmethod
    def send_form_notification(form, submission, recipients=None):
        """
        Send form submission notification

        Args:
            form: FormTemplate instance
            submission: FormSubmission instance
            recipients: List of recipient emails (optional)

        Returns:
            bool: True if email sent successfully
        """
        try:
            # Get recipients
            if not recipients:
                recipients = form.settings.get("notification_emails", [])

            if not recipients:
                logger.warning(f"No recipients configured for form {form.form_id}")
                return False

            # Prepare context
            context = {
                "form": form,
                "submission": submission,
                "submission_data": submission.get_formatted_data(),
                "store": form.store,
            }

            # Send to all recipients
            success_count = 0
            for recipient in recipients:
                if send_email(
                    subject=f"New Form Submission: {form.title}",
                    template="forms/submission_notification",
                    context=context,
                    to=recipient,
                ):
                    success_count += 1

            logger.info(f"Form notification sent to {success_count}/{len(recipients)} recipients")
            return success_count > 0

        except Exception as e:
            logger.error(f"Failed to send form notification: {e}")
            return False

    @staticmethod
    def send_auto_reply(form, submission):
        """
        Send auto-reply to form submitter

        Args:
            form: FormTemplate instance
            submission: FormSubmission instance

        Returns:
            bool: True if email sent successfully
        """
        try:
            # Check if auto-reply is enabled
            if not form.settings.get("auto_reply_enabled", False):
                return False

            # Get submitter email from submission data
            submitter_email = None
            for data in submission.submission_data.all():
                field_config = form.fields.get(data.field_name, {})
                if field_config.get("type") == "email":
                    submitter_email = data.field_value
                    break

            if not submitter_email:
                logger.warning("No email found in submission for auto-reply")
                return False

            # Prepare context
            context = {
                "form": form,
                "submission": submission,
                "submission_data": submission.get_formatted_data(),
                "store": form.store,
            }

            # Send auto-reply
            return send_email(
                subject=form.settings.get("auto_reply_subject", f"Thank you for your submission"),
                template="forms/auto_reply",
                context=context,
                to=submitter_email,
            )

        except Exception as e:
            logger.error(f"Failed to send auto-reply: {e}")
            return False
