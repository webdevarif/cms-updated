# Ecommerce Improvement Suggestions

## 9. DFCMS Ecommerce Improvements

### 9.1 Current Issues Analysis

#### Data Model Issues
```python
# Current problems in dfcms ecommerce models

# 1. Missing Store Scoping
# Problem: Models don't have explicit store relationships
# Impact: Data isolation issues, multi-tenancy problems

# Current (Problematic):
class Product(models.Model):
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    # Missing store field

# Improved:
class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    # Store-scoped with proper isolation

# 2. Inconsistent Status Management
# Problem: Status fields use different values across models
# Impact: Confusing state management, difficult reporting

# Current (Inconsistent):
ORDER_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
]

PRODUCT_STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
]

# Improved (Consistent):
class StatusChoices:
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'
    DELETED = 'deleted'

# 3. Missing Business Logic Layer
# Problem: Business logic scattered across views and models
# Impact: Difficult to test, maintain, and reuse

# Current (Scattered):
# In views.py
def create_order(request):
    if request.method == 'POST':
        # Business logic mixed with view logic
        order = Order.objects.create(...)
        # Email sending logic here
        # Inventory update logic here
        # Payment processing logic here

# Improved (Centralized):
class OrderService:
    @staticmethod
    def create_order_from_cart(cart, billing_address, shipping_address):
        # Centralized business logic
        order = Order.objects.create(...)
        InventoryService.reserve_inventory(order)
        PaymentService.process_payment(order)
        EmailService.send_confirmation(order)
        return order
```

#### Performance Issues
```python
# Current performance problems

# 1. N+1 Query Problems
# Problem: Related objects fetched with multiple queries
# Impact: Slow page loads, high database load

# Current (Inefficient):
def get_product_list(request):
    products = Product.objects.all()
    result = []
    for product in products:
        # N+1 queries for each product's variants
        variants = product.variants.all()
        # N+1 queries for each product's images
        images = product.images.all()
        result.append({
            'product': product,
            'variants': variants,
            'images': images
        })

# Improved (Optimized):
def get_product_list(request):
    products = Product.objects.select_related('store').prefetch_related(
        'variants',
        'images',
        'categories'
    ).all()
    
    # Single query with all related data
    return products

# 2. Missing Database Indexes
# Problem: No indexes on frequently queried fields
# Impact: Slow query performance

# Current (Unindexed):
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    # No indexes defined

# Improved (Indexed):
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status', 'created_at']),
        ]

# 3. Inefficient Cart Operations
# Problem: Cart recalculates totals on every access
# Impact: Slow cart page loads

# Current (Inefficient):
class Cart(models.Model):
    def get_total(self):
        total = 0
        for item in self.items.all():
            total += item.quantity * item.unit_price
        return total

# Improved (Cached):
class Cart(models.Model):
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def get_total(self):
        return self.total
    
    def recalculate_totals(self):
        self.subtotal = sum(item.get_total() for item in self.items.all())
        self.tax = self.calculate_tax()
        self.shipping = self.calculate_shipping()
        self.total = self.subtotal + self.tax + self.shipping
        self.save()
```

### 9.2 Architecture Improvements

#### Service Layer Implementation
```python
# Proposed service layer architecture

# 1. Product Service
class ProductService:
    """Centralized product business logic"""
    
    @staticmethod
    def create_product(store, user, data):
        """Create product with validation and logging"""
        # Validate data
        ProductService.validate_product_data(data)
        
        # Create product
        product = Product.objects.create(
            store=store,
            title=data['title'],
            slug=ProductService.generate_unique_slug(store, data['title']),
            sku=data['sku'],
            created_by=user
        )
        
        # Create variants
        if 'variants' in data:
            ProductService.create_variants(product, data['variants'])
        
        # Setup inventory
        ProductService.setup_inventory(product)
        
        # Log creation
        log_event_async(
            user=user,
            store=store,
            action='product_created',
            object_type='product',
            object_id=product.id
        )
        
        return product
    
    @staticmethod
    def update_product_inventory(product, variant, quantity_change, reason):
        """Update inventory with audit trail"""
        inventory = Inventory.objects.get_or_create(
            store=product.store,
            product=product,
            variant=variant
        )[0]
        
        old_quantity = inventory.quantity
        inventory.quantity += quantity_change
        inventory.save()
        
        # Create transaction record
        InventoryTransaction.objects.create(
            inventory=inventory,
            type='adjustment',
            quantity=quantity_change,
            notes=reason
        )
        
        # Log change
        log_event_async(
            user=None,
            store=product.store,
            action='inventory_updated',
            object_type='inventory',
            object_id=inventory.id,
            details={
                'old_quantity': old_quantity,
                'new_quantity': inventory.quantity,
                'change': quantity_change,
                'reason': reason
            }
        )

# 2. Order Service
class OrderService:
    """Centralized order business logic"""
    
    @staticmethod
    def process_order_payment(order, payment_method, payment_data):
        """Process payment with fraud detection"""
        # Fraud check
        fraud_analysis = FraudDetectionService.analyze_order(order)
        if fraud_analysis['risk_score'] > 80:
            order.status = 'flagged'
            order.save()
            raise ValidationError("Order flagged for review")
        
        # Process payment
        payment = PaymentService.process_payment(
            order, payment_method, payment_data
        )
        
        # Update order status
        if payment.status == 'completed':
            order.payment_status = 'paid'
            order.status = 'confirmed'
            order.save()
            
            # Send confirmation
            EmailService.send_order_confirmation(order)
            
            # Update customer stats
            order.customer.update_statistics()
        
        return payment

# 3. Cart Service
class CartService:
    """Centralized cart business logic"""
    
    @staticmethod
    def add_item_with_validation(cart, product, variant, quantity):
        """Add item with inventory validation"""
        # Check inventory
        inventory = Inventory.objects.filter(
            store=cart.store,
            product=product,
            variant=variant
        ).first()
        
        if not inventory or inventory.available < quantity:
            raise ValidationError("Insufficient inventory")
        
        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
        
        # Reserve inventory
        inventory.reserve(cart_item.quantity)
        
        # Recalculate cart totals
        cart.recalculate_totals()
        
        return cart_item
```

#### Event-Driven Architecture
```python
# Proposed event system for better decoupling

# 1. Event Definitions
class EcommerceEvents:
    PRODUCT_CREATED = 'product.created'
    PRODUCT_UPDATED = 'product.updated'
    PRODUCT_DELETED = 'product.deleted'
    
    ORDER_CREATED = 'order.created'
    ORDER_CONFIRMED = 'order.confirmed'
    ORDER_SHIPPED = 'order.shipped'
    ORDER_CANCELLED = 'order.cancelled'
    
    PAYMENT_COMPLETED = 'payment.completed'
    PAYMENT_FAILED = 'payment.failed'
    
    INVENTORY_LOW = 'inventory.low'
    INVENTORY_OUT_OF_STOCK = 'inventory.out_of_stock'

# 2. Event Dispatcher
class EventDispatcher:
    @staticmethod
    def dispatch(event_name, data):
        """Dispatch event to all registered handlers"""
        handlers = EventHandler.get_handlers(event_name)
        
        for handler in handlers:
            try:
                handler.handle(data)
            except Exception as e:
                # Log error but don't stop other handlers
                log_error(f"Event handler failed: {e}")

# 3. Event Handlers
class InventoryEventHandler:
    @staticmethod
    def handle_order_created(data):
        """Handle order created event"""
        order = data['order']
        
        # Reserve inventory
        for item in order.items.all():
            inventory = Inventory.objects.filter(
                product=item.product,
                variant=item.variant
            ).first()
            
            if inventory:
                inventory.reserve(item.quantity)
                
                # Check for low stock
                if inventory.available <= 5:
                    EventDispatcher.dispatch(
                        EcommerceEvents.INVENTORY_LOW,
                        {'inventory': inventory}
                    )

class EmailEventHandler:
    @staticmethod
    def handle_order_created(data):
        """Send order confirmation email"""
        order = data['order']
        send_order_confirmation_email.delay(order.id)
    
    @staticmethod
    def handle_inventory_low(data):
        """Send low stock alert"""
        inventory = data['inventory']
        send_low_stock_alert_email.delay(inventory.id)

# 4. Register handlers
EventHandler.register(EcommerceEvents.ORDER_CREATED, InventoryEventHandler)
EventHandler.register(EcommerceEvents.ORDER_CREATED, EmailEventHandler)
EventHandler.register(EcommerceEvents.INVENTORY_LOW, EmailEventHandler)
```

### 9.3 Feature Enhancements

#### Advanced Product Variants
```python
# Current limitations and improvements

# Current (Basic):
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory_quantity = models.IntegerField(default=0)

# Improved (Advanced):
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Inventory
    inventory_quantity = models.IntegerField(default=0)
    inventory_policy = models.CharField(
        max_length=20,
        choices=[
            ('deny', 'Deny'),
            ('continue', 'Continue'),
            ('backorder', 'Backorder')
        ],
        default='deny'
    )
    
    # Physical attributes
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Variant options (structured)
    option1 = models.CharField(max_length=100, blank=True)
    option2 = models.CharField(max_length=100, blank=True)
    option3 = models.CharField(max_length=100, blank=True)
    
    # Position for ordering
    position = models.IntegerField(default=0)
    
    # Metadata
    barcode = models.CharField(max_length=50, blank=True)
    requires_shipping = models.BooleanField(default=True)
    taxable = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['position']
        indexes = [
            models.Index(fields=['product', 'position']),
            models.Index(fields=['sku']),
            models.Index(fields=['inventory_quantity']),
        ]

# Variant Option Management
class VariantOption(models.Model):
    """Structured variant options"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variant_options')
    name = models.CharField(max_length=50)  # e.g., "Size", "Color"
    position = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['product', 'name']
        ordering = ['position']

class VariantOptionValue(models.Model):
    """Values for variant options"""
    option = models.ForeignKey(VariantOption, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100)  # e.g., "Small", "Red"
    position = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['option', 'value']
        ordering = ['position']
```

#### Smart Collections
```python
# Current: Manual collections only
# Improved: Smart collections with rules

class Collection(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ForeignKey('media.MediaFile', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Smart collection settings
    is_smart = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Sorting
    sort_order = models.CharField(
        max_length=20,
        choices=[
            ('manual', 'Manual'),
            ('price_low_high', 'Price: Low to High'),
            ('price_high_low', 'Price: High to Low'),
            ('created_at', 'Created Date'),
            ('title', 'Title'),
            ('best_selling', 'Best Selling')
        ],
        default='manual'
    )
    
    # Metadata
    created_by = models.ForeignKey(GlobalUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['store', 'slug']

class CollectionCondition(models.Model):
    """Rules for smart collections"""
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='conditions')
    
    # Condition definition
    field = models.CharField(
        max_length=50,
        choices=[
            ('title', 'Title'),
            ('type', 'Product Type'),
            ('vendor', 'Vendor'),
            ('price', 'Price'),
            ('compare_at_price', 'Compare at Price'),
            ('inventory', 'Inventory'),
            ('weight', 'Weight'),
            ('tag', 'Tag'),
            ('category', 'Category')
        ]
    )
    
    operator = models.CharField(
        max_length=20,
        choices=[
            ('equals', 'Equals'),
            ('not_equals', 'Does not equal'),
            ('contains', 'Contains'),
            ('not_contains', 'Does not contain'),
            ('starts_with', 'Starts with'),
            ('ends_with', 'Ends with'),
            ('greater_than', 'Greater than'),
            ('less_than', 'Less than'),
            ('between', 'Between'),
            ('in', 'In list'),
            ('not_in', 'Not in list')
        ]
    )
    
    value = models.JSONField()  # Flexible value storage
    position = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['position']

# Smart collection service
class SmartCollectionService:
    @staticmethod
    def get_products_for_collection(collection):
        """Get products matching smart collection rules"""
        if not collection.is_smart:
            return collection.products.all()
        
        queryset = Product.objects.filter(store=collection.store, status='published')
        
        for condition in collection.conditions.all():
            queryset = SmartCollectionService.apply_condition(queryset, condition)
        
        # Apply sorting
        queryset = SmartCollectionService.apply_sorting(queryset, collection.sort_order)
        
        return queryset.distinct()
    
    @staticmethod
    def apply_condition(queryset, condition):
        """Apply single condition to queryset"""
        field = condition.field
        operator = condition.operator
        value = condition.value
        
        if field == 'title':
            if operator == 'contains':
                return queryset.filter(title__icontains=value)
            elif operator == 'equals':
                return queryset.filter(title__iexact=value)
            # ... other operators
        
        elif field == 'price':
            if operator == 'greater_than':
                return queryset.filter(variants__price__gt=value)
            elif operator == 'less_than':
                return queryset.filter(variants__price__lt=value)
            elif operator == 'between':
                return queryset.filter(
                    variants__price__gte=value[0],
                    variants__price__lte=value[1]
                )
        
        elif field == 'category':
            if operator == 'equals':
                return queryset.filter(categories__id=value)
            elif operator == 'in':
                return queryset.filter(categories__id__in=value)
        
        return queryset
```

#### Advanced Discount System
```python
# Current: Basic coupons only
# Improved: Advanced discount engine

class DiscountRule(models.Model):
    """Advanced discount rules"""
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Rule configuration
    rule_type = models.CharField(
        max_length=20,
        choices=[
            ('cart_total', 'Cart Total'),
            ('product_specific', 'Product Specific'),
            ('category_specific', 'Category Specific'),
            ('customer_specific', 'Customer Specific'),
            ('buy_x_get_y', 'Buy X Get Y'),
            ('bundle', 'Bundle Discount')
        ]
    )
    
    # Conditions
    conditions = models.JSONField(default=dict)
    
    # Discount calculation
    discount_type = models.CharField(
        max_length=20,
        choices=[
            ('percentage', 'Percentage'),
            ('fixed_amount', 'Fixed Amount'),
            ('fixed_price', 'Fixed Price'),
            ('free_shipping', 'Free Shipping')
        ]
    )
    
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Limits and restrictions
    usage_limit = models.IntegerField(null=True, blank=True)
    usage_limit_per_customer = models.IntegerField(null=True, blank=True)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Timing
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    
    # Status
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(GlobalUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class DiscountEngine:
    """Advanced discount calculation engine"""
    
    @staticmethod
    def calculate_discounts(cart, customer=None):
        """Calculate all applicable discounts for cart"""
        discounts = []
        total_discount = Decimal('0.00')
        
        # Get applicable rules
        rules = DiscountEngine.get_applicable_rules(cart.store, cart, customer)
        
        for rule in rules:
            discount = DiscountEngine.calculate_rule_discount(rule, cart, customer)
            if discount['amount'] > 0:
                discounts.append(discount)
                total_discount += discount['amount']
        
        return {
            'discounts': discounts,
            'total_discount': total_discount,
            'final_total': cart.get_total() - total_discount
        }
    
    @staticmethod
    def get_applicable_rules(store, cart, customer):
        """Get rules that apply to this cart"""
        rules = DiscountRule.objects.filter(
            store=store,
            is_active=True,
            starts_at__lte=timezone.now(),
            ends_at__gte=timezone.now()
        )
        
        applicable_rules = []
        
        for rule in rules:
            if DiscountEngine.rule_applies(rule, cart, customer):
                applicable_rules.append(rule)
        
        return applicable_rules
    
    @staticmethod
    def rule_applies(rule, cart, customer):
        """Check if rule applies to cart"""
        conditions = rule.conditions
        
        # Check minimum order amount
        if rule.minimum_order_amount > 0:
            if cart.get_subtotal() < rule.minimum_order_amount:
                return False
        
        # Check usage limits
        if rule.usage_limit:
            if rule.used_count >= rule.usage_limit:
                return False
        
        if rule.usage_limit_per_customer and customer:
            customer_usage = Order.objects.filter(
                customer=customer,
                discounts__rule=rule
            ).count()
            if customer_usage >= rule.usage_limit_per_customer:
                return False
        
        # Check specific conditions based on rule type
        if rule.rule_type == 'cart_total':
            return DiscountEngine.check_cart_total_conditions(rule, cart)
        elif rule.rule_type == 'product_specific':
            return DiscountEngine.check_product_conditions(rule, cart)
        elif rule.rule_type == 'customer_specific':
            return DiscountEngine.check_customer_conditions(rule, customer)
        
        return True
    
    @staticmethod
    def calculate_rule_discount(rule, cart, customer):
        """Calculate discount amount for a specific rule"""
        if rule.discount_type == 'percentage':
            discount_amount = cart.get_subtotal() * (rule.discount_value / 100)
        elif rule.discount_type == 'fixed_amount':
            discount_amount = min(rule.discount_value, cart.get_subtotal())
        elif rule.discount_type == 'free_shipping':
            discount_amount = cart.get_shipping()
        else:
            discount_amount = Decimal('0.00')
        
        return {
            'rule_id': rule.id,
            'rule_name': rule.name,
            'discount_type': rule.discount_type,
            'discount_value': rule.discount_value,
            'amount': discount_amount
        }
```

### 9.4 User Experience Improvements

#### Progressive Web App Features
```python
# PWA features for better mobile experience

# 1. Offline Cart Support
class OfflineCartService:
    """Service for offline cart functionality"""
    
    @staticmethod
    def sync_cart_when_online(user, offline_cart_data):
        """Sync offline cart when user comes online"""
        try:
            cart = CartService.get_cart_for_user(user)
            
            for item_data in offline_cart_data['items']:
                # Merge offline items with online cart
                CartService.add_item_with_validation(
                    cart,
                    item_data['product_id'],
                    item_data.get('variant_id'),
                    item_data['quantity']
                )
            
            return {'status': 'synced', 'cart_id': cart.id}
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

# 2. Push Notifications for Order Updates
class PushNotificationService:
    """Push notifications for order status updates"""
    
    @staticmethod
    def send_order_update_notification(order, status):
        """Send push notification for order update"""
        if order.customer.user.push_notification_token:
            message = {
                'title': f'Order {order.order_number} Updated',
                'body': f'Your order status is now: {status}',
                'icon': '/static/icons/order-icon.png',
                'badge': '/static/icons/badge.png',
                'data': {
                    'order_id': order.id,
                    'status': status
                },
                'actions': [
                    {
                        'action': 'view',
                        'title': 'View Order'
                    }
                ]
            }
            
            send_push_notification.delay(
                order.customer.user.push_notification_token,
                message
            )

# 3. One-Click Reorder
class ReorderService:
    """Service for quick reordering"""
    
    @staticmethod
    def create_reorder(order, user):
        """Create new order from existing order"""
        new_order = Order.objects.create(
            store=order.store,
            customer=user.customer,
            billing_address=order.billing_address,
            shipping_address=order.shipping_address,
            status='draft'
        )
        
        # Copy order items
        for item in order.items.all():
            OrderItem.objects.create(
                order=new_order,
                product=item.product,
                variant=item.variant,
                title=item.title,
                sku=item.sku,
                quantity=item.quantity,
                unit_price=item.product.get_current_price(),
                total_price=item.product.get_current_price() * item.quantity
            )
        
        # Recalculate totals
        new_order.calculate_totals()
        new_order.save()
        
        return new_order
```

#### Advanced Search and Filtering
```python
# Enhanced search capabilities

class ProductSearchService:
    """Advanced product search with filters"""
    
    @staticmethod
    def search_products(store, query, filters=None, sort=None):
        """Advanced product search"""
        queryset = Product.objects.filter(
            store=store,
            status='published'
        )
        
        # Text search
        if query:
            queryset = queryset.filter(
                models.Q(title__icontains=query) |
                models.Q(description__icontains=query) |
                models.Q(sku__icontains=query) |
                models.Q(variants__sku__icontains=query) |
                models.Q(tags__contains=query)
            ).distinct()
        
        # Apply filters
        if filters:
            queryset = ProductSearchService.apply_filters(queryset, filters)
        
        # Apply sorting
        if sort:
            queryset = ProductSearchService.apply_sorting(queryset, sort)
        
        return queryset
    
    @staticmethod
    def apply_filters(queryset, filters):
        """Apply search filters"""
        # Category filter
        if 'category' in filters:
            queryset = queryset.filter(categories__slug=filters['category'])
        
        # Price range filter
        if 'price_min' in filters:
            queryset = queryset.filter(variants__price__gte=filters['price_min'])
        if 'price_max' in filters:
            queryset = queryset.filter(variants__price__lte=filters['price_max'])
        
        # In stock filter
        if 'in_stock' in filters and filters['in_stock']:
            queryset = queryset.filter(
                variants__inventory_quantity__gt=0
            )
        
        # Attributes filter
        if 'attributes' in filters:
            for attr, value in filters['attributes'].items():
                queryset = queryset.filter(
                    attributes__contains={attr: value}
                )
        
        return queryset.distinct()
    
    @staticmethod
    def get_search_suggestions(store, query):
        """Get search suggestions for autocomplete"""
        suggestions = []
        
        # Product title suggestions
        title_matches = Product.objects.filter(
            store=store,
            status='published',
            title__icontains=query
        ).values_list('title', flat=True)[:5]
        
        suggestions.extend(title_matches)
        
        # Category suggestions
        category_matches = ProductCategory.objects.filter(
            store=store,
            name__icontains=query
        ).values_list('name', flat=True)[:3]
        
        suggestions.extend(category_matches)
        
        return list(set(suggestions))[:10]
```

### 9.5 Analytics and Reporting

#### Advanced Analytics
```python
# Enhanced analytics and reporting

class EcommerceAnalytics:
    """Advanced ecommerce analytics"""
    
    @staticmethod
    def get_sales_report(store, start_date, end_date):
        """Generate comprehensive sales report"""
        orders = Order.objects.filter(
            store=store,
            created_at__range=[start_date, end_date]
        )
        
        report = {
            'summary': {
                'total_orders': orders.count(),
                'total_revenue': orders.aggregate(
                    total=models.Sum('total')
                )['total'] or Decimal('0.00'),
                'average_order_value': orders.aggregate(
                    avg=models.Avg('total')
                )['avg'] or Decimal('0.00'),
                'conversion_rate': EcommerceAnalytics.calculate_conversion_rate(
                    store, start_date, end_date
                )
            },
            'daily_sales': EcommerceAnalytics.get_daily_sales(orders),
            'top_products': EcommerceAnalytics.get_top_products(orders),
            'customer_analysis': EcommerceAnalytics.get_customer_analysis(orders),
            'revenue_by_category': EcommerceAnalytics.get_revenue_by_category(orders)
        }
        
        return report
    
    @staticmethod
    def get_customer_lifetime_value(store):
        """Calculate customer lifetime value"""
        customers = Customer.objects.filter(
            orders__store=store
        ).distinct()
        
        clv_data = []
        for customer in customers:
            orders = Order.objects.filter(customer=customer, store=store)
            total_spent = orders.aggregate(total=models.Sum('total'))['total'] or 0
            order_count = orders.count()
            first_order = orders.order_by('created_at').first()
            last_order = orders.order_by('-created_at').first()
            
            if first_order and last_order:
                days_active = (last_order.created_at - first_order.created_at).days
                avg_order_value = total_spent / order_count if order_count > 0 else 0
                
                clv_data.append({
                    'customer_id': customer.id,
                    'customer_name': customer.get_full_name(),
                    'total_spent': total_spent,
                    'order_count': order_count,
                    'avg_order_value': avg_order_value,
                    'days_active': days_active,
                    'clv_per_day': total_spent / days_active if days_active > 0 else 0
                })
        
        return sorted(clv_data, key=lambda x: x['total_spent'], reverse=True)
    
    @staticmethod
    def get_inventory_turnover(store):
        """Calculate inventory turnover ratio"""
        inventory = Inventory.objects.filter(store=store)
        
        turnover_data = []
        for item in inventory:
            # Calculate cost of goods sold
            sold_quantity = OrderItem.objects.filter(
                product=item.product,
                variant=item.variant,
                order__created_at__gte=timezone.now() - timedelta(days=365)
            ).aggregate(total=models.Sum('quantity'))['total'] or 0
            
            # Calculate turnover
            avg_inventory = (item.quantity + sold_quantity) / 2
            turnover_rate = sold_quantity / avg_inventory if avg_inventory > 0 else 0
            
            turnover_data.append({
                'product': item.product.title,
                'variant': item.variant.title if item.variant else 'Default',
                'current_inventory': item.quantity,
                'sold_last_year': sold_quantity,
                'turnover_rate': turnover_rate,
                'days_of_supply': 365 / turnover_rate if turnover_rate > 0 else 999
            })
        
        return sorted(turnover_data, key=lambda x: x['turnover_rate'], reverse=True)
```

### 9.6 Performance Optimizations

#### Caching Strategy
```python
# Comprehensive caching strategy

class EcommerceCache:
    """Ecommerce-specific caching"""
    
    CACHE_KEYS = {
        'product_list': 'product_list:{store_id}:{page}',
        'product_detail': 'product_detail:{product_id}',
        'category_tree': 'category_tree:{store_id}',
        'cart_totals': 'cart_totals:{cart_id}',
        'search_results': 'search:{store_id}:{query_hash}'
    }
    
    CACHE_TIMEOUTS = {
        'product_list': 300,  # 5 minutes
        'product_detail': 600,  # 10 minutes
        'category_tree': 3600,  # 1 hour
        'cart_totals': 60,  # 1 minute
        'search_results': 180  # 3 minutes
    }
    
    @staticmethod
    def get_product_list(store_id, page=1):
        """Get cached product list"""
        cache_key = EcommerceCache.CACHE_KEYS['product_list'].format(
            store_id=store_id, page=page
        )
        
        products = cache.get(cache_key)
        
        if not products:
            products = Product.objects.filter(
                store_id=store_id,
                status='published'
            ).select_related('store').prefetch_related(
                'variants', 'images', 'categories'
            )
            
            cache.set(
                cache_key,
                products,
                EcommerceCache.CACHE_TIMEOUTS['product_list']
            )
        
        return products
    
    @staticmethod
    def invalidate_product_cache(product):
        """Invalidate product-related caches"""
        # Invalidate product detail
        cache.delete(
            EcommerceCache.CACHE_KEYS['product_detail'].format(
                product_id=product.id
            )
        )
        
        # Invalidate product list
        for page in range(1, 50):  # Invalidate first 50 pages
            cache.delete(
                EcommerceCache.CACHE_KEYS['product_list'].format(
                    store_id=product.store_id, page=page
                )
            )
        
        # Invalidate category tree
        cache.delete(
            EcommerceCache.CACHE_KEYS['category_tree'].format(
                store_id=product.store_id
            )
        )
```

### 9.7 Security Enhancements

#### Advanced Fraud Detection
```python
# Enhanced fraud detection system

class FraudDetectionEngine:
    """Advanced fraud detection"""
    
    @staticmethod
    def analyze_transaction(order, payment_data):
        """Comprehensive fraud analysis"""
        risk_score = 0
        risk_factors = []
        
        # 1. Order value analysis
        if order.total > 1000:
            risk_score += 15
            risk_factors.append('high_value_order')
        
        # 2. Customer behavior analysis
        customer_risk = FraudDetectionEngine.analyze_customer_behavior(order.customer)
        risk_score += customer_risk['score']
        risk_factors.extend(customer_risk['factors'])
        
        # 3. Geographic analysis
        geo_risk = FraudDetectionEngine.analyze_geographic_risk(
            order.billing_address, order.shipping_address
        )
        risk_score += geo_risk['score']
        risk_factors.extend(geo_risk['factors'])
        
        # 4. Payment method analysis
        payment_risk = FraudDetectionEngine.analyze_payment_method(payment_data)
        risk_score += payment_risk['score']
        risk_factors.extend(payment_risk['factors'])
        
        # 5. Device fingerprinting
        device_risk = FraudDetectionEngine.analyze_device_fingerprint(
            payment_data.get('device_fingerprint')
        )
        risk_score += device_risk['score']
        risk_factors.extend(device_risk['factors'])
        
        return {
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'recommendation': FraudDetectionEngine.get_recommendation(risk_score),
            'requires_review': risk_score > 70
        }
    
    @staticmethod
    def analyze_customer_behavior(customer):
        """Analyze customer behavior patterns"""
        risk_score = 0
        factors = []
        
        # New customer risk
        if customer.order_count == 0:
            risk_score += 20
            factors.append('new_customer')
        
        # Rapid ordering
        recent_orders = Order.objects.filter(
            customer=customer,
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        if recent_orders > 3:
            risk_score += 25
            factors.append('rapid_ordering')
        
        # Unusual order size
        if customer.total_spent > 0:
            avg_order_value = customer.total_spent / customer.order_count
            current_order = Order.objects.filter(customer=customer).last()
            
            if current_order and current_order.total > avg_order_value * 3:
                risk_score += 15
                factors.append('unusual_order_size')
        
        return {'score': risk_score, 'factors': factors}
```

### 9.8 Implementation Priority

#### Phase 1: Critical Issues (Week 1-2)
1. **Add store scoping to all models**
2. **Implement service layer for business logic**
3. **Fix N+1 query problems**
4. **Add database indexes**
5. **Implement proper error handling**

#### Phase 2: Feature Enhancements (Week 3-4)
1. **Advanced product variants**
2. **Smart collections**
3. **Enhanced discount system**
4. **Improved search functionality**
5. **Basic analytics dashboard**

#### Phase 3: Advanced Features (Week 5-6)
1. **Fraud detection system**
2. **Advanced caching**
3. **PWA features**
4. **Comprehensive analytics**
5. **Performance optimizations**

#### Phase 4: Polish and Testing (Week 7-8)
1. **Comprehensive testing**
2. **Documentation**
3. **Performance tuning**
4. **Security audit**
5. **User acceptance testing**
