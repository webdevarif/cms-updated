# Stores App Rules - DFCMS Compatible

Follow core.md and accounts.md strictly.
All models must use explicit store ForeignKey. Owner references accounts.models.User.
Use standard ViewSet with store filtering.

## 1. Directory Structure (V2-Only Clean Implementation)
```
apps/
├── stores/
│   ├── v2/                    # Version 2 (Current Only)
│   │   ├── __init__.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── services.py
│   │   └── tests.py
│   ├── models/                 # Shared models across versions
│   │   ├── __init__.py
│   │   ├── store.py
│   │   ├── settings.py
│   │   └── theme.py
│   ├── admin.py
│   ├── apps.py
│   ├── middleware.py
│   ├── signals.py
│   ├── tasks.py
│   ├── management/
│   │   └── commands/
│   │       └── migrate_stores.py
│   ├── migrations/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_views.py
│   └── api.md                  # API documentation (REQUIRED)
```

## 2. Core Models

### 2.1 Store Model
```python
# apps/stores/models/store.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import secrets

User = get_user_model()

class Store(models.Model):
    """Store model following DFCMS patterns with explicit store scoping"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]

    TYPE_CHOICES = [
        ('ecommerce', 'E-commerce'),
        ('blog', 'Blog'),
        ('portfolio', 'Portfolio'),
        ('corporate', 'Corporate'),
        ('other', 'Other'),
    ]

    # Core fields (from DFCMS)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    # Ownership (DFCMS compatibility)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_stores'
    )

    # Access & Security (from DFCMS)
    access_code = models.CharField(max_length=6, unique=True, editable=False)
    verification_token = models.CharField(max_length=255, unique=True, blank=True, null=True)

    # Status & Type
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    store_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='ecommerce')

    # Enhanced Features
    domain = models.URLField(blank=True, null=True, unique=True)
    logo = models.ImageField(upload_to='stores/logos/', blank=True, null=True)
    favicon = models.ImageField(upload_to='stores/favicons/', blank=True, null=True)

    # Dynamic Settings (JSON field for configs)
    settings = models.JSONField(default=dict, blank=True)

    # SEO Fields
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)

    # Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True)
    facebook_pixel_id = models.CharField(max_length=50, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_accessed = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'stores_store'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['owner']),
            models.Index(fields=['domain']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.name)

        # Generate access code and verification token for new stores
        if not self.pk:
            self.access_code = self._generate_access_code()
            self.verification_token = secrets.token_urlsafe(32)

        super().save(*args, **kwargs)

    def _generate_access_code(self):
        """Generate unique 6-digit access code"""
        while True:
            code = ''.join(secrets.choice('0123456789') for _ in range(6))
            if not Store.objects.filter(access_code=code).exists():
                return code
```

### 2.2 StoreSettings Model
```python
class StoreSettings(models.Model):
    """Store-specific settings with explicit store relationship"""

    store = models.OneToOneField(
        'Store',
        on_delete=models.CASCADE,
        related_name='store_settings'
    )

    # General Settings
    site_name = models.CharField(max_length=255, default='My Store')
    site_description = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    # Currency & Locale
    currency = models.CharField(max_length=3, default='USD')
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')

    # E-commerce Settings
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    shipping_enabled = models.BooleanField(default=True)
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Media References
    logo = models.ForeignKey(
        'media.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='store_logos',
        help_text="Store logo image"
    )
    favicon = models.ForeignKey(
        'media.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='store_favicons',
        help_text="Store favicon image"
    )

    # Advanced Settings (JSON for flexibility)
    custom_settings = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stores_settings'

    def __str__(self):
        return f"{self.store.name} Settings"
```

## 3. Service Layer

### 3.1 Store Service
```python
# apps/stores/services.py
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.stores.models import Store, StoreSettings
from apps.logs.tasks import log_event_async

class StoreService:
    """Store business logic following DFCMS patterns"""

    @staticmethod
    @transaction.atomic
    def create_store(owner, store_data):
        """Create new store with settings and theme"""
        try:
            # Create store
            store = Store.objects.create(
                owner=owner,
                name=store_data['name'],
                slug=store_data.get('slug', ''),
                description=store_data.get('description', ''),
                store_type=store_data.get('store_type', 'ecommerce')
            )

            # Create default settings
            StoreSettings.objects.create(
                store=store,
                site_name=store.name,
                contact_email=owner.email
            )

            # Log store creation
            log_event_async.delay({
                'event_type': 'CONTENT_CREATE',
                'message': f"Store created: {store.name}",
                'user': owner,
                'store': store,
                'entity_type': 'Store',
                'entity_id': store.id,
                'metadata': {'store_data': store_data}
            })

            return store

        except Exception as e:
            log_event_async.delay({
                'event_type': 'SYSTEM_ERROR',
                'message': f"Failed to create store: {str(e)}",
                'user': owner,
                'level': 'ERROR',
                'metadata': {'error': str(e), 'store_data': store_data}
            })
            raise

    @staticmethod
    def update_store(store, update_data, user=None):
        """Update store with logging"""
        try:
            old_data = {
                'name': store.name,
                'status': store.status,
                'description': store.description
            }

            for field, value in update_data.items():
                if hasattr(store, field):
                    setattr(store, field, value)

            store.save()

            # Log update
            log_event_async.delay({
                'event_type': 'CONTENT_UPDATE',
                'message': f"Store updated: {store.name}",
                'user': user,
                'store': store,
                'entity_type': 'Store',
                'entity_id': store.id,
                'metadata': {
                    'old_data': old_data,
                    'new_data': update_data
                }
            })

            return store

        except Exception as e:
            log_event_async.delay({
                'event_type': 'SYSTEM_ERROR',
                'message': f"Failed to update store: {str(e)}",
                'user': user,
                'store': store,
                'level': 'ERROR',
                'metadata': {'error': str(e), 'update_data': update_data}
            })
            raise

    @staticmethod
    def verify_store(store, token):
        """Verify store email"""
        if store.verification_token == token:
            store.status = 'active'
            store.verification_token = None
            store.save()

            log_event_async.delay({
                'event_type': 'CONTENT_UPDATE',
                'message': f"Store verified: {store.name}",
                'store': store,
                'entity_type': 'Store',
                'entity_id': store.id,
                'metadata': {'verification': True}
            })

            return True
        return False

    @staticmethod
    def get_store_analytics(store, days=30):
        """Get store analytics data from logs"""
        from datetime import timedelta
        from django.utils import timezone
        from apps.logs.models import LogEntry

        since = timezone.now() - timedelta(days=days)

        # Get analytics from logs app
        page_views = LogEntry.objects.filter(
            store=store,
            event_type='PAGE_VIEW',
            created_at__gte=since
        ).count()

        unique_visitors = LogEntry.objects.filter(
            store=store,
            event_type='PAGE_VIEW',
            created_at__gte=since
        ).values('session_id').distinct().count()

        security_events = LogEntry.objects.filter(
            store=store,
            is_suspicious=True,
            created_at__gte=since
        ).count()

        return {
            'page_views': page_views,
            'unique_visitors': unique_visitors,
            'security_events': security_events,
            'period_days': days,
        }
```

## 4. API Views (V2 Only)

### 4.1 Public Store Views
```python
# apps/stores/v2/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from core.viewsets import BaseViewSet
from ..serializers import StorePublicSerializer
from ..services import StoreService

class StorePublicViewSet(BaseViewSet):
    """Public store API - no authentication required"""

    permission_classes = [AllowAny]
    queryset = Store.objects.filter(status='active')
    serializer_class = StorePublicSerializer

    def get_queryset(self):
        """Filter by domain or subdomain"""
        queryset = super().get_queryset()

        # Filter by domain if provided
        domain = self.request.GET.get('domain')
        if domain:
            queryset = queryset.filter(domain=domain)

        return queryset

    @extend_schema(
        summary="Get store by slug",
        description="Get public store details by slug",
        tags=["Stores Public"]
    )
    def retrieve(self, request, *args, **kwargs):
        """Get store details"""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="List active stores",
        description="List all active stores",
        tags=["Stores Public"]
    )
    def list(self, request, *args, **kwargs):
        """List stores"""
        return super().list(request, *args, **kwargs)
```

### 4.2 Dashboard Store Views
```python
# apps/stores/v2/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from core.viewsets import StoreScopedViewSet
from core.permissions import IsStoreOwner
from ..serializers import StoreSerializer, StoreCreateSerializer
from ..services import StoreService

class StoreViewSet(StoreScopedViewSet):
    """Store management API for dashboard"""

    permission_classes = [IsAuthenticated, IsStoreOwner]
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    def get_queryset(self):
        """Filter by current user's stores"""
        return super().get_queryset().filter(owner=self.request.user)

    @extend_schema(
        summary="Create store",
        description="Create new store",
        request=StoreCreateSerializer,
        responses={201: StoreSerializer},
        tags=["Stores Dashboard"]
    )
    def create(self, request, *args, **kwargs):
        """Create new store"""
        serializer = StoreCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        store = StoreService.create_store(
            owner=request.user,
            store_data=serializer.validated_data
        )

        return Response(
            StoreSerializer(store).data,
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        summary="Update store",
        description="Update store details",
        tags=["Stores Dashboard"]
    )
    def update(self, request, *args, **kwargs):
        """Update store"""
        store = self.get_object()
        updated_store = StoreService.update_store(
            store=store,
            update_data=request.data,
            user=request.user
        )

        return Response(StoreSerializer(updated_store).data)

    @extend_schema(
        summary="Store analytics",
        description="Get store analytics data",
        tags=["Stores Dashboard"]
    )
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get store analytics"""
        store = self.get_object()
        days = int(request.GET.get('days', 30))

        analytics = StoreService.get_store_analytics(store, days)
        return Response(analytics)
```

## 5. Serializers

### 5.1 Store Serializers
```python
# apps/stores/v2/serializers.py
from rest_framework import serializers
from core.serializers import BaseSerializer
from apps.stores.models import Store, StoreSettings, StoreTheme

class StorePublicSerializer(BaseSerializer):
    """Public store information"""

    class Meta:
        model = Store
        fields = [
            'id', 'name', 'slug', 'description', 'logo',
            'domain', 'meta_title', 'meta_description',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class StoreSerializer(BaseSerializer):
    """Full store information for owners"""
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    store_type_display = serializers.CharField(source='get_store_type_display', read_only=True)

    class Meta:
        model = Store
        fields = '__all__'
        read_only_fields = ['id', 'owner', 'access_code', 'created_at']

class StoreCreateSerializer(BaseSerializer):
    """Store creation serializer"""

    class Meta:
        model = Store
        fields = ['name', 'slug', 'description', 'store_type']

    def validate_slug(self, value):
        """Validate slug uniqueness"""
        if Store.objects.filter(slug=value).exists():
            raise serializers.ValidationError("Store with this slug already exists.")
        return value

class StoreSettingsSerializer(BaseSerializer):
    """Store settings serializer"""

    class Meta:
        model = StoreSettings
        fields = '__all__'

class StoreThemeSerializer(BaseSerializer):
    """Store theme serializer"""

    class Meta:
        model = StoreTheme
        fields = '__all__'
```

## 6. Migration & Legacy Rules

### 6.1 Migration Command
```python
# apps/stores/management/commands/migrate_stores.py
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.stores.models import Store

class Command(BaseCommand):
    help = 'Migrate old stores from DFCMS structure'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be migrated')
        parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for migration')

    def handle(self, *args, **options):
        from apps.activity_logs.models import ActivityLog  # Old DFCMS

        # Migrate stores logic here
        self.stdout.write(self.style.SUCCESS("Store migration completed"))
```

## 7. Signals for Logging

```python
# apps/stores/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Store, StoreSettings, StoreTheme
from apps.logs.tasks import log_event_async

@receiver(post_save, sender=Store)
def log_store_change(sender, instance, created, **kwargs):
    """Log store changes"""
    if created:
        event_type = 'CONTENT_CREATE'
        message = f"Store created: {instance.name}"
    else:
        event_type = 'CONTENT_UPDATE'
        message = f"Store updated: {instance.name}"

    log_event_async.delay({
        'event_type': event_type,
        'message': message,
        'store': instance,
        'entity_type': 'Store',
        'entity_id': instance.id,
        'metadata': {'created': created}
    })

@receiver(post_delete, sender=Store)
def log_store_deletion(sender, instance, **kwargs):
    """Log store deletion"""
    log_event_async.delay({
        'event_type': 'CONTENT_DELETE',
        'message': f"Store deleted: {instance.name}",
        'entity_type': 'Store',
        'entity_id': instance.id,
        'metadata': {'store_name': instance.name}
    })
```

## 8. What AI Can Do

### ✅ **Allowed Actions**
1. **Create Store Models**: Following exact model patterns with explicit store FK
2. **Implement Services**: Business logic in services.py with logging integration
3. **Create ViewSets**: V2-only ViewSets with StoreScopedViewSet base
4. **Add Serializers**: Both public and internal serializers with validation
5. **Configure URLs**: V2 URL patterns with nested routes
6. **Write Tests**: Model, service, and API tests with proper coverage
7. **Add Admin**: Django admin configuration for store management
8. **Implement Signals**: Auto-logging integration with logs app

### 🚫 **Forbidden Actions**
1. **No V1 References**: Only V2 implementation allowed
2. **No Business Logic in Views**: All logic must be in services
3. **No Hardcoded Values**: Use settings or configuration
4. **No Direct Database Queries**: Use service layer
5. **No Missing Store FK**: All models must have store relationship
6. **No Missing Logging**: All actions must be logged
7. **No TenantModel**: Use explicit store FK relationships
8. **No Nested Subfolders**: Models stay in apps/stores/models/
9. **No Missing API Documentation**: api.md file is REQUIRED
10. **No Missing Tests**: Minimum 80% coverage required

---

**Review suggested changes carefully before applying.**
