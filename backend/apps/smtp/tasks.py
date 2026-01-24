"""
Celery tasks for SMTP app.
"""
from celery import shared_task
from django.utils import timezone
from .models import EmailLog
from .services import SmtpEmailService


@shared_task(bind=True, max_retries=3)
def process_email_queue(self):
    """Process queued emails"""
    batch_size = getattr(settings, 'EMAIL_BATCH_SIZE', 50)
    
    # Get pending emails, ordered by priority and creation time
    queued_emails = EmailLog.objects.filter(
        status='queued',
        scheduled_at__lte=timezone.now()
    ).order_by('created_at')[:batch_size]
    
    for email in queued_emails:
        try:
            # Send email
            result = SmtpEmailService.send_email_async.delay({
                'to_email': email.to_email,
                'subject': email.subject,
                'html_content': email.html_content,
                'text_content': email.text_content,
                'smtp_config_id': str(email.smtp_config_id),
                'store_id': str(email.store_id),
                'template_id': str(email.template_id) if email.template_id else None
            })
            
            # Mark as sent
            email.status = 'sent'
            email.sent_at = timezone.now()
            email.save(update_fields=['status', 'sent_at'])
            
        except Exception as e:
            # Handle retries
            if email.retry_count >= 3:
                email.status = 'failed'
                email.error_message = str(e)
                email.save()
            else:
                email.retry_count += 1
                email.save()
            
            self.retry(exc=e, countdown=60 * (2 ** email.retry_count))
