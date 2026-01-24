"""
Services for payment processing with notifications.
"""
from django.db import transaction
from django.utils import timezone
import logging
from celery import shared_task

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for payment operations"""
    
    @staticmethod
    @transaction.atomic
    def process_payment(order, payment_method, amount):
        """Process a payment"""
        from .models import Payment
        from apps.logs.tasks import log_event_async
        
        # Create payment record
        payment = Payment.objects.create(
            store=order.store,
            order=order,
            payment_method=payment_method,
            amount=amount,
            currency=order.currency,
            status='processing'
        )
        
        # Log payment attempt
        log_event_async.delay({
            'event_type': 'PAYMENT_ATTEMPTED',
            'message': f"Payment {payment.id} attempted for order {order.order_number}",
            'store': order.store,
            'entity_type': 'Payment',
            'entity_id': payment.id,
            'metadata': {
                'order_number': order.order_number,
                'amount': str(amount)
            }
        })
        
        # Process payment (this would integrate with payment provider)
        try:
            # Simulate payment processing
            result = PaymentService._process_with_provider(payment)
            
            if result['success']:
                payment.status = 'completed'
                payment.transaction_id = result['transaction_id']
                payment.save()
                
                # Update order status
                order.status = 'processing'
                order.save()
                
                # Send success notification
                from apps.notifications.services import NotificationService
                NotificationService.notify_user(
                    user=order.user,
                    notification_type='payment.success',
                    context={
                        'title': 'Payment Successful',
                        'message': f'Your payment of ${amount} for order {order.order_number} was successful',
                        'payment_id': payment.id,
                        'order_number': order.order_number,
                        'amount': str(amount)
                    },
                    store=order.store
                )
                
            else:
                payment.status = 'failed'
                payment.metadata = {'error': result['error']}
                payment.save()
                
                # Trigger async payment failure notification with retry
                handle_payment_failure.delay(payment.id)
                
        except Exception as e:
            payment.status = 'failed'
            payment.metadata = {'error': str(e)}
            payment.save()
            
            # Trigger async payment failure notification with retry
            handle_payment_failure.delay(payment.id)
        
        return payment
    
    @staticmethod
    def _process_with_provider(payment):
        """Process payment with external provider (mock implementation)"""
        # This would integrate with actual payment provider
        import random
        
        # Simulate 80% success rate
        if random.random() > 0.2:
            return {
                'success': True,
                'transaction_id': f"txn_{payment.id}_{timezone.now().timestamp()}"
            }
        else:
            return {
                'success': False,
                'error': 'Payment declined by provider'
            }


@shared_task(bind=True, max_retries=3)
def handle_payment_failure(self, payment_id):
    """Handle payment failure with retry logic"""
    from .models import Payment
    from apps.notifications.services import NotificationService
    
    try:
        payment = Payment.objects.get(id=payment_id)
        order = payment.order
        
        # Send failure notification
        NotificationService.notify_user(
            user=order.user,
            notification_type='payment.failed',
            context={
                'title': 'Payment Failed',
                'message': f'Your payment of ${payment.amount} for order {order.order_number} failed. Please update your payment method.',
                'payment_id': payment.id,
                'order_number': order.order_number,
                'amount': str(payment.amount),
                'retry_count': self.request.retries
            },
            store=payment.store
        )
        
        # Log payment failure
        from apps.logs.tasks import log_event_async
        log_event_async.delay({
            'event_type': 'PAYMENT_FAILED',
            'message': f"Payment {payment_id} failed for order {order.order_number}",
            'store': payment.store,
            'entity_type': 'Payment',
            'entity_id': payment.id,
            'metadata': {
                'order_number': order.order_number,
                'amount': str(payment.amount),
                'retry_count': self.request.retries
            }
        })
        
        return {
            'payment_id': payment_id,
            'status': 'notified',
            'retry_count': self.request.retries
        }
        
    except Payment.DoesNotExist:
        logger.error(f"Payment #{payment_id} not found")
        raise
        
    except Exception as exc:
        logger.error(f"Payment failure notification error: {exc}")
        # Retry with exponential backoff
        countdown = 60 * (2 ** self.request.retries)  # 1min, 2min, 4min
        raise self.retry(exc=exc, countdown=countdown)
