# Ecommerce Services

## 4. Service Layer

### 4.1 Product Services

#### ProductService
```python
class ProductService:
    """Business logic for product management"""

    @staticmethod
    def create_product(store, user, data):
        """Create new product with variants and categories"""
        product = Product.objects.create(
            store=store,
            title=data['title'],
            slug=data['slug'],
            description=data.get('description', ''),
            short_description=data.get('short_description', ''),
            sku=data['sku'],
            barcode=data.get('barcode', ''),
            track_inventory=data.get('track_inventory', True),
            allow_backorder=data.get('allow_backorder', False),
            requires_shipping=data.get('requires_shipping', True),
            weight=data.get('weight'),
            status=data.get('status', 'draft'),
            featured=data.get('featured', False),
            seo_title=data.get('seo_title', ''),
            seo_description=data.get('seo_description', ''),
            created_by=user
        )

        # Create variants
        if 'variants' in data:
            for variant_data in data['variants']:
                ProductVariant.objects.create(
                    product=product,
                    title=variant_data['title'],
                    sku=variant_data['sku'],
                    barcode=variant_data.get('barcode', ''),
                    price=variant_data['price'],
                    compare_at_price=variant_data.get('compare_at_price'),
                    cost_price=variant_data.get('cost_price'),
                    weight=variant_data.get('weight'),
                    inventory_quantity=variant_data.get('inventory_quantity', 0),
                    inventory_policy=variant_data.get('inventory_policy', 'deny'),
                    requires_shipping=variant_data.get('requires_shipping', True),
                    taxable=variant_data.get('taxable', True),
                    position=variant_data.get('position', 0),
                    option1=variant_data.get('option1', ''),
                    option2=variant_data.get('option2', ''),
                    option3=variant_data.get('option3', '')
                )

        # Add categories
        if 'category_ids' in data:
            product.categories.set(data['category_ids'])

        # Create inventory records
        for variant in product.variants.all():
            Inventory.objects.get_or_create(
                store=store,
                product=product,
                variant=variant,
                defaults={'quantity': variant.inventory_quantity}
            )

        # Log creation
        log_event_async(
            user=user,
            store=store,
            action='product_created',
            object_type='product',
            object_id=product.id,
            details={'title': product.title, 'sku': product.sku}
        )

        return product

    @staticmethod
    def update_product(product, user, data):
        """Update product and related data"""
        old_status = product.status

        # Update product fields
        for field, value in data.items():
            if field not in ['variants', 'category_ids']:
                setattr(product, field, value)

        product.save()

        # Update variants
        if 'variants' in data:
            for variant_data in data['variants']:
                variant_id = variant_data.get('id')
                if variant_id:
                    variant = product.variants.get(id=variant_id)
                    for field, value in variant_data.items():
                        if field != 'id':
                            setattr(variant, field, value)
                    variant.save()
                else:
                    # Create new variant
                    ProductVariant.objects.create(
                        product=product,
                        **variant_data
                    )

        # Update categories
        if 'category_ids' in data:
            product.categories.set(data['category_ids'])

        # Log status change
        if 'status' in data and old_status != data['status']:
            log_event_async(
                user=user,
                store=product.store,
                action='product_status_updated',
                object_type='product',
                object_id=product.id,
                details={
                    'old_status': old_status,
                    'new_status': data['status']
                }
            )

        return product

    @staticmethod
    def duplicate_product(product, user):
        """Duplicate product with variants"""
        new_product = Product.objects.create(
            store=product.store,
            title=f"{product.title} (Copy)",
            slug=f"{product.slug}-copy-{int(time.time())}",
            description=product.description,
            short_description=product.short_description,
            sku=f"{product.sku}-COPY",
            barcode=product.barcode,
            track_inventory=product.track_inventory,
            allow_backorder=product.allow_backorder,
            requires_shipping=product.requires_shipping,
            weight=product.weight,
            status='draft',
            featured=False,
            seo_title=product.seo_title,
            seo_description=product.seo_description,
            created_by=user
        )

        # Duplicate variants
        for variant in product.variants.all():
            ProductVariant.objects.create(
                product=new_product,
                title=variant.title,
                sku=f"{variant.sku}-COPY",
                barcode=variant.barcode,
                price=variant.price,
                compare_at_price=variant.compare_at_price,
                cost_price=variant.cost_price,
                weight=variant.weight,
                inventory_quantity=0,
                inventory_policy=variant.inventory_policy,
                requires_shipping=variant.requires_shipping,
                taxable=variant.taxable,
                position=variant.position,
                option1=variant.option1,
                option2=variant.option2,
                option3=variant.option3
            )

        # Copy categories
        new_product.categories.set(product.categories.all())

        # Log duplication
        log_event_async(
            user=user,
            store=product.store,
            action='product_duplicated',
            object_type='product',
            object_id=new_product.id,
            details={
                'original_product_id': product.id,
                'original_title': product.title
            }
        )

        return new_product

    @staticmethod
    def delete_product(product, user):
        """Soft delete product"""
        product.status = 'deleted'
        product.save()

        # Log deletion
        log_event_async(
            user=user,
            store=product.store,
            action='product_deleted',
            object_type='product',
            object_id=product.id,
            details={'title': product.title}
        )
```

### 4.2 Cart Services

#### CartService
```python
class CartService:
    """Business logic for shopping cart management"""

    @staticmethod
    def get_cart(store, user=None, session_key=None):
        """Get or create cart for user or session"""
        if user and hasattr(user, 'customer'):
            customer = user.customer
            cart, created = Cart.objects.get_or_create(
                store=store,
                customer=customer,
                defaults={'status': 'active'}
            )
        elif session_key:
            cart, created = Cart.objects.get_or_create(
                store=store,
                session_key=session_key,
                defaults={'status': 'active'}
            )
        else:
            cart = None

        return cart

    @staticmethod
    def add_item(cart, product, variant=None, quantity=1):
        """Add item to cart with inventory check"""
        if variant:
            inventory = Inventory.objects.filter(
                store=cart.store,
                product=product,
                variant=variant
            ).first()
        else:
            inventory = Inventory.objects.filter(
                store=cart.store,
                product=product,
                variant__isnull=True
            ).first()

        # Check inventory availability
        if inventory and inventory.available < quantity:
            raise ValidationError(f"Only {inventory.available} items available")

        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={
                'quantity': quantity,
                'unit_price': variant.price if variant else product.variants.first().price
            }
        )

        if not created:
            new_quantity = cart_item.quantity + quantity

            # Check inventory again for additional quantity
            if inventory and inventory.available < new_quantity:
                raise ValidationError(f"Only {inventory.available} items available")

            cart_item.quantity = new_quantity
            cart_item.save()

        # Reserve inventory
        if inventory:
            inventory.reserve(cart_item.quantity)

        return cart_item

    @staticmethod
    def update_item_quantity(cart_item, quantity):
        """Update cart item quantity with inventory check"""
        if quantity <= 0:
            # Remove item and release inventory
            inventory = Inventory.objects.filter(
                store=cart_item.cart.store,
                product=cart_item.product,
                variant=cart_item.variant
            ).first()

            if inventory:
                inventory.release(cart_item.quantity)

            cart_item.delete()
            return True

        # Check inventory availability
        inventory = Inventory.objects.filter(
            store=cart_item.cart.store,
            product=cart_item.product,
            variant=cart_item.variant
        ).first()

        if inventory and inventory.available < quantity:
            raise ValidationError(f"Only {inventory.available} items available")

        # Update quantity and adjust reservation
        if inventory:
            inventory.release(cart_item.quantity)
            inventory.reserve(quantity)

        cart_item.quantity = quantity
        cart_item.save()

        return cart_item

    @staticmethod
    def remove_item(cart_item):
        """Remove item from cart and release inventory"""
        inventory = Inventory.objects.filter(
            store=cart_item.cart.store,
            product=cart_item.product,
            variant=cart_item.variant
        ).first()

        if inventory:
            inventory.release(cart_item.quantity)

        cart_item.delete()

    @staticmethod
    def clear_cart(cart):
        """Clear all items from cart and release inventory"""
        for item in cart.items.all():
            inventory = Inventory.objects.filter(
                store=cart.store,
                product=item.product,
                variant=item.variant
            ).first()

            if inventory:
                inventory.release(item.quantity)

        cart.items.all().delete()

    @staticmethod
    def convert_to_order(cart, billing_address, shipping_address, customer_notes=''):
        """Convert cart to order"""
        if not cart.items.exists():
            raise ValidationError("Cannot create order from empty cart")

        # Create order
        order = Order.objects.create(
            store=cart.store,
            customer=cart.customer,
            cart=cart,
            billing_address=billing_address,
            shipping_address=shipping_address,
            customer_notes=customer_notes,
            currency=cart.currency
        )

        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                title=cart_item.product.title,
                sku=cart_item.variant.sku if cart_item.variant else cart_item.product.sku,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                total_price=cart_item.get_total()
            )

        # Calculate totals
        order.calculate_totals()
        order.save()

        # Reserve inventory for order
        for cart_item in cart.items.all():
            inventory = Inventory.objects.filter(
                store=cart.store,
                product=cart_item.product,
                variant=cart_item.variant
            ).first()

            if inventory:
                inventory.reserve(cart_item.quantity)

        # Update cart status
        cart.status = 'converted'
        cart.save()

        return order
```

### 4.3 Order Services

#### OrderService
```python
class OrderService:
    """Business logic for order management"""

    @staticmethod
    def create_order_from_cart(cart, billing_address, shipping_address, customer_notes=''):
        """Create order from cart"""
        return CartService.convert_to_order(
            cart, billing_address, shipping_address, customer_notes
        )

    @staticmethod
    def update_order_status(order, new_status, user=None):
        """Update order status with validation"""
        old_status = order.status

        # Validate status transition
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['processing', 'cancelled'],
            'processing': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'cancelled'],
            'delivered': [],
            'cancelled': []
        }

        if new_status not in valid_transitions.get(old_status, []):
            raise ValidationError(f"Cannot transition from {old_status} to {new_status}")

        order.status = new_status
        order.save()

        # Handle inventory based on status
        if new_status == 'cancelled':
            OrderService.release_inventory(order)
        elif new_status == 'shipped':
            OrderService.deduct_inventory(order)

        # Log status change
        log_event_async(
            user=user,
            store=order.store,
            action='order_status_updated',
            object_type='order',
            object_id=order.id,
            details={
                'old_status': old_status,
                'new_status': new_status,
                'order_number': order.order_number
            }
        )

        # Send notifications
        if new_status in ['confirmed', 'shipped', 'delivered', 'cancelled']:
            send_order_status_email.delay(order.id, new_status)

        return order

    @staticmethod
    def release_inventory(order):
        """Release reserved inventory for cancelled order"""
        for order_item in order.items.all():
            inventory = Inventory.objects.filter(
                store=order.store,
                product=order_item.product,
                variant=order_item.variant
            ).first()

            if inventory:
                inventory.release(order_item.quantity)

    @staticmethod
    def deduct_inventory(order):
        """Deduct inventory for shipped order"""
        for order_item in order.items.all():
            inventory = Inventory.objects.filter(
                store=order.store,
                product=order_item.product,
                variant=order_item.variant
            ).first()

            if inventory:
                inventory.deduct(order_item.quantity)

    @staticmethod
    def process_payment(order, payment_method, payment_data):
        """Process payment for order"""
        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=order.total
        )

        # Process based on payment method
        if payment_method.type == 'stripe':
            result = process_stripe_payment(payment, payment_data)
        elif payment_method.type == 'paypal':
            result = process_paypal_payment(payment, payment_data)
        elif payment_method.type == 'cash_on_delivery':
            result = {'status': 'pending'}
        else:
            result = {'status': 'failed', 'error': 'Unsupported payment method'}

        payment.status = result.get('status', 'failed')
        payment.transaction_id = result.get('transaction_id', '')
        payment.gateway_response = result
        payment.save()

        # Update order payment status
        if payment.status == 'completed':
            order.payment_status = 'paid'
            order.save()
        elif payment.status == 'failed':
            order.payment_status = 'failed'
            order.save()

        # Log payment
        log_event_async(
            user=None,
            store=order.store,
            action='payment_processed',
            object_type='payment',
            object_id=payment.id,
            details={
                'order_id': order.id,
                'amount': str(payment.amount),
                'status': payment.status,
                'method': payment_method.type
            }
        )

        return payment

    @staticmethod
    def calculate_shipping(order, shipping_method=None):
        """Calculate shipping cost for order"""
        if not shipping_method:
            # Get default shipping method
            shipping_method = ShippingMethod.objects.filter(
                store=order.store,
                is_active=True
            ).first()

        if not shipping_method:
            return Decimal('0.00')

        # Calculate based on shipping method rules
        if shipping_method.type == 'flat_rate':
            return shipping_method.rate
        elif shipping_method.type == 'weight_based':
            total_weight = sum(
                item.variant.weight or 0 for item in order.items.all()
            )
            return total_weight * shipping_method.rate_per_weight
        elif shipping_method.type == 'price_based':
            return order.subtotal * (shipping_method.rate_percentage / 100)

        return Decimal('0.00')

    @staticmethod
    def calculate_tax(order):
        """Calculate tax for order"""
        # Get tax rates for store location
        tax_rates = TaxRate.objects.filter(
            store=order.store,
            is_active=True
        )

        total_tax = Decimal('0.00')

        for tax_rate in tax_rates:
            if tax_rate.applies_to_shipping:
                taxable_amount = order.subtotal + order.shipping
            else:
                taxable_amount = order.subtotal

            tax_amount = taxable_amount * (tax_rate.rate / 100)
            total_tax += tax_amount

        return total_tax
```

### 4.4 Customer Services

#### CustomerService
```python
class CustomerService:
    """Business logic for customer management"""

    @staticmethod
    def create_customer(user, data):
        """Create customer profile for user"""
        customer = Customer.objects.create(
            user=user,
            first_name=data.get('first_name', user.first_name),
            last_name=data.get('last_name', user.last_name),
            email=data.get('email', user.email),
            phone=data.get('phone', ''),
            date_of_birth=data.get('date_of_birth'),
            gender=data.get('gender', ''),
            email_marketing=data.get('email_marketing', True),
            sms_marketing=data.get('sms_marketing', False),
            default_billing_address=data.get('billing_address', {}),
            default_shipping_address=data.get('shipping_address', {})
        )

        # Log customer creation
        log_event_async(
            user=user,
            store=None,  # Global customer
            action='customer_created',
            object_type='customer',
            object_id=customer.id,
            details={'email': customer.email}
        )

        return customer

    @staticmethod
    def update_customer(customer, data):
        """Update customer profile"""
        old_email = customer.email

        for field, value in data.items():
            setattr(customer, field, value)

        customer.save()

        # Log email change
        if 'email' in data and old_email != data['email']:
            log_event_async(
                user=customer.user,
                store=None,
                action='customer_email_updated',
                object_type='customer',
                object_id=customer.id,
                details={'old_email': old_email, 'new_email': customer.email}
            )

        return customer

    @staticmethod
    def merge_customers(target_customer, source_customer):
        """Merge source customer into target customer"""
        # Merge orders
        Order.objects.filter(customer=source_customer).update(customer=target_customer)

        # Merge carts
        Cart.objects.filter(customer=source_customer).update(customer=target_customer)

        # Merge addresses
        if not target_customer.default_billing_address:
            target_customer.default_billing_address = source_customer.default_billing_address

        if not target_customer.default_shipping_address:
            target_customer.default_shipping_address = source_customer.default_shipping_address

        # Update statistics
        target_customer.update_statistics()

        # Log merge
        log_event_async(
            user=target_customer.user,
            store=None,
            action='customers_merged',
            object_type='customer',
            object_id=target_customer.id,
            details={
                'source_customer_id': source_customer.id,
                'source_email': source_customer.email
            }
        )

        # Delete source customer
        source_customer.delete()

        return target_customer

    @staticmethod
    def update_customer_statistics(customer):
        """Update customer order statistics"""
        orders = Order.objects.filter(customer=customer)
        customer.order_count = orders.count()
        customer.total_spent = orders.aggregate(
            total=models.Sum('total')
        )['total'] or 0
        last_order = orders.order_by('-created_at').first()
        customer.last_order_at = last_order.created_at if last_order else None
        customer.save()
```

### 4.5 Collection Services

#### CollectionService
```python
class CollectionService:
    """Business logic for collection management"""

    @staticmethod
    def create_collection(store, user, data):
        """Create new collection"""
        collection = Collection.objects.create(
            store=store,
            title=data['title'],
            slug=data['slug'],
            description=data.get('description', ''),
            is_smart=data.get('is_smart', False),
            is_active=data.get('is_active', True),
            sort_order=data.get('sort_order', 'manual'),
            created_by=user
        )

        # Add image if provided
        if 'image_id' in data:
            collection.image_id = data['image_id']
            collection.save()

        # Add conditions for smart collections
        if collection.is_smart and 'conditions' in data:
            for condition_data in data['conditions']:
                CollectionCondition.objects.create(
                    collection=collection,
                    field=condition_data['field'],
                    operator=condition_data['operator'],
                    value=condition_data['value'],
                    position=condition_data.get('position', 0)
                )

        # Add products for manual collections
        if not collection.is_smart and 'product_ids' in data:
            products = Product.objects.filter(
                id__in=data['product_ids'],
                store=store
            )
            collection.products.add(*products)

        # Log creation
        log_event_async(
            user=user,
            store=store,
            action='collection_created',
            object_type='collection',
            object_id=collection.id,
            details={'title': collection.title, 'is_smart': collection.is_smart}
        )

        return collection

    @staticmethod
    def get_smart_products(collection):
        """Get products for smart collection based on conditions"""
        queryset = Product.objects.filter(store=collection.store, status='published')

        for condition in collection.conditions.all():
            if condition.field == 'title':
                if condition.operator == 'contains':
                    queryset = queryset.filter(title__icontains=condition.value)
                elif condition.operator == 'equals':
                    queryset = queryset.filter(title__iexact=condition.value)
                elif condition.operator == 'starts_with':
                    queryset = queryset.filter(title__istartswith=condition.value)

            elif condition.field == 'price':
                if condition.operator == 'greater_than':
                    queryset = queryset.filter(variants__price__gt=condition.value)
                elif condition.operator == 'less_than':
                    queryset = queryset.filter(variants__price__lt=condition.value)
                elif condition.operator == 'between':
                    queryset = queryset.filter(
                        variants__price__gte=condition.value[0],
                        variants__price__lte=condition.value[1]
                    )

            elif condition.field == 'category':
                queryset = queryset.filter(categories__id=condition.value)

            elif condition.field == 'tag':
                queryset = queryset.filter(tags__contains=condition.value)

        # Apply sorting
        if collection.sort_order == 'price_low_high':
            queryset = queryset.order_by('variants__price')
        elif collection.sort_order == 'price_high_low':
            queryset = queryset.order_by('-variants__price')
        elif collection.sort_order == 'created_at':
            queryset = queryset.order_by('-created_at')
        elif collection.sort_order == 'title':
            queryset = queryset.order_by('title')

        return queryset.distinct()

    @staticmethod
    def update_collection(collection, data):
        """Update collection"""
        old_is_smart = collection.is_smart

        for field, value in data.items():
            if field not in ['conditions', 'product_ids']:
                setattr(collection, field, value)

        collection.save()

        # Update conditions for smart collections
        if collection.is_smart and 'conditions' in data:
            collection.conditions.all().delete()
            for condition_data in data['conditions']:
                CollectionCondition.objects.create(
                    collection=collection,
                    **condition_data
                )

        # Update products for manual collections
        if not collection.is_smart and 'product_ids' in data:
            collection.products.set(data['product_ids'])

        return collection
```

### 4.6 Coupon Services

#### CouponService
```python
class CouponService:
    """Business logic for coupon management"""

    @staticmethod
    def create_coupon(store, user, data):
        """Create new coupon"""
        coupon = Coupon.objects.create(
            store=store,
            campaign_id=data.get('campaign_id'),
            code=data['code'].upper(),
            type=data['type'],
            value=data['value'],
            minimum_order_amount=data.get('minimum_order_amount', 0),
            usage_limit=data.get('usage_limit'),
            usage_limit_per_customer=data.get('usage_limit_per_customer'),
            starts_at=data['starts_at'],
            ends_at=data['ends_at'],
            is_active=data.get('is_active', True),
            created_by=user
        )

        # Log creation
        log_event_async(
            user=user,
            store=store,
            action='coupon_created',
            object_type='coupon',
            object_id=coupon.id,
            details={
                'code': coupon.code,
                'type': coupon.type,
                'value': str(coupon.value)
            }
        )

        return coupon

    @staticmethod
    def validate_coupon(coupon, customer=None, cart_total=0):
        """Validate coupon for use"""
        return coupon.is_valid(customer, cart_total)

    @staticmethod
    def apply_coupon(coupon, order, customer=None):
        """Apply coupon to order"""
        is_valid, message = coupon.is_valid(customer, order.subtotal)

        if not is_valid:
            raise ValidationError(message)

        # Calculate discount
        discount_amount = coupon.apply_discount(order.subtotal)

        # Update order discount
        order.discount = discount_amount
        order.calculate_totals()
        order.save()

        # Add coupon to order
        order.coupons.add(coupon)

        # Increment usage count
        coupon.used_count += 1
        coupon.save()

        # Log coupon usage
        log_event_async(
            user=customer.user if customer else None,
            store=order.store,
            action='coupon_applied',
            object_type='coupon',
            object_id=coupon.id,
            details={
                'code': coupon.code,
                'order_id': order.id,
                'discount_amount': str(discount_amount)
            }
        )

        return discount_amount

    @staticmethod
    def generate_bulk_coupons(store, user, template_data, count):
        """Generate multiple coupons from template"""
        coupons = []
        prefix = template_data.get('prefix', '')
        base_code = template_data['code']

        for i in range(count):
            code = f"{prefix}{base_code}_{i+1}"
            coupon = Coupon.objects.create(
                store=store,
                campaign_id=template_data.get('campaign_id'),
                code=code,
                type=template_data['type'],
                value=template_data['value'],
                minimum_order_amount=template_data.get('minimum_order_amount', 0),
                usage_limit=template_data.get('usage_limit'),
                usage_limit_per_customer=template_data.get('usage_limit_per_customer'),
                starts_at=template_data['starts_at'],
                ends_at=template_data['ends_at'],
                is_active=template_data.get('is_active', True),
                created_by=user
            )
            coupons.append(coupon)

        # Log bulk generation
        log_event_async(
            user=user,
            store=store,
            action='coupons_bulk_generated',
            object_type='coupon',
            details={
                'count': count,
                'base_code': base_code,
                'prefix': prefix
            }
        )

        return coupons
```

### 4.7 Inventory Services

#### InventoryService
```python
class InventoryService:
    """Business logic for inventory management"""

    @staticmethod
    def adjust_inventory(store, product, variant, quantity, transaction_type, user=None, notes=''):
        """Adjust inventory levels"""
        inventory, created = Inventory.objects.get_or_create(
            store=store,
            product=product,
            variant=variant,
            defaults={'quantity': 0}
        )

        old_quantity = inventory.quantity

        if transaction_type == 'add':
            inventory.quantity += quantity
        elif transaction_type == 'subtract':
            inventory.quantity = max(0, inventory.quantity - quantity)
        elif transaction_type == 'set':
            inventory.quantity = quantity
        else:
            raise ValidationError("Invalid transaction type")

        inventory.save()

        # Create transaction record
        InventoryTransaction.objects.create(
            inventory=inventory,
            type=transaction_type,
            quantity=quantity,
            notes=notes,
            created_by=user
        )

        # Log inventory change
        log_event_async(
            user=user,
            store=store,
            action='inventory_adjusted',
            object_type='inventory',
            object_id=inventory.id,
            details={
                'product_title': product.title,
                'variant_title': variant.title if variant else None,
                'old_quantity': old_quantity,
                'new_quantity': inventory.quantity,
                'transaction_type': transaction_type,
                'quantity_change': quantity
            }
        )

        return inventory

    @staticmethod
    def reserve_inventory(order):
        """Reserve inventory for order"""
        for order_item in order.items.all():
            inventory = Inventory.objects.filter(
                store=order.store,
                product=order_item.product,
                variant=order_item.variant
            ).first()

            if inventory:
                if not inventory.reserve(order_item.quantity):
                    raise ValidationError(
                        f"Insufficient inventory for {order_item.product.title}"
                    )

    @staticmethod
    def release_inventory(order):
        """Release reserved inventory for cancelled order"""
        for order_item in order.items.all():
            inventory = Inventory.objects.filter(
                store=order.store,
                product=order_item.product,
                variant=order_item.variant
            ).first()

            if inventory:
                inventory.release(order_item.quantity)

    @staticmethod
    def deduct_inventory(order):
        """Deduct inventory for shipped order"""
        for order_item in order.items.all():
            inventory = Inventory.objects.filter(
                store=order.store,
                product=order_item.product,
                variant=order_item.variant
            ).first()

            if inventory:
                if not inventory.deduct(order_item.quantity):
                    raise ValidationError(
                        f"Insufficient inventory for {order_item.product.title}"
                    )

    @staticmethod
    def get_low_stock_alerts(store, threshold=10):
        """Get products with low inventory"""
        inventories = Inventory.objects.filter(
            store=store,
            available__lte=threshold
        ).select_related('product', 'variant')

        return inventories

    @staticmethod
    def sync_variant_inventory(variant):
        """Sync inventory between variant and inventory records"""
        inventory = Inventory.objects.filter(
            store=variant.product.store,
            product=variant.product,
            variant=variant
        ).first()

        if inventory:
            variant.inventory_quantity = inventory.quantity
            variant.save()
        else:
            # Create inventory record
            Inventory.objects.create(
                store=variant.product.store,
                product=variant.product,
                variant=variant,
                quantity=variant.inventory_quantity
            )
```
