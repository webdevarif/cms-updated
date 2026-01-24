"""
Signals for ecommerce app.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, Order, Inventory
from apps.logs.tasks import log_event_async
from apps.notifications.services import NotificationService
from apps.public.translations.services import TranslationService


@receiver(post_save, sender=Product)
def create_product_translation_keys(sender, instance, created, **kwargs):
    """Create translation keys for product fields"""
    if created:
        # Create translation keys for translatable fields
        fields_to_translate = ['title', 'description', 'short_description']
        
        for field in fields_to_translate:
            field_value = getattr(instance, field)
            if field_value:
                key = f"ecommerce.{field}.{instance.id}"
                TranslationService.get_or_create_translation_key(
                    key=key,
                    namespace='ecommerce',
                    content_type='html' if field in ['description'] else 'plain',
                    description=f"Product {field.replace('_', ' ').title()} for product: {instance.title}"
                )


@receiver(post_save, sender=Product)
def log_product_change(sender, instance, created, **kwargs):
    """Log product changes"""
    if created:
        event_type = 'PRODUCT_CREATED'
        message = f"Product created: {instance.title}"
    else:
        event_type = 'PRODUCT_UPDATED'
        message = f"Product updated: {instance.title}"
    
    log_event_async.delay({
        'event_type': event_type,
        'message': message,
        'store': instance.store,
        'entity_type': 'Product',
        'entity_id': instance.id,
        'metadata': {
            'sku': instance.sku,
            'price': str(instance.base_price)
        }
    })


@receiver(post_save, sender=Order)
def log_order_change(sender, instance, created, **kwargs):
    """Log order changes"""
    if created:
        event_type = 'ORDER_CREATED'
        message = f"Order created: {instance.order_number}"
    else:
        event_type = 'ORDER_UPDATED'
        message = f"Order updated: {instance.order_number}"
    
    log_event_async.delay({
        'event_type': event_type,
        'message': message,
        'store': instance.store,
        'entity_type': 'Order',
        'entity_id': instance.id,
        'metadata': {
            'order_number': instance.order_number,
            'total': str(instance.total)
        }
    })


@receiver(post_save, sender=Inventory)
def check_low_stock(sender, instance, created, **kwargs):
    """Check for low stock and send notification"""
    if not created:
        # Check if stock is below threshold
        if instance.quantity <= instance.low_stock_threshold:
            # Use the new notify_staff helper
            NotificationService.notify_staff(
                store=instance.store,
                notification_type='inventory.low_stock',
                context={
                    'title': f'Low Stock Alert: {instance.product.title}',
                    'message': f'Stock for {instance.product.title} is low: {instance.quantity} units remaining',
                    'product_id': instance.product.id,
                    'current_stock': instance.quantity,
                    'threshold': instance.low_stock_threshold
                }
            )
