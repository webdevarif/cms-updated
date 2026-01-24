"""
Tasks for webhooks module.
"""
from celery import shared_task
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def deliver_webhook(self, delivery_id):
    """Async webhook delivery task"""
    from .models import WebhookDelivery
    from .services import WebhookService
    
    try:
        delivery = WebhookDelivery.objects.select_related('webhook').get(id=delivery_id)
        
        # Skip if already successful
        if delivery.status == 'success':
            return {'status': 'already_delivered'}
        
        # Deliver webhook
        result = WebhookService.deliver_webhook_sync(delivery)
        
        return {
            'delivery_id': delivery_id,
            'status': result.status,
            'response_status': result.response_status
        }
        
    except WebhookDelivery.DoesNotExist:
        logger.error(f"Webhook delivery #{delivery_id} not found")
        raise
        
    except Exception as exc:
        logger.error(f"Webhook delivery failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def cleanup_old_deliveries(days=90):
    """Clean up old webhook delivery records"""
    from django.utils import timezone
    from .models import WebhookDelivery
    
    cutoff = timezone.now() - timezone.timedelta(days=days)
    deleted_count = WebhookDelivery.objects.filter(
        triggered_at__lt=cutoff,
        status='success'
    ).delete()[0]
    
    logger.info(f"Cleaned up {deleted_count} old webhook deliveries")
    return deleted_count
