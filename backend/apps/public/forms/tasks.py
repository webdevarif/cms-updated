"""
Tasks for forms module.
"""
from celery import shared_task
import logging
from django.utils import timezone
from apps.smtp.services import SmtpEmailService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_form_notifications(submission_id):
    """Send form notification emails asynchronously"""
    try:
        from .models import FormSubmission

        submission = FormSubmission.objects.select_related('form_template').get(id=submission_id)
        form_template = submission.form_template

        email_templates = form_template.email_templates.filter(is_active=True)

        for email_template in email_templates:
            context = {
                'form_title': form_template.title,
                'submission_data': submission.data,
                'submitted_at': submission.submitted_at,
                'submission_id': submission.id
            }

            rendered = email_template.render_with_context(context)

            recipients = _get_email_recipients(
                email_template, submission.data, form_template.store
            )

            if not recipients:
                continue

            SmtpEmailService.send_email_async.delay({
                'to_email': recipients[0],
                'subject': rendered['subject'],
                'html_content': rendered['html'],
                'text_content': rendered['text'],
                'store': form_template.store,
                'template_id': email_template.id,
                'context': context
            })

        submission.email_sent = True
        submission.email_sent_at = timezone.now()
        submission.status = 'sent'
        submission.save(update_fields=['email_sent', 'email_sent_at', 'status'])

    except Exception as exc:
        logger.error(f"Failed to send form notifications: {exc}")
        submission.status = 'failed'
        submission.save(update_fields=['status'])


def _get_email_recipients(email_template, submission_data, store):
    """Determine email recipients from template configuration"""
    if email_template.recipient_type == 'custom' and email_template.recipient_email:
        return [email_template.recipient_email]
    
    # Auto-detect from form fields
    if email_template.auto_detect_recipient:
        recipient_email = submission_data.get('email')
        if recipient_email:
            return [recipient_email]
    
    # Default to admin
    return [store.owner.email] if store.owner else []
