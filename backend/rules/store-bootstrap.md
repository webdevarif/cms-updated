# Store-Bootstrap Rules v1.0

## 🎯 Purpose
This document defines the complete store bootstrap lifecycle for CMS-Updated backend, ensuring all stores are properly initialized with required content types, roles, settings, and permissions upon creation.

## 🏗️ Structure
### **Bootstrap Phases**
When a new store is created, the following phases **must** be executed in order:
1. **Phase 1: Core Store Creation** - Basic store record
2. **Phase 2: Content Type Initialization** - Required post types
3. **Phase 3: Role and Permission Setup** - Default roles and permissions
4. **Phase 4: Default Configuration** - Store settings and preferences
5. **Phase 5: Theme Initialization** - Default theme setup
6. **Phase 6: Search Index Creation** - Search infrastructure
7. **Phase 7: Cache Warming** - Initial cache population
8. **Phase 8: Notification Setup** - Default notification preferences

## 🔧 Implementation
```python
# apps/stores/services.py
from django.db import transaction
import logging
logger = logging.getLogger(__name__)
class StoreBootstrapService:
    """Store bootstrap service"""
    @staticmethod
    @transaction.atomic
    def bootstrap_store(store):
        """
        Bootstrap a new store with all required components
        """
        try:
            logger.info(f"Starting bootstrap for store: {store.slug}")
            # Phase 1: Core store creation (already done)
            StoreBootstrapService._phase1_complete(store)
            # Phase 2: Content type initialization
            # Mark as complete
            store.bootstrap_completed = True
            store.bootstrap_phase = 'completed'
            store.save(update_fields=['bootstrap_completed', 'bootstrap_phase'])
        except Exception as e:
            store.bootstrap_error = str(e)
            store.save(update_fields=['bootstrap_error'])
            logger.error(f"Bootstrap failed for store {store.slug}: {e}")
            raise
    @staticmethod
    def _bootstrap_phase_2(store, actor):
        """
        Initialize content types and default pages
        Args:
            store: The Store instance
            actor: The User who initiated the bootstrap
        """
        logger.info(f"Starting phase 2 for store: {store.slug}")
        # Create required post types
        post_types = [
            {
                'name': 'Page',
                'slug': 'page',
                'description': 'Static pages for the store',
                'is_system': True,
                'is_deletable': False
            },
            {
                'name': 'Blog',
                'slug': 'blog',
                'description': 'Blog posts for the store',
                'is_system': True,
                'is_deletable': False
            },
            {
                'name': 'Product',
                'slug': 'product',
                'description': 'Product catalog',
                'is_system': True,
                'is_deletable': False
            }
        ]
        for post_type_data in post_types:
            PostType.objects.get_or_create(
                store=store,
                slug=post_type_data['slug'],
                defaults={
                    'name': post_type_data['name'],
                    'description': post_type_data['description'],
                    'is_system': post_type_data['is_system'],
                    'is_deletable': post_type_data['is_deletable'],
                    'created_by': actor  # Use the actor as creator
                }
            )
        # Create default pages
        StoreBootstrapService._create_default_pages(store)
        store.bootstrap_phase = 'phase2_complete'
        store.save(update_fields=['bootstrap_phase'])
        logger.info(f"Phase 2 complete for store: {store.slug}")
    @staticmethod
    def _bootstrap_phase_3(store, actor):
        """
        Initialize roles and permissions
        Args:
            store: The Store instance
            actor: The User who will be assigned as store owner
        """
        logger.info(f"Starting phase 3 for store: {store.slug}")
        # Create default roles
        roles = [
            {
                'name': 'Owner',
                'slug': 'owner',
                'description': 'Full access to all store features',
                'is_system': True,
                'permissions': ['*']
            },
            {
                'name': 'Admin',
                'slug': 'admin',
                'description': 'Administrative access to store',
                'is_system': True,
                'permissions': ['content.*', 'ecommerce.*', 'settings.*']
            },
            {
                'name': 'Manager',
                'slug': 'manager',
                'description': 'Manager access to store',
                'is_system': True,
                'permissions': ['content.read', 'content.write', 'ecommerce.read', 'ecommerce.write']
            },
            {
                'name': 'Staff',
                'slug': 'staff',
                'description': 'Staff access to store',
                'is_system': True,
                'permissions': ['content.read', 'ecommerce.read']
            },
            {
                'name': 'Viewer',
                'slug': 'viewer',
                'description': 'Read-only access to store',
                'is_system': True,
                'permissions': ['content.read']
            }
        ]
        owner_role = None
        for role_data in roles:
            role, created = Role.objects.get_or_create(
                store=store,
                slug=role_data['slug'],
                defaults={
                    'name': role_data['name'],
                    'description': role_data['description'],
                    'is_system': role_data['is_system'],
                    'created_by': actor  # Track who created the role
                }
            )
            if created and role_data.get('permissions'):
                role.permissions.set(role_data['permissions'])
            if role.slug == 'owner':
                owner_role = role
        # Assign owner role to the actor
        if owner_role:
            StoreMember.objects.get_or_create(
                store=store,
                user=actor,
                defaults={
                    'role': owner_role,
                    'is_active': True
                }
            )
        StoreMember.objects.get_or_create(
            store=store,
            user=store.owner,
            defaults={'role': owner_role}
        )
        store.bootstrap_phase = 'phase3_complete'
        store.save(update_fields=['bootstrap_phase'])
        logger.info(f"Phase 3 complete for store: {store.slug}")
    @staticmethod
    def _create_role_permissions(store, role):
        """Create permissions for a role"""
        from apps.accounts.models import Permission
        # Define permission sets based on role
        permission_sets = {
            'owner': ['*'],  # All permissions
            'admin': ['content.*', 'ecommerce.*', 'settings.*'],
            'manager': ['content.read', 'content.write', 'ecommerce.read', 'ecommerce.write'],
            'staff': ['content.read', 'ecommerce.read'],
            'viewer': ['content.read']
        }
        permissions = permission_sets.get(role.slug, [])
        for perm in permissions:
            Permission.objects.get_or_create(
                store=store,
                code=perm,
                defaults={'description': f'{perm} permission'}
            )
            role.permissions.add(Permission.objects.get(store=store, code=perm))
    @staticmethod
    def _phase4_configuration(store):
        """Phase 4: Default configuration"""
        from apps.metafields.services import MetaFieldService
        # Set default store configuration
        default_config = {
            'currency': 'USD',
            'timezone': 'UTC',
            'language': 'en_US',
            'date_format': 'MM/DD/YYYY',
            'time_format': 'HH:mm',
            'tax_rate': '0.00',
            'shipping_free_threshold': '0'
        }
        for key, value in default_config.items():
            MetaFieldService.set_metafield_value(
                store,
                key,
                value,
                namespace='config'
            )
        store.bootstrap_phase = 'phase4_complete'
        store.save(update_fields=['bootstrap_phase'])
        logger.info(f"Phase 4 complete for store: {store.slug}")
    @staticmethod
    def _phase5_theme(store):
        """Phase 5: Theme initialization"""
        from apps.themes.models import Theme, ColorScheme, Typography
        # Create default theme
        theme, created = Theme.objects.get_or_create(
            store=store,
            name='Default Theme',
            defaults={'is_active': True}
        )
        if created:
            # Create default color scheme
            ColorScheme.objects.create(
                store=store,
                theme=theme,
                name='Light',
                colors={
                    'primary': '#0066cc',
                    'secondary': '#666666',
                    'background': '#ffffff',
                    'text': '#333333',
                    'accent': '#ff6600'
                },
                is_default=True
            )
            # Create default typography
            Typography.objects.create(
                store=store,
                theme=theme,
                base_font_size=16,
                font_smoothing=True,
                font_families={
                    'primary': 'Arial, sans-serif',
                    'heading': 'Georgia, serif'
                }
            )
        store.bootstrap_phase = 'phase5_complete'
        store.save(update_fields=['bootstrap_phase'])
        logger.info(f"Phase 5 complete for store: {store.slug}")
    @staticmethod
    def _phase6_search_index(store):
        """Phase 6: Search index creation"""
        from apps.search.models import SearchIndex
        # Create search index for store
        SearchIndex.objects.get_or_create(
            store=store,
            name='Default Search Index',
            defaults={
                'index_name': f'{store.slug}_search',
                'content_types': ['Page', 'Post', 'Product'],
                'fields': {
                    'title': 'text',
                    'content': 'text',
                    'description': 'text'
                },
                'facets': [
                    {'field': 'type', 'label': 'Type'},
                    {'field': 'category_id', 'label': 'Category'}
                ],
                'is_active': True
            }
        )
        # Warm search index
        from apps.search.services import SearchService
        SearchService.rebuild_index(store)
        store.bootstrap_phase = 'phase6_complete'
        store.save(update_fields=['bootstrap_phase'])
        logger.info(f"Phase 6 complete for store: {store.slug}")
    @staticmethod
    def _phase7_cache_warming(store):
        """Phase 7: Cache warming"""
        from apps.cache.services import CacheWarmupService
        # Warm cache for store
        CacheWarmupService.warm_store_cache(store)
        store.bootstrap_phase = 'phase7_complete'
        store.save(update_fields=['bootstrap_phase'])
        logger.info(f"Phase 7 complete for store: {store.slug}")
    @staticmethod
    def _phase8_notifications(store):
        """Phase 8: Notification setup"""
        from apps.notifications.models import NotificationPreference, NotificationTemplate
        # Create default notification templates
        templates = [
            {
                'notification_type': 'order.created',
                'title_template': 'Order Created',
                'message_template': 'Your order {{order_number}} has been created',
                'email_subject_template': 'Order Confirmation - {{order_number}}',
                'email_body_template': 'Thank you for your order!'
            },
            {
                'notification_type': 'user.registered',
                'title_template': 'Welcome to {{store_name}}',
                'message_template': 'Welcome to our store!',
                'email_subject_template': 'Welcome to {{store_name}}',
                'email_body_template': 'Thank you for registering!'
            }
        ]
        for template_data in templates:
            NotificationTemplate.objects.get_or_create(
                store=store,
                notification_type=template_data['notification_type'],
                defaults=template_data
            )
        # Create default notification preferences for owner
        notification_types = [
            'order.created', 'order.shipped', 'order.delivered',
            'user.registered', 'form.submitted', 'system.alert'
        ]
        for notification_type in notification_types:
            NotificationPreference.objects.get_or_create(
                store=store,
                user=store.owner,
                notification_type=notification_type,
                defaults={
                    'channel_preferences': {'email': True, 'in_app': True},
                    'digest_enabled': False
                }
            )
        store.bootstrap_phase = 'phase8_complete'
        store.save(update_fields=['bootstrap_phase'])
        logger.info(f"Phase 8 complete for store: {store.slug}")
```

---

## 🔒 Permissions
[Permissions content to be added]

## 🧪 Testing
### **Required Coverage**
- **Bootstrap Service**: 100% code coverage
- **Integration**: Critical path testing
- **Error Handling**: Test failure scenarios

### **Test Examples**
```python
# apps/stores/tests/test_bootstrap.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from ..services import StoreBootstrapService
from ..models import Store
User = get_user_model()
class StoreBootstrapTest(TestCase):
    """
    Test the store bootstrap process
    Note: We create a test user here because tests run in isolation.
    In production, the user would come from the request.
    """
    def setUp(self):
        # Create a test user to simulate the actor
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password'
        )
        # Create a store owned by the test user
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store',
            owner=self.user
        )
    def test_complete_bootstrap_flow(self):
        """Test the complete bootstrap flow"""
        # Execute bootstrap
        StoreBootstrapService.bootstrap_store(store=self.store, actor=self.user)
        # Refresh store from DB
        self.store.refresh_from_db()
        # Verify bootstrap completed
        self.assertTrue(self.store.bootstrap_completed)
        self.assertEqual(self.store.bootstrap_phase, 'completed')
        # Verify post types were created
        from apps.posts.models import PostType
        self.assertTrue(PostType.objects.filter(store=self.store).exists())
        # Verify roles were created
        from apps.accounts.models import Role
        self.assertTrue(Role.objects.filter(store=self.store).exists())
        # Verify owner role was assigned to the actor
        from apps.accounts.models import StoreMember
        member = StoreMember.objects.get(store=self.store, user=self.user)
        self.assertEqual(member.role.slug, 'owner')
    def test_bootstrap_with_existing_owner(self):
        """Test bootstrap when owner already exists"""
        # First bootstrap
        StoreBootstrapService.bootstrap_store(store=self.store, actor=self.user)
        # Should not create duplicate owner
        from apps.accounts.models import StoreMember
        owners = StoreMember.objects.filter(
            store=self.store,
            role__slug='owner'
        )
        self.assertEqual(owners.count(), 1)
    def test_bootstrap_error_handling(self):
        """Test error handling during bootstrap"""
        # Force an error by making store name invalid
        self.store.name = ''
        self.store.save(update_fields=['name'])
        with self.assertRaises(ValueError):
            StoreBootstrapService.bootstrap_store(store=self.store, actor=self.user)
        # Verify error state was recorded
        self.store.refresh_from_db()
        self.assertIsNotNone(self.store.bootstrap_error)
        self.assertFalse(self.store.bootstrap_completed)
        # Retry bootstrap
        result = StoreBootstrapService.retry_bootstrap(store)
        self.assertTrue(result)
        self.assertTrue(store.bootstrap_completed)
```

---

## ⚙️ Services
StoreBootstrapService.bootstrap_store(self)
```
### **Store Model Integration**
Your existing `Store` model should already have these core fields:
- `name`
- `slug` (unique)
- `status` (with appropriate choices)
- `owner` (ForeignKey to User)
- `created_at`
- `updated_at`
```

---

## 🔗 Dependencies
[Dependencies content to be added]

## 📋 Migration
### **Bootstrap Fields to Add to Store Model**
Add these fields to your existing `Store` model in `apps/stores/models.py`:
```python
# Bootstrap tracking fields
bootstrap_completed = models.BooleanField(
    default=False,
    help_text="Indicates if bootstrap process has completed successfully"
)
bootstrap_phase = models.CharField(
    max_length=50,
    blank=True,
    help_text="Current phase of the bootstrap process"
)
bootstrap_error = models.TextField(
    blank=True,
    help_text="Any errors that occurred during bootstrap"
)
```
### **Bootstrap Lifecycle Hook**
Add this to your `Store` model's `save()` method:
```python
def save(self, *args, **kwargs):
    is_new = self.pk is None
    super().save(*args, **kwargs)

    if is_new:
        # Import here to avoid circular imports
        from .services import StoreBootstrapService
        StoreBootstrapService.bootstrap_store(self)
```
### **Store Model Integration**
Your existing `Store` model should already have these core fields:
- `name`
- `slug` (unique)
- `status` (with appropriate choices)
- `owner` (ForeignKey to User)
- `created_at`
- `updated_at`
```

---

## ✅ Benefits
[Benefits content to be added]

---
**Version**: 1.0
**Last Updated**: 2026-01-26
**Next Review**: 2026-02-25
