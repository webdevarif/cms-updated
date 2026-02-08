"""
Email helper service for forms app.

Provides email sending functionality for form notifications.
"""

from apps.smtp.services.smtp_service import send_email

from django.template.loader import render_to_string


def send_form_notification(email_template, context, store=None):
    """
    Send form notification email using template and context.

    Args:
        email_template: EmailTemplate instance or dict with subject/body
        context: Context dictionary for template rendering
        store: Store object for SMTP configuration (required)

    Returns:
        dict: Result with success status and message
    """
    if not store:
        raise ValueError("store parameter is required for email sending")

    try:
        # Handle both EmailTemplate instance and dict
        if hasattr(email_template, "subject"):
            subject = email_template.subject
            body_html = email_template.body_html
            body_text = email_template.body_text
            template_slug = email_template.name if hasattr(email_template, "name") else None
        else:
            subject = email_template.get("subject", "Form Submission Notification")
            body_html = email_template.get("body_html", "")
            body_text = email_template.get("body_text", "")
            template_slug = None

        # Render email content if template is provided
        if body_html and context:
            body_html = render_to_string("forms/email_notification.html", context)

        # Get recipient email
        if hasattr(email_template, "recipient_email") and email_template.recipient_email:
            recipient_email = email_template.recipient_email
        else:
            recipient_email = context.get("recipient_email", "admin@example.com")

        # Send email using unified SMTP API
        result = send_email(
            store=store,
            to_email=recipient_email,
            subject=subject,
            html_content=body_html,
            text_content=body_text or body_html,
            template_slug=template_slug,
            context=context,
            async_=True,
            user=context.get("user"),
        )

        return {
            "success": True,
            "message": "Email sent successfully",
            "email_log_id": result.get("email_log_id"),
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to send email: {str(e)}"}
