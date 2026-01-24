"""
Email channel for notifications.
"""
import logging
from .base import BaseChannel

logger = logging.getLogger(__name__)


class EmailChannel(BaseChannel):
    """Email notification channel"""
    
    @staticmethod
    def send(notification):
        """Send notification via email"""
        if not notification.user or not notification.user.email:
            logger.warning(f"No email for notification #{notification.id}")
            return
        
        from ..models import NotificationTemplate
        from apps.smtp.services import SmtpEmailService
        
        # Get or create email template
        template = NotificationTemplate.objects.filter(
            store=notification.store,
            notification_type=notification.notification_type
        ).first()
        
        if template:
            rendered = template.render(notification.metadata)
            subject = rendered.get('email_subject', notification.title)
            body = rendered.get('email_body', notification.message)
        else:
            subject = notification.title
            body = notification.message
        
        # Send via SMTP service
        SmtpEmailService.send_email_async.delay({
            'to_email': notification.user.email,
            'subject': subject,
            'html_content': body,
            'text_content': notification.message,
            'store': notification.store,
            'template_id': template.id if template else None
        })
        
        logger.info(f"Email notification sent to {notification.user.email}")
    
    @staticmethod
    def validate_config(notification):
        """Validate email configuration"""
        return notification.user and notification.user.email
