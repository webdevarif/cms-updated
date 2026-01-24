"""
Initial ecommerce migration with DFCMS legacy data mapping.

This migration creates the new store-scoped ecommerce models and provides
basic mapping from legacy DFCMS ecommerce data to the new structure.
"""
from django.db import migrations, models
import django.db.models.deletion
import logging

logger = logging.getLogger(__name__)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('stores', '0001_initial'),
        ('mediafile', '0001_initial'),
    ]

    operations = [
        # Product Model
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('sku', models.CharField(max_length=100, unique=True)),
                ('upc', models.CharField(blank=True, max_length=12, null=True, unique=True)),
                ('description', models.TextField(blank=True)),
                ('short_description', models.TextField(blank=True, max_length=500)),
                ('base_price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('compare_at_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('cost_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('track_inventory', models.BooleanField(default=True)),
                ('inventory_quantity', models.IntegerField(default=0)),
                ('inventory_policy', models.CharField(choices=[('deny', 'Deny'), ('continue', 'Continue')], default='deny', max_length=20)),
                ('allow_backorder', models.BooleanField(default=False)),
                ('requires_shipping', models.BooleanField(default=True)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('active', 'Active'), ('archived', 'Archived')], default='draft', max_length=20)),
                ('is_featured', models.BooleanField(default=False)),
                ('is_available', models.BooleanField(default=True)),
                ('seo_title', models.CharField(blank=True, max_length=255)),
                ('seo_description', models.TextField(blank=True, max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='stores.store')),
                ('featured_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='featured_products', to='mediafile.mediafile')),
                ('digital_file_media', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mediafile.mediafile')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_products', to='auth.user')),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['store', 'sku']),
                    models.Index(fields=['store', 'status']),
                    models.Index(fields=['store', 'is_featured']),
                    models.Index(fields=['store', 'slug']),
                ],
            },
        ),
        
        # ProductVariant Model
        migrations.CreateModel(
            name='ProductVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('sku', models.CharField(max_length=100)),
                ('barcode', models.CharField(blank=True, max_length=50)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('compare_at_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('cost_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('inventory_quantity', models.IntegerField(default=0)),
                ('inventory_policy', models.CharField(choices=[('deny', 'Deny'), ('continue', 'Continue')], default='deny', max_length=20)),
                ('requires_shipping', models.BooleanField(default=True)),
                ('taxable', models.BooleanField(default=True)),
                ('position', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='public_ecommerce.product')),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mediafile.mediafile')),
            ],
            options={
                'verbose_name': 'Product Variant',
                'verbose_name_plural': 'Product Variants',
                'ordering': ['position'],
                'indexes': [
                    models.Index(fields=['product', 'sku']),
                ],
            },
        ),
        
        # Cart Model
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, max_length=40)),
                ('status', models.CharField(choices=[('active', 'Active'), ('abandoned', 'Abandoned'), ('converted', 'Converted')], default='active', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carts', to='stores.store')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='carts', to='auth.user')),
            ],
            options={
                'verbose_name': 'Cart',
                'verbose_name_plural': 'Carts',
                'ordering': ['-updated_at'],
                'indexes': [
                    models.Index(fields=['store', 'user']),
                    models.Index(fields=['store', 'session_key']),
                ],
            },
        ),
        
        # CartItem Model
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='public_ecommerce.cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='public_ecommerce.product')),
                ('variant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='public_ecommerce.productvariant')),
            ],
            options={
                'verbose_name': 'Cart Item',
                'verbose_name_plural': 'Cart Items',
                'ordering': ['cart', '-created_at'],
                'indexes': [
                    models.Index(fields=['cart', 'product']),
                    models.Index(fields=['cart', 'variant']),
                ],
            },
        ),
        
        # Order Model
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=50, unique=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tax', models.DecimalField(decimal_places=2, max_digits=10, default=0)),
                ('shipping', models.DecimalField(decimal_places=2, max_digits=10, default=0)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('customer_email', models.EmailField(blank=True, max_length=254)),
                ('customer_phone', models.CharField(blank=True, max_length=20)),
                ('shipping_address', models.TextField(blank=True)),
                ('billing_address', models.TextField(blank=True)),
                ('customer_notes', models.TextField(blank=True)),
                ('fulfillment_status', models.CharField(choices=[('unfulfilled', 'Unfulfilled'), ('partial', 'Partial'), ('fulfilled', 'Fulfilled')], default='unfulfilled', max_length=20)),
                ('tracking_number', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='stores.store')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='auth.user')),
            ],
            options={
                'verbose_name': 'Order',
                'verbose_name_plural': 'Orders',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['store', 'order_number']),
                    models.Index(fields=['store', 'status']),
                    models.Index(fields=['store', 'created_at']),
                ],
            },
        ),
        
        # OrderItem Model
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('sku', models.CharField(max_length=100)),
                ('quantity', models.IntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='public_ecommerce.order')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='public_ecommerce.product')),
                ('variant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='public_ecommerce.productvariant')),
            ],
            options={
                'verbose_name': 'Order Item',
                'verbose_name_plural': 'Order Items',
                'ordering': ['order', 'created_at'],
                'indexes': [
                    models.Index(fields=['order', 'product']),
                    models.Index(fields=['order', 'variant']),
                ],
            },
        ),
        
        # Data migration from legacy DFCMS
        migrations.RunPython(
            'migrate_legacy_dfcms_ecommerce_data',
            reverse_code=migrations.RunPython.noop
        ),
    ]


def migrate_legacy_dfcms_ecommerce_data(apps, schema_editor):
    """
    Migrate legacy DFCMS ecommerce data to new store-scoped structure.
    
    This migration provides basic mapping from legacy DFCMS ecommerce data to the new structure.
    """
    from django.db import connection
    from apps.stores.models import Store
    from ..models import Product
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Get all stores for migration
    stores = Store.objects.all()
    if not stores.exists():
        logger.warning("No stores found for migration")
        return
    
    # Get legacy data from DFCMS ecommerce tables (if they exist)
    try:
        with connection.cursor() as cursor:
            # Check if legacy tables exist
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = DATABASE_NAME 
                AND table_name LIKE 'legacy_%'
            """)
            legacy_tables = [row[0] for row in cursor.fetchall()]
            
            if 'legacy_products' in legacy_tables:
                cursor.execute("SELECT * FROM legacy_products")
                legacy_products = cursor.fetchall()
                
                # Get column names for mapping
                columns = [desc[0] for desc in cursor.description]
                
                # Map legacy products to new structure
                for product_row in legacy_products:
                    try:
                        # Create mapping dictionary based on columns
                        product_data = dict(zip(columns, product_row))
                        
                        # Find appropriate store (first store for now)
                        store = stores.first()
                        
                        # Create new Product with store mapping
                        new_product = Product.objects.create(
                            store=store,
                            title=product_data.get('title', ''),
                            slug=product_data.get('slug', ''),
                            description=product_data.get('description', ''),
                            base_price=product_data.get('price', 0),
                            sku=product_data.get('sku', ''),
                            status='active'
                        )
                        logger.info(f"Migrated product: {new_product.title}")
                    except Exception as e:
                        logger.error(f"Failed to migrate product: {e}")
            else:
                logger.info("No legacy products table found")
                
    except Exception as e:
        logger.error(f"Error during legacy data migration: {e}")
    
    logger.info("Legacy DFCMS ecommerce data migration completed")
