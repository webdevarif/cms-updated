# Ecommerce Migration

## 8. Migration Strategy

### 8.1 Legacy Data Analysis

#### Current DFCMS Ecommerce Structure
```python
# Legacy models in dfcms/backend/modules/ecommerce/models.py

# 1. Product Models
- Product (basic fields)
- ProductVariant (limited fields)
- ProductCategory (hierarchical)
- ProductImage (media integration)

# 2. Order Models  
- Order (basic order tracking)
- OrderItem (order line items)
- OrderStatus (status tracking)

# 3. Cart Models
- Cart (session/customer based)
- CartItem (cart line items)

# 4. Customer Models
- Customer (linked to User)
- CustomerAddress (address management)

# 5. Discount Models
- Discount (simple discounts)
- Coupon (coupon codes)

# 6. Inventory Models
- Inventory (basic tracking)
- InventoryTransaction (movement tracking)
```

#### Migration Complexity Assessment
```python
# Migration complexity matrix
MIGRATION_COMPLEXITY = {
    'products': {
        'data_volume': 'high',
        'relationship_complexity': 'medium',
        'business_logic_changes': 'high',
        'estimated_effort': '3-4 days'
    },
    'orders': {
        'data_volume': 'high',
        'relationship_complexity': 'high',
        'business_logic_changes': 'medium',
        'estimated_effort': '4-5 days'
    },
    'customers': {
        'data_volume': 'medium',
        'relationship_complexity': 'low',
        'business_logic_changes': 'low',
        'estimated_effort': '1-2 days'
    },
    'cart': {
        'data_volume': 'low',
        'relationship_complexity': 'low',
        'business_logic_changes': 'medium',
        'estimated_effort': '1 day'
    },
    'discounts': {
        'data_volume': 'low',
        'relationship_complexity': 'medium',
        'business_logic_changes': 'high',
        'estimated_effort': '2-3 days'
    },
    'inventory': {
        'data_volume': 'medium',
        'relationship_complexity': 'medium',
        'business_logic_changes': 'medium',
        'estimated_effort': '2-3 days'
    }
}
```

### 8.2 Migration Phases

#### Phase 1: Infrastructure Setup
```python
# Phase 1: Create new V2 structure
# Duration: 1-2 days

# 1. Create new models structure
# 2. Set up store scoping
# 3. Create migration framework
# 4. Set up data validation

class MigrationPhase1:
    """Phase 1: Infrastructure and model creation"""
    
    def create_new_models(self):
        """Create new V2 models with store scoping"""
        # Create Product model with store FK
        # Create ProductVariant with enhanced fields
        # Create Order model with new fields
        # Create Customer model linked to GlobalUser
        # Create new inventory system
        pass
    
    def setup_store_scoping(self):
        """Add store FK to all models"""
        # Add store field to all models
        # Create indexes for store-based queries
        # Set up store isolation
        pass
    
    def create_migration_utilities(self):
        """Create migration helper functions"""
        # Data validation utilities
        # Data transformation utilities
        # Progress tracking utilities
        pass
```

#### Phase 2: Data Migration
```python
# Phase 2: Migrate core data
# Duration: 5-7 days

class MigrationPhase2:
    """Phase 2: Core data migration"""
    
    def migrate_products(self):
        """Migrate products and variants"""
        # 1. Map legacy products to new structure
        # 2. Create store associations
        # 3. Migrate product categories
        # 4. Migrate product images
        # 5. Set up inventory records
        
        legacy_products = LegacyProduct.objects.all()
        
        for legacy_product in legacy_products:
            # Determine store (default to first store or create mapping)
            store = self.get_store_for_legacy_product(legacy_product)
            
            # Create new product
            new_product = Product.objects.create(
                store=store,
                title=legacy_product.name,
                slug=self.generate_slug(legacy_product.name),
                sku=legacy_product.sku or self.generate_sku(legacy_product),
                description=legacy_product.description or '',
                status=self.map_status(legacy_product.status),
                created_by=self.get_created_by(legacy_product),
                created_at=legacy_product.created_at,
                updated_at=legacy_product.updated_at
            )
            
            # Migrate variants
            self.migrate_variants(legacy_product, new_product)
            
            # Migrate categories
            self.migrate_product_categories(legacy_product, new_product)
            
            # Migrate images
            self.migrate_product_images(legacy_product, new_product)
    
    def migrate_variants(self, legacy_product, new_product):
        """Migrate product variants"""
        for legacy_variant in legacy_product.variants.all():
            ProductVariant.objects.create(
                product=new_product,
                title=legacy_variant.name or 'Default',
                sku=legacy_variant.sku or f"{new_product.sku}-VAR",
                price=legacy_variant.price or Decimal('0.00'),
                compare_at_price=legacy_variant.compare_price,
                cost_price=legacy_variant.cost_price,
                weight=legacy_variant.weight,
                inventory_quantity=legacy_variant.stock or 0,
                inventory_policy='deny' if legacy_variant.track_stock else 'ignore',
                option1=legacy_variant.option1,
                option2=legacy_variant.option2,
                option3=legacy_variant.option3
            )
    
    def migrate_orders(self):
        """Migrate orders and order items"""
        legacy_orders = LegacyOrder.objects.all()
        
        for legacy_order in legacy_orders:
            # Get or create customer
            customer = self.get_or_create_customer(legacy_order)
            
            # Determine store
            store = self.get_store_for_legacy_order(legacy_order)
            
            # Create new order
            new_order = Order.objects.create(
                store=store,
                customer=customer,
                order_number=legacy_order.order_number or self.generate_order_number(),
                status=self.map_order_status(legacy_order.status),
                payment_status=self.map_payment_status(legacy_order.payment_status),
                fulfillment_status=self.map_fulfillment_status(legacy_order.fulfillment_status),
                currency=legacy_order.currency or 'USD',
                subtotal=legacy_order.subtotal or Decimal('0.00'),
                tax=legacy_order.tax or Decimal('0.00'),
                shipping=legacy_order.shipping or Decimal('0.00'),
                discount=legacy_order.discount or Decimal('0.00'),
                total=legacy_order.total or Decimal('0.00'),
                billing_address=self.migrate_address(legacy_order.billing_address),
                shipping_address=self.migrate_address(legacy_order.shipping_address),
                notes=legacy_order.notes,
                created_at=legacy_order.created_at,
                updated_at=legacy_order.updated_at
            )
            
            # Migrate order items
            self.migrate_order_items(legacy_order, new_order)
    
    def migrate_customers(self):
        """Migrate customer data"""
        legacy_customers = LegacyCustomer.objects.all()
        
        for legacy_customer in legacy_customers:
            # Get or create GlobalUser
            user = self.get_or_create_user(legacy_customer)
            
            # Create new customer
            customer = Customer.objects.create(
                user=user,
                first_name=legacy_customer.first_name,
                last_name=legacy_customer.last_name,
                email=legacy_customer.email,
                phone=legacy_customer.phone,
                date_of_birth=legacy_customer.date_of_birth,
                gender=legacy_customer.gender,
                email_marketing=legacy_customer.email_marketing,
                sms_marketing=legacy_customer.sms_marketing,
                total_spent=legacy_customer.total_spent or Decimal('0.00'),
                order_count=legacy_customer.order_count or 0,
                last_order_at=legacy_customer.last_order_at,
                default_billing_address=self.migrate_address(legacy_customer.billing_address),
                default_shipping_address=self.migrate_address(legacy_customer.shipping_address),
                created_at=legacy_customer.created_at,
                updated_at=legacy_customer.updated_at
            )
```

#### Phase 3: Data Validation and Cleanup
```python
# Phase 3: Validation and cleanup
# Duration: 2-3 days

class MigrationPhase3:
    """Phase 3: Data validation and cleanup"""
    
    def validate_data_integrity(self):
        """Validate migrated data integrity"""
        validation_errors = []
        
        # Validate products
        for product in Product.objects.all():
            if not product.store:
                validation_errors.append(f"Product {product.id} missing store")
            
            if not product.variants.exists():
                validation_errors.append(f"Product {product.id} has no variants")
            
            if not product.slug:
                validation_errors.append(f"Product {product.id} missing slug")
        
        # Validate orders
        for order in Order.objects.all():
            if not order.customer:
                validation_errors.append(f"Order {order.id} missing customer")
            
            if not order.store:
                validation_errors.append(f"Order {order.id} missing store")
            
            if not order.items.exists():
                validation_errors.append(f"Order {order.id} has no items")
        
        return validation_errors
    
    def cleanup_legacy_data(self):
        """Clean up legacy data after successful migration"""
        # Archive legacy tables
        # Create backup
        # Remove unused fields
        pass
    
    def update_references(self):
        """Update system references to new models"""
        # Update foreign key references
        # Update API endpoints
        # Update admin configurations
        pass
```

### 8.3 Data Mapping Functions

#### Status Mapping
```python
class StatusMapper:
    """Map legacy status values to new system"""
    
    PRODUCT_STATUS_MAP = {
        'active': 'published',
        'inactive': 'draft',
        'draft': 'draft',
        'published': 'published',
        'archived': 'archived',
        'deleted': 'deleted'
    }
    
    ORDER_STATUS_MAP = {
        'pending': 'pending',
        'processing': 'processing',
        'shipped': 'shipped',
        'delivered': 'delivered',
        'cancelled': 'cancelled',
        'refunded': 'refunded'
    }
    
    PAYMENT_STATUS_MAP = {
        'pending': 'pending',
        'paid': 'paid',
        'failed': 'failed',
        'refunded': 'refunded',
        'partially_refunded': 'partially_refunded'
    }
    
    FULFILLMENT_STATUS_MAP = {
        'unfulfilled': 'unfulfilled',
        'partial': 'partial',
        'fulfilled': 'fulfilled',
        'restocked': 'restocked'
    }
    
    @classmethod
    def map_product_status(cls, legacy_status):
        """Map legacy product status"""
        return cls.PRODUCT_STATUS_MAP.get(legacy_status, 'draft')
    
    @classmethod
    def map_order_status(cls, legacy_status):
        """Map legacy order status"""
        return cls.ORDER_STATUS_MAP.get(legacy_status, 'pending')
    
    @classmethod
    def map_payment_status(cls, legacy_status):
        """Map legacy payment status"""
        return cls.PAYMENT_STATUS_MAP.get(legacy_status, 'pending')
    
    @classmethod
    def map_fulfillment_status(cls, legacy_status):
        """Map legacy fulfillment status"""
        return cls.FULFILLMENT_STATUS_MAP.get(legacy_status, 'unfulfilled')
```

#### Address Migration
```python
class AddressMapper:
    """Migrate address data"""
    
    @staticmethod
    def migrate_address(legacy_address):
        """Migrate legacy address to new format"""
        if not legacy_address:
            return {}
        
        return {
            'first_name': legacy_address.first_name,
            'last_name': legacy_address.last_name,
            'company': legacy_address.company,
            'street': legacy_address.address1,
            'street2': legacy_address.address2,
            'city': legacy_address.city,
            'state': legacy_address.state,
            'country': legacy_address.country,
            'postal_code': legacy_address.postal_code,
            'phone': legacy_address.phone
        }
```

### 8.4 Migration Commands

#### Management Command
```python
# ecommerce/management/commands/migrate_ecommerce.py
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from progress.bar import Bar

class Command(BaseCommand):
    help = 'Migrate ecommerce data from legacy system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--phase',
            type=int,
            choices=[1, 2, 3],
            help='Migration phase to run'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run migration without making changes'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Batch size for data processing'
        )
    
    def handle(self, *args, **options):
        phase = options.get('phase')
        dry_run = options.get('dry_run', False)
        batch_size = options.get('batch_size', 1000)
        
        if phase == 1:
            self.run_phase_1(dry_run)
        elif phase == 2:
            self.run_phase_2(dry_run, batch_size)
        elif phase == 3:
            self.run_phase_3(dry_run)
        else:
            self.run_full_migration(dry_run, batch_size)
    
    def run_phase_1(self, dry_run):
        """Run phase 1: Infrastructure setup"""
        self.stdout.write("Starting Phase 1: Infrastructure setup")
        
        if dry_run:
            self.stdout.write("DRY RUN: No changes will be made")
        
        # Create new models
        # Set up store scoping
        # Create migration utilities
        
        self.stdout.write(self.style.SUCCESS("Phase 1 completed"))
    
    def run_phase_2(self, dry_run, batch_size):
        """Run phase 2: Data migration"""
        self.stdout.write("Starting Phase 2: Data migration")
        
        if dry_run:
            self.stdout.write("DRY RUN: No changes will be made")
        
        # Migrate products
        self.migrate_products(dry_run, batch_size)
        
        # Migrate customers
        self.migrate_customers(dry_run, batch_size)
        
        # Migrate orders
        self.migrate_orders(dry_run, batch_size)
        
        # Migrate inventory
        self.migrate_inventory(dry_run, batch_size)
        
        self.stdout.write(self.style.SUCCESS("Phase 2 completed"))
    
    def run_phase_3(self, dry_run):
        """Run phase 3: Validation and cleanup"""
        self.stdout.write("Starting Phase 3: Validation and cleanup")
        
        if dry_run:
            self.stdout.write("DRY RUN: No changes will be made")
        
        # Validate data integrity
        errors = self.validate_migration()
        
        if errors:
            self.stdout.write(self.style.ERROR("Validation errors found:"))
            for error in errors:
                self.stdout.write(f"  - {error}")
        else:
            self.stdout.write(self.style.SUCCESS("No validation errors found"))
        
        if not dry_run and not errors:
            # Cleanup legacy data
            self.cleanup_legacy_data()
            
            # Update references
            self.update_references()
        
        self.stdout.write(self.style.SUCCESS("Phase 3 completed"))
    
    def migrate_products(self, dry_run, batch_size):
        """Migrate products in batches"""
        from ecommerce.migration import ProductMigrator
        
        migrator = ProductMigrator(dry_run=dry_run)
        
        legacy_products = LegacyProduct.objects.all()
        total = legacy_products.count()
        
        bar = Bar('Migrating products', max=total)
        
        for i in range(0, total, batch_size):
            batch = legacy_products[i:i + batch_size]
            migrator.migrate_batch(batch)
            bar.next(len(batch))
        
        bar.finish()
```

### 8.5 Rollback Strategy

#### Rollback Planning
```python
class MigrationRollback:
    """Rollback strategy for failed migration"""
    
    def __init__(self):
        self.backup_created = False
        self.rollback_points = []
    
    def create_backup(self):
        """Create full database backup before migration"""
        # 1. Backup legacy tables
        # 2. Create migration checkpoint
        # 3. Document current state
        
        self.backup_created = True
        return True
    
    def create_rollback_point(self, phase, description):
        """Create rollback point for each phase"""
        rollback_point = {
            'phase': phase,
            'description': description,
            'timestamp': timezone.now(),
            'tables_backed_up': [],
            'data_counts': {}
        }
        
        self.rollback_points.append(rollback_point)
        return rollback_point
    
    def rollback_to_phase(self, target_phase):
        """Rollback to specific phase"""
        if not self.backup_created:
            raise Exception("No backup available for rollback")
        
        # Find rollback point
        rollback_point = None
        for point in reversed(self.rollback_points):
            if point['phase'] <= target_phase:
                rollback_point = point
                break
        
        if not rollback_point:
            raise Exception(f"No rollback point found for phase {target_phase}")
        
        # Execute rollback
        self.execute_rollback(rollback_point)
        
        return True
    
    def execute_rollback(self, rollback_point):
        """Execute rollback to specific point"""
        # 1. Drop new tables
        # 2. Restore legacy tables
        # 3. Restore data counts
        # 4. Verify integrity
        
        pass
```

### 8.6 Testing Migration

#### Migration Test Suite
```python
# tests/test_migration.py
import pytest
from django.test import TestCase
from django.core.management import call_command
from ecommerce.migration import MigrationPhase1, MigrationPhase2, MigrationPhase3
from ecommerce.models import Product, Order, Customer

class MigrationTest(TestCase):
    def setUp(self):
        """Set up test legacy data"""
        self.create_legacy_data()
    
    def create_legacy_data(self):
        """Create test legacy data"""
        # Create legacy products
        # Create legacy customers
        # Create legacy orders
        pass
    
    def test_phase_1_migration(self):
        """Test phase 1 migration"""
        migrator = MigrationPhase1()
        migrator.create_new_models()
        migrator.setup_store_scoping()
        
        # Verify models were created
        assert Product.objects.count() == 0  # Should be empty initially
        assert Order.objects.count() == 0
        assert Customer.objects.count() == 0
    
    def test_phase_2_migration(self):
        """Test phase 2 data migration"""
        # Run phase 1 first
        phase1 = MigrationPhase1()
        phase1.create_new_models()
        phase1.setup_store_scoping()
        
        # Run phase 2
        phase2 = MigrationPhase2()
        phase2.migrate_products()
        phase2.migrate_customers()
        phase2.migrate_orders()
        
        # Verify data was migrated
        assert Product.objects.count() > 0
        assert Customer.objects.count() > 0
        assert Order.objects.count() > 0
    
    def test_data_integrity(self):
        """Test migrated data integrity"""
        # Run full migration
        self.run_full_migration()
        
        # Test product integrity
        for product in Product.objects.all():
            assert product.store is not None
            assert product.slug is not None
            assert product.variants.exists()
        
        # Test order integrity
        for order in Order.objects.all():
            assert order.customer is not None
            assert order.store is not None
            assert order.items.exists()
    
    def test_migration_command(self):
        """Test migration management command"""
        # Test dry run
        call_command('migrate_ecommerce', '--phase=1', '--dry-run')
        
        # Test actual migration
        call_command('migrate_ecommerce', '--phase=1')
        
        # Verify phase 1 completion
        assert Product.objects.count() == 0  # Models created but no data yet
    
    def run_full_migration(self):
        """Run complete migration for testing"""
        phase1 = MigrationPhase1()
        phase1.create_new_models()
        phase1.setup_store_scoping()
        
        phase2 = MigrationPhase2()
        phase2.migrate_products()
        phase2.migrate_customers()
        phase2.migrate_orders()
        
        phase3 = MigrationPhase3()
        errors = phase3.validate_data_integrity()
        
        assert len(errors) == 0, f"Migration validation errors: {errors}"
```

### 8.7 Performance Considerations

#### Large Dataset Handling
```python
class PerformanceOptimizedMigration:
    """Optimized migration for large datasets"""
    
    def __init__(self, batch_size=1000):
        self.batch_size = batch_size
        self.memory_limit = 1024 * 1024 * 1024  # 1GB
    
    def migrate_large_dataset(self):
        """Migrate large datasets efficiently"""
        # Use bulk_create for faster inserts
        # Use iterator() to reduce memory usage
        # Disable indexes during migration
        # Use transactions for batch operations
        
        with transaction.atomic():
            # Disable constraints temporarily
            self.disable_constraints()
            
            try:
                # Migrate in batches
                self.migrate_in_batches()
                
                # Rebuild indexes
                self.rebuild_indexes()
                
            finally:
                # Re-enable constraints
                self.enable_constraints()
    
    def migrate_in_batches(self):
        """Migrate data in batches to manage memory"""
        queryset = LegacyProduct.objects.all()
        
        batch = []
        for obj in queryset.iterator():
            batch.append(obj)
            
            if len(batch) >= self.batch_size:
                self.process_batch(batch)
                batch = []
        
        # Process remaining items
        if batch:
            self.process_batch(batch)
    
    def process_batch(self, batch):
        """Process a batch of objects"""
        # Transform data
        transformed = [self.transform_object(obj) for obj in batch]
        
        # Bulk create
        Product.objects.bulk_create(transformed, batch_size=self.batch_size)
        
        # Clear memory
        del batch
        del transformed
```

### 8.8 Monitoring and Logging

#### Migration Monitoring
```python
class MigrationMonitor:
    """Monitor migration progress and performance"""
    
    def __init__(self):
        self.start_time = timezone.now()
        self.metrics = {
            'records_processed': 0,
            'errors': 0,
            'warnings': 0,
            'memory_usage': 0,
            'processing_time': 0
        }
    
    def log_progress(self, phase, current, total, message=""):
        """Log migration progress"""
        percentage = (current / total) * 100 if total > 0 else 0
        
        log_message = (
            f"Migration Phase {phase}: {current}/{total} "
            f"({percentage:.1f}%) - {message}"
        )
        
        self.stdout.write(log_message)
        
        # Log to file
        with open('migration.log', 'a') as f:
            f.write(f"{timezone.now()}: {log_message}\n")
    
    def track_performance(self, operation, start_time, end_time):
        """Track operation performance"""
        duration = end_time - start_time
        self.metrics['processing_time'] += duration.total_seconds()
        
        performance_log = (
            f"Operation: {operation}, "
            f"Duration: {duration.total_seconds():.2f}s"
        )
        
        with open('migration_performance.log', 'a') as f:
            f.write(f"{timezone.now()}: {performance_log}\n")
    
    def generate_report(self):
        """Generate migration completion report"""
        end_time = timezone.now()
        total_duration = end_time - self.start_time
        
        report = {
            'start_time': self.start_time,
            'end_time': end_time,
            'total_duration': total_duration,
            'metrics': self.metrics,
            'success': self.metrics['errors'] == 0
        }
        
        with open('migration_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return report
```

### 8.9 Post-Migration Tasks

#### Data Verification
```python
class PostMigrationTasks:
    """Tasks to complete after migration"""
    
    def verify_data_counts(self):
        """Verify data counts match legacy system"""
        legacy_counts = {
            'products': LegacyProduct.objects.count(),
            'customers': LegacyCustomer.objects.count(),
            'orders': LegacyOrder.objects.count()
        }
        
        new_counts = {
            'products': Product.objects.count(),
            'customers': Customer.objects.count(),
            'orders': Order.objects.count()
        }
        
        discrepancies = []
        for entity in legacy_counts:
            if legacy_counts[entity] != new_counts[entity]:
                discrepancies.append(
                    f"{entity}: legacy={legacy_counts[entity]}, "
                    f"new={new_counts[entity]}"
                )
        
        return discrepancies
    
    def update_sequences(self):
        """Update database sequences"""
        # Update primary key sequences
        # Update auto-increment values
        pass
    
    def create_indexes(self):
        """Create performance indexes"""
        # Create composite indexes
        # Create full-text search indexes
        pass
    
    def update_caches(self):
        """Update application caches"""
        # Clear Redis caches
        # Warm up frequently accessed data
        pass
```
