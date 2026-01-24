"""
Webhook handlers for email providers.
"""
import hmac
import hashlib
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..models import EmailLog

logger = logging.getLogger(__name__)

# Webhook configuration
WEBHOOK_CONFIG = {
    'sendgrid': {
        'signing_key': getattr(settings, 'SENDGRID_WEBHOOK_SIGNING_KEY', ''),
        'signature_header': 'X-Twilio-Email-Event-Webhook-Signature',
        'timestamp_header': 'X-Twilio-Email-Event-Webhook-Timestamp',
        'max_age_seconds': 300,
    },
    'mailgun': {
        'signing_key': getattr(settings, 'MAILGUN_WEBHOOK_SIGNING_KEY', ''),
        'signature_param': 'signature',
        'timestamp_param': 'timestamp',
        'token_param': 'token',
    }
}


@method_decorator(csrf_exempt, name='dispatch')
class EmailWebhookView(APIView):
    """Email webhook handler with signature verification"""
    permission_classes = [AllowAny]
    
    def verify_webhook_signature(self, request, provider):
        """Verify webhook signature using provider's signing key"""
        config = WEBHOOK_CONFIG.get(provider, {})
        
        if provider == 'sendgrid':
            signature = request.headers.get(config['signature_header'])
            timestamp = request.headers.get(config['timestamp_header'])
            
            if not all([signature, timestamp, config['signing_key']]):
                logger.warning('Missing required signature headers or signing key')
                return False
                
            # Verify timestamp
            try:
                event_time = datetime.fromtimestamp(int(timestamp))
                if (datetime.utcnow() - event_time) > timedelta(seconds=config['max_age_seconds']):
                    logger.warning('Webhook timestamp too old')
                    return False
            except (ValueError, TypeError):
                logger.warning('Invalid timestamp in webhook')
                return False
                
            # Verify signature
            payload = f"{timestamp}{request.body.decode('utf-8')}"
            expected_signature = hmac.new(
                key=config['signing_key'].encode('utf-8'),
                msg=payload.encode('utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        elif provider == 'mailgun':
            data = request.data
            signature = data.get(config['signature_param'])
            timestamp = data.get(config['timestamp_param'])
            token = data.get(config['token_param'])
            
            if not all([signature, timestamp, token, config['signing_key']]):
                return False
                
            # Verify timestamp
            try:
                import time
                if (time.time() - int(timestamp)) > config.get('max_age_seconds', 300):
                    return False
            except (ValueError, TypeError):
                return False
                
            # Verify signature
            signing_data = f"{timestamp}{token}"
            expected_signature = hmac.new(
                key=config['signing_key'].encode('utf-8'),
                msg=signing_data.encode('utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        return False
    
    def post(self, request, provider=None, *args, **kwargs):
        """Handle email webhooks from various providers"""
        try:
            provider = provider or request.GET.get('provider', 'sendgrid')
            
            # Verify webhook signature
            if not self.verify_webhook_signature(request, provider):
                logger.warning(f'Invalid webhook signature from {provider}')
                return Response(
                    {'error': 'Invalid signature'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Get handler for this provider
            handler = getattr(self, f'handle_{provider}', None)
            if not handler:
                return Response(
                    {'error': 'Unsupported email provider'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Process events
            events = handler(request.data)
            return Response({
                'status': 'success',
                'events_processed': len(events)
            })
            
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def handle_sendgrid(self, data):
        """Process SendGrid webhook events"""
        events = []
        event_list = data if isinstance(data, list) else [data]
        
        for event in event_list:
            try:
                event_type = event.get('event')
                tracking_id = event.get('tracking_id') or event.get('email_id')
                
                if not tracking_id:
                    continue
                
                # Map SendGrid event types to our system
                event_map = {
                    'processed': 'sent',
                    'delivered': 'delivered',
                    'open': 'opened',
                    'click': 'clicked',
                    'bounce': 'bounced',
                    'dropped': 'dropped',
                    'spamreport': 'spam',
                    'unsubscribe': 'unsubscribed'
                }
                
                mapped_type = event_map.get(event_type)
                if not mapped_type:
                    continue
                
                # Find and update email log
                email_log = EmailLog.objects.get(tracking_id=tracking_id)
                email_log.add_tracking_event(
                    event_type=mapped_type,
                    event_data=event
                )
                
                # Update email status if needed
                if mapped_type in ['delivered', 'bounced', 'dropped']:
                    email_log.status = mapped_type
                    email_log.save(update_fields=['status', 'updated_at'])
                
                events.append(mapped_type)
                
            except EmailLog.DoesNotExist:
                logger.warning(f"Email log not found for tracking_id: {tracking_id}")
            except Exception as e:
                logger.error(f"Error processing {event_type} event: {str(e)}")
        
        return events
