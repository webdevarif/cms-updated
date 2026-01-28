# Metafields Rules v1.0

## 🎯 Purpose
This document defines the architecture and implementation rules for the Metafields system, enabling dynamic custom fields for any model in the CMS-Updated platform.

---

## 🏗️ Structure
### **Fixed Directory Structure**
```
apps/
├── public/                    # Public APIs (no authentication)
│   └── metafields/           # Public metafield APIs
│       ├── v2/               # Version 2 (Current Only)
│       │   ├── urls.py
│       │   ├── views.py
│       │   ├── serializers.py
│       │   └── tests.py
│       ├── models/             # Shared models across versions
│       │   ├── __init__.py
│       │   ├── definitions.py  # MetafieldDefinition model
│       │   └── values.py       # Metafield model
│       ├── services.py
│       └── admin.py
├── customer/                  # Customer APIs (customer authentication)
│   └── metafields/           # Customer metafield APIs
│       ├── v2/               # Version 2 (Current Only)
│       │   ├── urls.py
│       │   ├── views.py
│       │   ├── serializers.py
│       │   └── tests.py
│       └── models/             # Same shared models
└── dashboard/                 # Dashboard APIs (admin authentication)
    └── metafields/           # Dashboard metafield APIs
        ├── v2/               # Version 2 (Current Only)
        │   ├── urls.py
        │   ├── views.py
        │   ├── serializers.py
        │   └── tests.py
        └── models/             # Same shared models
```

---

## 🔧 Implementation
### **MetafieldDefinition Model**
```python
# apps/public/metafields/models/definitions.py
from django.db import models
from core.models import TenantModel

class MetafieldDefinition(TenantModel):
    """Defines the structure and validation for metafields"""

    # Core Identification
    name = models.CharField(max_length=100)
    namespace = models.CharField(max_length=50, help_text="Category for grouping fields")
    key = models.CharField(max_length=50, help_text="Unique identifier within namespace")

    # Type and Validation
    TYPE_CHOICES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('boolean', 'True/False'),
        ('date', 'Date'),
        ('url', 'URL'),
        ('json', 'JSON'),
        ('select', 'Dropdown'),
        ('multiselect', 'Multi-select'),
        ('image', 'Image'),
        ('file', 'File'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    # Configuration
    is_required = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    is_filterable = models.BooleanField(default=False)
    is_sortable = models.BooleanField(default=False)

    # Options for select fields
    options = models.JSONField(
        default=list,
        help_text="Options for select/multiselect fields"
    )

    # Validation rules
    validations = models.JSONField(
        default=dict,
        help_text="Validation rules (min_length, max_length, etc.)"
    )

    # Content types this field applies to
    content_types = models.JSONField(
        default=list,
        help_text="Which models this field applies to"
    )

    # UI Configuration
    ui = models.JSONField(
        default=dict,
        help_text="UI configuration (placeholder, help text, etc.)"
    )

    class Meta(TenantModel.Meta):
        db_table = 'metafields_definition'
        unique_together = [['store', 'namespace', 'key']]
        indexes = [
            models.Index(fields=['namespace', 'key']),
            models.Index(fields=['is_visible']),
            models.Index(fields=['content_types']),
        ]
        ordering = ['namespace', 'key']

    def __str__(self):
        return f"{self.namespace}.{self.key}"

    def clean(self):
        """Validate the definition"""
        from django.core.exceptions import ValidationError

        # Validate namespace/key format
        if not self.namespace.islower():
            raise ValidationError("Namespace must be lowercase")

        if not self.key.islower():
            raise ValidationError("Key must be lowercase")

        # Validate options for select fields
        if self.type in ['select', 'multiselect'] and not self.options:
            raise ValidationError("Select fields must have options defined")
```

### **Metafield Model**
```python
# apps/public/metafields/models/values.py
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from core.models import TenantModel

class Metafield(TenantModel):
    """Stores actual metafield values with generic relations"""

    # Link to definition
    definition = models.ForeignKey(
        'metafields.MetafieldDefinition',
        on_delete=models.CASCADE,
        related_name='values'
    )

    # Generic relation to any model
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Value storage (type-specific)
    value_text = models.TextField(blank=True, null=True)
    value_number = models.FloatField(blank=True, null=True)
    value_boolean = models.BooleanField(blank=True, null=True)
    value_date = models.DateTimeField(blank=True, null=True)
    value_json = models.JSONField(blank=True, null=True)

    # Media fields (for image/file types)
    value_media = models.ForeignKey(
        'media.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = 'metafields_value'
        unique_together = [
            ['store', 'definition', 'content_type', 'object_id']
        ]
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['definition', 'value_text']),
            models.Index(fields=['definition', 'value_number']),
            models.Index(fields=['definition', 'value_boolean']),
        ]
        ordering = ['definition', 'created_at']

    def __str__(self):
        return f"{self.definition} = {self.get_value()}"

    def get_value(self):
        """Get the value in the correct type"""
        if self.definition.type in ['image', 'file']:
            return self.value_media
        return getattr(self, f'value_{self.definition.type}', None)

    def set_value(self, value):
        """Set the value with type conversion"""
        if self.definition.type in ['image', 'file']:
            self.value_media = value
        else:
            field_name = f'value_{self.definition.type}'
            setattr(self, field_name, value)

            # Clear other value fields
            for t in ['text', 'number', 'boolean', 'date', 'json']:
                if t != self.definition.type:
                    setattr(self, f'value_{t}', None)
            self.value_media = None
```

---

## 🔒 Permissions
### **Access Control**
- **Store Owners**: Full CRUD on all metafields
- **Staff**: Read-only access to metafields
- **Public**: Read-only access to public metafields (if `is_visible=True`)

### **Validation Rules**
- Namespace and keys must be lowercase alphanumeric with underscores
- Values are validated against their type definition
- Required fields must have values
- Select fields must have valid options

---

## 🧪 Testing
### **Test Cases**
```python
# tests/test_metafields.py
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from apps.products.models import Product
from ..models import MetafieldDefinition, Metafield

class MetafieldTests(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name="Test Store", slug="test-store")
        self.product = Product.objects.create(
            store=self.store,
            name="Test Product",
            sku="TEST-001"
        )

        # Create a test metafield definition
        self.defn = MetafieldDefinition.objects.create(
            store=self.store,
            name="Stock Warning Level",
            namespace="inventory",
            key="stock_warning_level",
            type="number"
        )

    def test_metafield_creation(self):
        """Test creating a metafield"""
        metafield = Metafield.objects.create(
            store=self.store,
            definition=self.defn,
            content_object=self.product,
            value_number=10
        )

        self.assertEqual(metafield.value_number, 10)
        self.assertEqual(metafield.content_object, self.product)
```

---

## ⚙️ Services
### **MetafieldService**
```python
# apps/public/metafields/services.py
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType

class MetafieldService:
    """Core service for metafield operations"""

    @staticmethod
    def get_metafield_definition(store, namespace, key):
        """Get a metafield definition by namespace and key"""
        from .models import MetafieldDefinition
        return MetafieldDefinition.objects.get(
            store=store,
            namespace=namespace,
            key=key
        )

    @staticmethod
    def get_metafield(instance, definition):
        """Get a metafield value for an instance"""
        from .models import Metafield

        content_type = ContentType.objects.get_for_model(instance)
        return Metafield.objects.filter(
            definition=definition,
            content_type=content_type,
            object_id=instance.id,
            store=instance.store
        ).first()

    @staticmethod
    def set_metafield(instance, namespace, key, value):
        """Set a metafield value for an instance"""
        from .models import Metafield, MetafieldDefinition

        # Get or create definition
        definition, created = MetafieldDefinition.objects.get_or_create(
            store=instance.store,
            namespace=namespace,
            key=key,
            defaults={
                'name': f"{namespace}.{key}",
                'type': MetafieldService._infer_type(value),
                'content_types': [ContentType.objects.get_for_model(instance).model]
            }
        )

        # Get or create metafield
        content_type = ContentType.objects.get_for_model(instance)
        metafield, created = Metafield.objects.get_or_create(
            definition=definition,
            content_type=content_type,
            object_id=instance.id,
            store=instance.store
        )

        # Set and save value
        metafield.set_value(value)
        metafield.save()

        return metafield

    @staticmethod
    def _infer_type(value):
        """Infer metafield type from Python type"""
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, (int, float)):
            return 'number'
        elif isinstance(value, dict):
            return 'json'
        return 'text'

    @staticmethod
    def get_metafields_for_object(instance, namespace=None):
        """Get all metafields for an object, optionally filtered by namespace"""
        from .models import Metafield, MetafieldDefinition

        content_type = ContentType.objects.get_for_model(instance)
        queryset = Metafield.objects.filter(
            store=instance.store,
            content_type=content_type,
            object_id=instance.id
        ).select_related('definition')

        if namespace:
            queryset = queryset.filter(definition__namespace=namespace)

        return queryset
```

---

## 🔗 Dependencies
```tree
[Related components with @path references]
```
- core.md for base models and utilities
- stores.md for store scoping and multi-tenancy
- media.md for image/file metafield support
- contenttypes.md for generic relationships

---

## 📋 Migration
### **From Legacy Custom Fields**
```python
# apps/metafields/management/commands/migrate_metafields.py
from django.core.management.base import BaseCommand
from django.db import transaction

class Command(BaseCommand):
    help = 'Migrate legacy custom fields to metafields system'

    def handle(self, *args, **options):
        from apps.legacy.models import CustomField, CustomFieldValue
        from .models import MetafieldDefinition, Metafield

        with transaction.atomic():
            # Migrate definitions
            for legacy_field in CustomField.objects.all():
                definition = MetafieldDefinition.objects.create(
                    store=legacy_field.store,
                    name=legacy_field.name,
                    namespace=legacy_field.category or 'custom',
                    key=legacy_field.key,
                    type=legacy_field.field_type,
                    is_required=legacy_field.required,
                    options=legacy_field.options or []
                )

                # Migrate values
                for legacy_value in CustomFieldValue.objects.filter(
                    field=legacy_field
                ):
                    Metafield.objects.create(
                        store=legacy_field.store,
                        definition=definition,
                        content_type=ContentType.objects.get_for_model(legacy_value.content_object),
                        object_id=legacy_value.object_id,
                        **{f'value_{legacy_field.field_type}': legacy_value.value}
                    )

        self.stdout.write(self.style.SUCCESS('Migration completed'))
```

---

## ✅ Benefits
- ✅ **Dynamic Fields**: Add custom fields without schema changes
- ✅ **Multi-tenant**: Store-scoped metafield definitions
- ✅ **Type Safety**: Proper validation and type handling
- ✅ **Generic Relations**: Works with any model
- ✅ **Performance Optimized**: Proper indexing and caching
- ✅ **Flexible Configuration**: UI, validation, and options support

---

**Version**: 1.0
**Last Updated**: 2026-01-26
**Next Review**: 2026-02-25

#### Metafield
```python
# apps/public/metafields/models/fields.py
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from core.models import TenantModel
class Metafield(TenantModel):
    """Stores actual metafield values with generic relations"""
    # Reference to the definition
    definition = models.ForeignKey(
        'metafields.MetafieldDefinition',
        on_delete=models.CASCADE,
        related_name='values'
    )
    # Generic relation to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    # Value storage (type-specific)
    value_text = models.TextField(blank=True, null=True)
    value_number = models.FloatField(blank=True, null=True)
    value_boolean = models.BooleanField(blank=True, null=True)
    value_date = models.DateField(blank=True, null=True)
    value_json = models.JSONField(blank=True, null=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta(TenantModel.Meta):
        db_table = 'metafields_metafield'
        unique_together = [['store', 'definition', 'content_type', 'object_id']]
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
    def __str__(self):
        return f"{self.definition} on {self.content_object}"
```

## 🔧 Implementation
### Core Components
- [ ] `MetafieldDefinition` model
- [ ] `Metafield` model
- [ ] `MetafieldService`
- [ ] API endpoints
### Integration Points
- [ ] User Profiles
- [ ] Products
- [ ] Pages
- [ ] Collections
---

## 🔒 Permissions
### Required Permissions
- `metafields.add_metafielddefinition`
- `metafields.change_metafielddefinition`
- `metafields.view_metafielddefinition`
- `metafields.add_metafield`
- `metafields.change_metafield`
- `metafields.view_metafield`

## 🧪 Testing
### Test Cases

```python
# tests/test_metafields.py
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from apps.products.models import Product
from ..models import MetafieldDefinition, Metafield
class MetafieldTests(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name="Test Store", slug="test-store")
        self.product = Product.objects.create(
            store=self.store,
            name="Test Product",
            sku="TEST-001"
        )
        # Create a test metafield definition
        self.defn = MetafieldDefinition.objects.create(
            store=self.store,
            name="Stock Warning Level",
            namespace="inventory",
            key="stock_warning_level",
            type="number"
        )
    def test_metafield_creation(self):
        """Test creating a metafield"""
        metafield = Metafield.objects.create(
            store=self.store,
            definition=self.defn,
            content_object=self.product,
            value_number=10
        )
        self.assertEqual(metafield.value_number, 10)
        self.assertEqual(metafield.content_object, self.product)
```

## ⚙️ Services
- [ ] API endpoints
### Integration Points
- [ ] User Profiles
- [ ] Products
- [ ] Pages
- [ ] Collections
---

## 🔗 Dependencies
[Dependencies content to be added]

## 📋 Migration
1. Add new metafield tables
2. Create data migration for existing fields
3. Update views to use new metafield system
4. Remove old field columns in subsequent release

## ✅ Benefits
- Use `select_related` and `prefetch_related` when querying metafields
   - Cache frequently accessed metafields

3. **Validation**
   - Always validate metafield values against their definitions
   - Use the provided validation methods in `MetafieldService`

---
**Version**: 1.0
**Last Updated**: 2026-01-26
**Next Review**: 2026-02-25
