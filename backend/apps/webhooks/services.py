"""
Services for webhooks module.
"""
import requests
from django.utils import timezone
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class WebhookService:
    """Shared webhook management service"""
    
    @staticmethod
    @transaction.atomic
    def trigger_webhook(webhook, event_type, event_data, store):
        """Trigger a webhook with retry logic"""
        # Check if webhook is subscribed to this event
        if not webhook.is_event_subscribed(event_type, event_data):
            return None
        
        # Create delivery record
        delivery = WebhookService.create_delivery_record(webhook, event_type, event_data)
        
        # Update webhook last triggered timestamp
        webhook.last_triggered_at = timezone.now()
        webhook.save(update_fields=['last_triggered_at'])
        
        # Trigger async delivery
        from .tasks import deliver_webhook
        deliver_webhook.delay(delivery.id)
        
        return delivery
    
    @staticmethod
    def deliver_webhook_sync(delivery):
        """Synchronous webhook delivery"""
        webhook = delivery.webhook
        
        # Prepare request
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': webhook.generate_signature(delivery.payload),
            'X-Webhook-Event': delivery.event_type,
            'X-Webhook-ID': str(delivery.id),
            'X-Store-ID': str(webhook.store.id),
            **webhook.headers
        }
        
        # Measure delivery time
        start_time = timezone.now()
        
        try:
            response = requests.request(
                method=webhook.method,
                url=webhook.url,
                json=delivery.payload,
                headers=headers,
                verify=webhook.verify_ssl,
                timeout=30
            )
            
            # Calculate duration
            duration_ms = int((timezone.now() - start_time).total_seconds() * 1000)
            
            # Update delivery
            delivery.response_status = response.status_code
            delivery.response_body = response.text[:10000]
            delivery.response_headers = dict(response.headers)
            delivery.delivered_at = timezone.now()
            delivery.duration_ms = duration_ms
            
            # Determine status
            if 200 <= response.status_code < 300:
                delivery.status = 'success'
            else:
                delivery.status = 'failed'
                delivery.error_message = f"HTTP {response.status_code}"
                delivery.error_code = 'HTTP_ERROR'
            
            delivery.save(update_fields=[
                'response_status', 'response_body', 'response_headers',
                'delivered_at', 'duration_ms', 'status', 'error_message', 'error_code'
            ])
            
            # Log delivery
            logger.info(
                f"Webhook #{delivery.id} delivered to {webhook.url} "
                f"- Status: {response.status_code} - Duration: {duration_ms}ms"
            )
            
        except requests.exceptions.Timeout:
            delivery.status = 'failed'
            delivery.error_message = 'Request timeout'
            delivery.error_code = 'TIMEOUT'
            delivery.save(update_fields=['status', 'error_message', 'error_code'])
            logger.error(f"Webhook #{delivery.id} timeout")
            
        except requests.exceptions.SSLError as e:
            delivery.status = 'failed'
            delivery.error_message = f'SSL error: {str(e)}'
            delivery.error_code = 'SSL_ERROR'
            delivery.save(update_fields=['status', 'error_message', 'error_code'])
            logger.error(f"Webhook #{delivery.id} SSL error: {e}")
            
        except requests.exceptions.RequestException as e:
            delivery.status = 'failed'
            delivery.error_message = str(e)
            delivery.error_code = 'REQUEST_ERROR'
            delivery.save(update_fields=['status', 'error_message', 'error_code'])
            logger.error(f"Webhook #{delivery.id} request error: {e}")
        
        # Schedule retry if failed and retries remaining
        if delivery.status == 'failed' and delivery.attempt_number < webhook.max_retries:
            WebhookService.schedule_retry(delivery)
        
        return delivery
    
    @staticmethod
    def schedule_retry(delivery):
        """Schedule webhook delivery retry with exponential backoff"""
        webhook = delivery.webhook
        
        # Calculate retry delay with exponential backoff
        retry_delay = webhook.retry_delay * (webhook.retry_backoff_multiplier ** (delivery.attempt_number - 1))
        
        # Update delivery
        delivery.status = 'retrying'
        delivery.attempt_number += 1
        delivery.next_retry_at = timezone.now() + timezone.timedelta(seconds=retry_delay)
        delivery.save(update_fields=['status', 'attempt_number', 'next_retry_at'])
        
        # Schedule retry task
        from .tasks import deliver_webhook
        deliver_webhook.apply_async(
            args=[delivery.id],
            eta=delivery.next_retry_at
        )
        
        logger.info(
            f"Webhook #{delivery.id} scheduled for retry #{delivery.attempt_number} "
            f"in {retry_delay}s"
        )
