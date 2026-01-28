# Ecommerce AI Guidelines

## 10. AI Development Guidelines

### 10.1 What AI Can Do

#### Code Generation and Refactoring
```python
# ✅ AI CAN generate boilerplate code for:
# - Model definitions with standard fields
# - Serializer classes
# - Basic ViewSet structures
# - Migration files
# - Test templates

# Example: AI can generate this standard model structure
class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['store', 'slug']
        indexes = [
            models.Index(fields=['store', 'status']),
            models.Index(fields=['sku']),
        ]
```

#### Documentation Generation
```python
# ✅ AI CAN generate comprehensive documentation:
# - API endpoint documentation
# - Model field descriptions
# - Service method documentation
# - Code comments and docstrings

# Example: AI can generate this docstring
def calculate_order_totals(order):
    """
    Calculate order totals including subtotal, tax, shipping, and final total.

    Args:
        order (Order): The order instance to calculate totals for

    Returns:
        dict: Dictionary containing calculated totals:
            - subtotal (Decimal): Sum of all order items
            - tax (Decimal): Calculated tax amount
            - shipping (Decimal): Shipping cost
            - total (Decimal): Final total including all charges

    Raises:
        ValidationError: If order items are invalid or missing

    Example:
        >>> order = Order.objects.get(id=1)
        >>> totals = calculate_order_totals(order)
        >>> print(totals['total'])
        Decimal('129.99')
    """
    pass
```

#### Test Case Generation
```python
# ✅ AI CAN generate test cases for:
# - Model validation tests
# - API endpoint tests
# - Service method tests
# - Edge case scenarios

# Example: AI can generate this test structure
class ProductModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name="Test Store")
        self.user = User.objects.create_user(email="test@example.com")

    def test_product_creation_with_valid_data(self):
        """Test creating product with all required fields"""
        product = Product.objects.create(
            store=self.store,
            title="Test Product",
            slug="test-product",
            sku="TEST-001",
            created_by=self.user
        )

        assert product.title == "Test Product"
        assert product.status == "draft"
        assert product.store == self.store

    def test_product_slug_uniqueness_per_store(self):
        """Test that product slugs are unique within each store"""
        # Test implementation
        pass
```

#### Configuration and Setup
```python
# ✅ AI CAN generate configuration files:
# - Django settings
# - URL configurations
# - Admin registrations
# - Celery task definitions

# Example: AI can generate this admin configuration
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'sku', 'status', 'store', 'created_at']
    list_filter = ['status', 'store', 'created_at']
    search_fields = ['title', 'sku', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'sku', 'status')
        }),
        ('Details', {
            'fields': ('description', 'featured_image')
        }),
        ('Metadata', {
            'fields': ('store', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
```

#### Code Optimization Suggestions
```python
# ✅ AI CAN suggest performance optimizations:
# - Query optimization
# - Caching strategies
# - Database indexing
# - Memory usage improvements

# Example: AI can suggest this optimization
# BEFORE (N+1 query problem):
def get_products_with_variants():
    products = Product.objects.all()
    result = []
    for product in products:
        variants = product.variants.all()  # N+1 query
        result.append({'product': product, 'variants': variants})
    return result

# AFTER (Optimized with prefetch_related):
def get_products_with_variants():
    products = Product.objects.prefetch_related('variants').all()
    return [{'product': p, 'variants': list(p.variants.all())} for p in products]
```

### 10.2 What AI Cannot Do

#### Business Logic Implementation
```python
# ❌ AI CANNOT implement complex business logic without explicit requirements:
# - Tax calculation rules (vary by jurisdiction)
# - Shipping rate calculations (complex carrier integrations)
# - Inventory management policies (business-specific rules)
# - Discount validation logic (complex rule combinations)

# Example: AI should NOT implement this without detailed business rules:
def calculate_tax(order):
    # This requires specific tax rules for each jurisdiction
    # AI cannot know the specific tax rates, exemptions, or rules
    # Must be implemented by developer with business requirements
    pass

# ✅ INSTEAD, AI can provide a template:
def calculate_tax(order):
    """
    Calculate tax based on order shipping address and items.

    TODO: Implement specific tax calculation logic based on:
    - Shipping address jurisdiction
    - Product taxability
    - Tax exemptions
    - Tax rates from tax service API
    """
    tax_service = TaxService()
    return tax_service.calculate_tax(order)
```

#### Security Implementation
```python
# ❌ AI CANNOT implement security-critical code:
# - Payment processing (PCI compliance required)
# - Authentication and authorization (security policies)
# - Data encryption (specific algorithms and keys)
# - Fraud detection rules (business-specific thresholds)

# Example: AI should NOT implement payment processing:
def process_payment(order, payment_data):
    # This requires PCI compliance and specific payment gateway integration
    # AI cannot handle secure credential management
    # Must be implemented by security-conscious developer
    pass

# ✅ INSTEAD, AI can provide a secure structure:
def process_payment(order, payment_data):
    """
    Process payment using secure payment gateway.

    SECURITY NOTES:
    - Never store raw card data
    - Use tokenization for payment methods
    - Implement proper error handling
    - Log all payment attempts
    - Validate all input data
    """
    payment_gateway = PaymentGateway()
    return payment_gateway.process_payment(order, payment_data)
```

#### Database Schema Design
```python
# ❌ AI CANNOT design optimal database schema without understanding:
# - Data volume and growth patterns
# - Query performance requirements
# - Specific business relationships
# - Data integrity constraints

# Example: AI should NOT design this without requirements:
class Order(models.Model):
    # AI might suggest this structure, but it may not be optimal
    # for specific business needs, performance, or data volume
    customer_data = models.JSONField()  # Might be better normalized
    items = models.JSONField()  # Should be separate model for querying
    pass

# ✅ INSTEAD, AI can suggest normalized structure:
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    # Separate OrderItem model for better querying and indexing
    pass

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
```

#### Integration with External Services
```python
# ❌ AI CANNOT implement external service integrations without:
# - API credentials and authentication
# - Specific endpoint URLs and parameters
# - Error handling requirements
# - Rate limiting and retry logic

# Example: AI should NOT implement this without API docs:
def sync_with_shipping_carrier(order):
    # This requires specific carrier API integration
    # AI cannot know API endpoints, authentication, or data formats
    pass

# ✅ INSTEAD, AI can provide integration template:
def sync_with_shipping_carrier(order):
    """
    Sync order with shipping carrier API.

    TODO: Implement specific carrier integration:
    - Add API endpoint configuration
    - Implement authentication
    - Add error handling and retry logic
    - Handle rate limiting
    - Map data fields correctly
    """
    carrier_api = ShippingCarrierAPI()
    return carrier_api.create_shipment(order)
```

### 10.3 AI Development Workflow

#### Step 1: Requirements Analysis
```python
# ✅ AI CAN help analyze requirements and suggest structure:

# Developer provides: "I need a product model with variants and inventory"
# AI suggests:
class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    track_inventory = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory_quantity = models.IntegerField(default=0)
    # ... other fields

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=0)
    reserved = models.IntegerField(default=0)
    available = models.IntegerField(default=0)
```

#### Step 2: Code Generation
```python
# ✅ AI CAN generate initial code implementation:

# Developer: "Generate serializers for these models"
# AI generates:
class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    inventory_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'sku', 'description', 'status',
            'variants', 'inventory_count', 'created_at'
        ]

    def get_inventory_count(self, obj):
        return sum(variant.inventory_quantity for variant in obj.variants.all())

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'title', 'sku', 'price', 'inventory_quantity']
```

#### Step 3: Review and Refine
```python
# ✅ AI CAN suggest improvements after review:

# Developer: "This serializer is slow, optimize it"
# AI suggests optimization:
class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    inventory_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'sku', 'description', 'status',
            'variants', 'inventory_count', 'created_at'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optimize query with prefetch_related
        if self.instance:
            self.instance = Product.objects.prefetch_related('variants').get(
                id=self.instance.id
            )

    def get_inventory_count(self, obj):
        # Use annotated field for better performance
        return getattr(obj, '_inventory_count', 0)
```

### 10.4 Best Practices for AI-Assisted Development

#### Code Quality Standards
```python
# ✅ AI-generated code should follow these standards:

# 1. Use descriptive variable names
# ❌ BAD:
def calc(o):
    t = sum(i.q * i.p for i in o.items)
    return t

# ✅ GOOD:
def calculate_order_subtotal(order):
    subtotal = sum(item.quantity * item.unit_price for item in order.items.all())
    return subtotal

# 2. Include proper error handling
# ❌ BAD:
def process_order(order):
    order.save()
    send_email(order.customer.email)

# ✅ GOOD:
def process_order(order):
    try:
        order.save()
        send_order_confirmation_email.delay(order.id)
    except ValidationError as e:
        logger.error(f"Order validation failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing order: {e}")
        order.status = 'error'
        order.save()
        raise

# 3. Add comprehensive docstrings
def reserve_inventory(variant, quantity):
    """
    Reserve inventory for a product variant.

    Args:
        variant (ProductVariant): The product variant to reserve inventory for
        quantity (int): The quantity to reserve

    Returns:
        bool: True if reservation successful, False otherwise

    Raises:
        ValidationError: If quantity is invalid or insufficient inventory

    Example:
        >>> variant = ProductVariant.objects.get(sku="SHIRT-RED-M")
        >>> success = reserve_inventory(variant, 2)
        >>> print(success)
        True
    """
    if quantity <= 0:
        raise ValidationError("Quantity must be positive")

    inventory = Inventory.objects.filter(variant=variant).first()
    if not inventory or inventory.available < quantity:
        return False

    inventory.reserved += quantity
    inventory.save()
    return True
```

#### Security Guidelines
```python
# ✅ AI should always generate secure code:

# 1. Validate all inputs
def create_product_from_api(request_data):
    # Validate required fields
    required_fields = ['title', 'sku', 'price']
    for field in required_fields:
        if field not in request_data:
            raise ValidationError(f"Missing required field: {field}")

    # Sanitize input
    title = bleach.clean(request_data['title'], tags=[], strip=True)
    sku = re.sub(r'[^A-Za-z0-9_-]', '', request_data['sku'])

    # Validate data types
    try:
        price = Decimal(str(request_data['price']))
    except (ValueError, TypeError):
        raise ValidationError("Invalid price format")

# 2. Use parameterized queries (Django ORM handles this)
# ❌ BAD (SQL injection risk):
# Product.objects.raw(f"SELECT * FROM product WHERE title LIKE '%{user_input}%'")

# ✅ GOOD (Django ORM protects against injection):
Product.objects.filter(title__icontains=user_input)

# 3. Never log sensitive data
def log_payment_attempt(payment_data):
    # ❌ BAD: Logs sensitive card data
    logger.info(f"Payment attempt: {payment_data}")

    # ✅ GOOD: Only logs non-sensitive data
    logger.info(f"Payment attempt: {payment_data['order_id']}, amount: {payment_data['amount']}")
```

#### Performance Guidelines
```python
# ✅ AI should generate performant code:

# 1. Use select_related and prefetch_related
def get_orders_with_customers():
    # ❌ BAD: N+1 queries
    orders = Order.objects.all()
    for order in orders:
        print(order.customer.email)  # Separate query for each order

    # ✅ GOOD: Single query with related data
    orders = Order.objects.select_related('customer').all()
    for order in orders:
        print(order.customer.email)

# 2. Use database indexes
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['customer', 'status']),  # For customer order queries
            models.Index(fields=['status', 'created_at']),  # For status-based queries
        ]

# 3. Use bulk operations for large datasets
def update_product_prices(price_updates):
    # ❌ BAD: Individual updates
    for product_id, new_price in price_updates.items():
        product = Product.objects.get(id=product_id)
        product.price = new_price
        product.save()

    # ✅ GOOD: Bulk update
    Product.objects.filter(id__in=price_updates.keys()).update(
        price=Case(*[When(id=pk, then=Value(price)) for pk, price in price_updates.items()])
    )
```

### 10.5 Code Review Checklist

#### Before Committing AI-Generated Code
```python
# ✅ Review checklist for AI-generated code:

# 1. [ ] Business Logic Verification
#    - Does the code implement correct business rules?
#    - Are edge cases handled properly?
#    - Is the logic consistent with requirements?

# 2. [ ] Security Review
#    - Are all inputs validated?
#    - Is sensitive data handled properly?
#    - Are there any injection vulnerabilities?

# 3. [ ] Performance Review
#    - Are database queries optimized?
#    - Are indexes properly used?
#    - Is caching implemented where needed?

# 4. [ ] Testing Coverage
#    - Are there tests for all methods?
#    - Are edge cases tested?
#    - Are integration tests included?

# 5. [ ] Documentation
#    - Are docstrings complete?
#    - Are complex algorithms explained?
#    - Are API endpoints documented?

# Example review process:
def review_ai_generated_code(code):
    """
    Review AI-generated code before committing.

    Args:
        code (str): The AI-generated code to review

    Returns:
        dict: Review results with issues and recommendations
    """
    issues = []

    # Check for security issues
    if 'eval(' in code or 'exec(' in code:
        issues.append("Potentially unsafe code execution detected")

    # Check for missing input validation
    if 'request.data' in code and 'validate' not in code:
        issues.append("Missing input validation")

    # Check for N+1 queries
    if '.objects.all()' in code and 'select_related' not in code:
        issues.append("Potential N+1 query problem")

    return {
        'issues': issues,
        'approved': len(issues) == 0
    }
```

### 10.6 Continuous Improvement

#### Learning from AI Mistakes
```python
# ✅ Document and learn from AI errors:

# Example: AI generated incorrect tax calculation
def calculate_tax_v1(order):
    # AI initially generated this (incorrect):
    return order.subtotal * 0.08  # Hardcoded tax rate

# Corrected version with proper business logic:
def calculate_tax_v2(order):
    """
    Calculate tax based on shipping address and product taxability.

    The AI initially suggested a hardcoded tax rate, but business requirements
    showed that tax rates vary by jurisdiction and product type.
    """
    tax_calculator = TaxCalculator()
    return tax_calculator.calculate_tax(order)

# Lesson learned: Always verify business logic assumptions with stakeholders
```

#### Feedback Loop
```python
# ✅ Create feedback mechanism for AI improvements:

class AICodeFeedback:
    """Track and learn from AI code generation feedback"""

    def __init__(self):
        self.feedback_log = []

    def log_feedback(self, prompt, generated_code, issues, corrections):
        """Log feedback for AI improvement"""
        feedback_entry = {
            'timestamp': timezone.now(),
            'prompt': prompt,
            'generated_code': generated_code,
            'issues': issues,
            'corrections': corrections,
            'lesson_learned': self.extract_lesson(issues, corrections)
        }

        self.feedback_log.append(feedback_entry)

    def extract_lesson(self, issues, corrections):
        """Extract learning points from feedback"""
        lessons = []

        for issue in issues:
            if 'security' in issue.lower():
                lessons.append("Always prioritize security in generated code")
            elif 'performance' in issue.lower():
                lessons.append("Consider database optimization in generated code")
            elif 'validation' in issue.lower():
                lessons.append("Include proper input validation")

        return lessons

    def generate_improvement_summary(self):
        """Generate summary of improvements needed"""
        issue_counts = {}
        for entry in self.feedback_log:
            for issue in entry['issues']:
                issue_type = issue.split(':')[0]
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

        return {
            'total_feedback': len(self.feedback_log),
            'common_issues': issue_counts,
            'improvement_areas': sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        }
```

### 10.7 Final Guidelines

#### Golden Rules for AI-Assisted Ecommerce Development
```python
# 1. ✅ ALWAYS verify business logic with stakeholders
# 2. ✅ ALWAYS prioritize security over convenience
# 3. ✅ ALWAYS test AI-generated code thoroughly
# 4. ✅ NEVER trust AI with sensitive data handling
# 5. ✅ NEVER deploy AI code without human review
# 6. ✅ ALWAYS document assumptions and limitations
# 7. ✅ ALWAYS consider performance implications
# 8. ✅ ALWAYS maintain code quality standards
# 9. ✅ NEVER use AI for critical security implementations
# 10. ✅ ALWAYS learn from AI mistakes and improve prompts

# Example of responsible AI usage:
def responsible_ai_usage_example():
    """
    Example of using AI responsibly for ecommerce development.

    Process:
    1. Use AI to generate boilerplate code and templates
    2. Review and understand all generated code
    3. Implement business logic manually based on requirements
    4. Add security measures and input validation
    5. Write comprehensive tests
    6. Document assumptions and limitations
    7. Get code review from team members
    8. Test thoroughly before deployment
    """
    pass
```
