# Metafields System v2.0

## 🎯 Purpose

This document defines the architecture and implementation rules for the Metafields system, enabling dynamic custom fields for any model in the CMS-Updated platform.

## 📚 Related Documents
- [Core Architecture](../core.md)
- [Store Management](../stores.md)
- [Content Types](../content-types.md)

## 🔍 Implementation Status

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

## 🏗️ Architecture

### Core Models

#### MetafieldDefinition
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

    class Meta(TenantModel.Meta):
        db_table = 'metafields_definition'
        unique_together = [['store', 'namespace', 'key']]
        ordering = ['namespace', 'key']

    def __str__(self):
        return f"{self.namespace}.{self.key}"

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

## 🔄 Integration Patterns

### 1. Adding Metafields to a Model

```python
# Example: Adding to Product model
from django.contrib.contenttypes.fields import GenericRelation

class Product(TenantModel):
    # ... existing fields ...
    metafields = GenericRelation(
        'metafields.Metafield',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='product'
    )
```

### 2. Using MetafieldService

```python
# Get a metafield value
value = MetafieldService.get_metafield(
    store=store,
    content_object=product,
    namespace='inventory',
    key='stock_warning_level'
)

# Set a metafield value
MetafieldService.set_metafield(
    store=store,
    content_object=product,
    namespace='inventory',
    key='stock_warning_level',
    value=10
)
```

## 🔐 Permissions

### Required Permissions
- `metafields.add_metafielddefinition`
- `metafields.change_metafielddefinition`
- `metafields.view_metafielddefinition`
- `metafields.add_metafield`
- `metafields.change_metafield`
- `metafields.view_metafield`

## 🚀 Best Practices

1. **Namespace Organization**
   - Use consistent namespaces (e.g., 'seo', 'inventory', 'display')
   - Document all namespaces in use

2. **Performance**
   - Use `select_related` and `prefetch_related` when querying metafields
   - Cache frequently accessed metafields

3. **Validation**
   - Always validate metafield values against their definitions
   - Use the provided validation methods in `MetafieldService`

## 🔄 Migration Strategy

1. Add new metafield tables
2. Create data migration for existing fields
3. Update views to use new metafield system
4. Remove old field columns in subsequent release

## 📊 Monitoring

### Key Metrics
- Metafield usage by type
- Query performance
- Storage usage

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

## 📝 Version History

### v2.0 (Current)
- Consolidated metafields documentation
- Added integration patterns and examples
- Improved type safety and validation

### v1.0 (Legacy)
- Initial implementation
        ('post', 'Post'),
        ('product', 'Product'),
        ('collection', 'Collection'),
        ('store', 'Store'),
    ]
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
            models.Index(fields=['content_types'], name='content_types_idx')
        ]

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

#### **Metafield**
```python
# apps/public/metafields/models/values.py
from core.models import TenantModel
from django.db import models

class Metafield(TenantModel):
    """
    Stores actual metafield values with generic relations
    """

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
    content_object = models.GenericForeignKey('content_type', 'object_id')

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
            'store', 'definition', 'content_type', 'object_id'
        ]
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['definition', 'value_text']),
            models.Index(fields=['definition', 'value_number']),
            models.Index(fields=['definition', 'value_boolean']),
        ]

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

## 🛠️ Services Layer

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

    @staticmethod
    def get_metafields_by_namespace(store, namespace):
        """Get all metafield definitions for a namespace"""
        from .models import MetafieldDefinition
        return MetafieldDefinition.objects.filter(
            store=store,
            namespace=namespace
        )

    @staticmethod
    @transaction.atomic
    def bulk_update_metafields(instance, metafield_data):
        """Update multiple metafields for an instance"""
        from .models import Metafield, MetafieldDefinition

        content_type = ContentType.objects.get_for_model(instance)
        updated_metafields = []

        for namespace_key, value in metafield_data.items():
            if '.' not in namespace_key:
                continue

            namespace, key = namespace_key.split('.', 1)

            # Get or create definition
            definition, created = MetafieldDefinition.objects.get_or_create(
                store=instance.store,
                namespace=namespace,
                key=key,
                defaults={
                    'name': f"{namespace}.{key}",
                    'type': MetafieldService._infer_type(value),
                    'content_types': [content_type.model]
                }
            )

            # Get or create metafield
            metafield, created = Metafield.objects.get_or_create(
                definition=definition,
                content_type=content_type,
                object_id=instance.id,
                store=instance.store
            )

            # Set value
            metafield.set_value(value)
            metafield.save()
            updated_metafields.append(metafield)

        return updated_metafields
```

---

## 🌐 API Endpoints

### **MetafieldDefinitionViewSet**
```python
# apps/dashboard/metafields/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema

class MetafieldDefinitionViewSet(TenantViewSet):
    """
    CRUD operations for metafield definitions
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = MetafieldDefinitionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = ['namespace', 'type', 'is_required', 'is_visible']
    search_fields = ['name', 'namespace', 'key']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        return MetafieldDefinition.objects.filter(store=self.request.store)

    @extend_schema(
        summary="List Metafield Definitions",
        description="Get paginated list of metafield definitions"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create Metafield Definition",
        request=MetafieldDefinitionSerializer,
        responses={201: MetafieldDefinitionSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
```

### **MetafieldViewSet**
```python
# apps/dashboard/metafields/v2/views.py
class MetafieldViewSet(TenantViewSet):
    """
    CRUD operations for metafield values
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = MetafieldSerializer

    def get_queryset(self):
        return Metafield.objects.filter(store=self.request.store)

    @extend_schema(
        summary="Get Metafields for Object",
        description="Get all metafields for a specific object"
    )
    @action(detail=False, methods=['get'])
    def for_object(self, request):
        """Get all metafields for a specific object"""
        content_type = request.query_params.get('content_type')
        object_id = request.query_params.get('object_id')

        if not content_type or not object_id:
            return Response(
                {"error": "content_type and object_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        metafields = Metafield.objects.filter(
            store=request.store,
            content_type__model=content_type,
            object_id=object_id
        )

        serializer = self.get_serializer(metafields, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Bulk Update Metafields",
        request=BulkMetafieldSerializer,
        responses={200: MetafieldSerializer(many=True)}
    )
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update metafields for an object"""
        content_type = request.query_params.get('content_type')
        object_id = request.query_params.get('object_id')

        if not content_type or not object_id:
            return Response(
                {"error": "content_type and object_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the object
        content_type_obj = ContentType.objects.get(model=content_type)
        model_class = content_type_obj.model_class()
        instance = model_class.objects.get(id=object_id)

        # Update metafields
        metafields = MetafieldService.bulk_update_metafields(
            instance, request.data
        )

        serializer = self.get_serializer(metafields, many=True)
        return Response(serializer.data)
```

---

## 🔄 Usage Examples

### **Adding Metafields to Models**
```python
# apps/public/users/models.py
from django.db import models
from core.models import TenantModel

class UserProfile(TenantModel):
    """Example model with metafields support"""

    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE)
    bio = models.TextField(blank=True)

    # Metafields property
    @property
    def metafields(self):
        """Access metafields as attributes"""
        from metafields.services import MetafieldService
        return MetafieldService.get_metafields_for_object(self)

    def get_metafield(self, namespace, key):
        """Get a specific metafield"""
        from metafields.services import MetafieldService
        try:
            definition = MetafieldService.get_metafield_definition(
                self.store, namespace, key
            )
            return MetafieldService.get_metafield(self, definition)
        except:
            return None

    def set_metafield(self, namespace, key, value):
        """Set a metafield value"""
        from metafields.services import MetafieldService
        return MetafieldService.set_metafield(self, namespace, key, value)

    def get_all_metafields(self):
        """Get all metafields as a dictionary"""
        metafields = {}
        for metafield in self.metafields:
            key = f"{metafield.definition.namespace}.{metafield.definition.key}"
            metafields[key] = metafield.get_value()
        return metafields
```

### **Using Metafields in Views**
```python
# Example: Setting metafields
profile = UserProfile.objects.first()
profile.set_metafield("social", "twitter_handle", "@example")
profile.set_metafield("social", "website_url", "https://example.com")
profile.set_metafield("preferences", "theme_color", "#FF5722")

# Example: Getting metafields
handle = profile.get_metafield("social", "twitter_handle")
print(handle.get_value())  # Output: @example

# Example: Getting all metafields
all_metafields = profile.get_all_metafields()
print(all_metafields)
# Output: {
#   "social.twitter_handle": "@example",
#   "social.website_url": "https://example.com",
#   "preferences.theme_color": "#FF5722"
# }
```

### **Frontend Integration**
```javascript
// Example JavaScript for metafield management
async function updateMetafields(objectType, objectId, metafields) {
    try {
        const response = await fetch(
            `/v2/api/dashboard/metafields/bulk_update/?content_type=${objectType}&object_id=${objectId}`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(metafields)
            }
        );

        const result = await response.json();
        return result;

    } catch (error) {
        console.error('Error updating metafields:', error);
    }
}

// Usage
updateMetafields('user', 123, {
    'social.twitter_handle': '@newhandle',
    'preferences.theme_color': '#2196F3'
});
```

---

## 🛡️ Security & Permissions

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

## 🚀 Performance Considerations

### **Indexing**
- All foreign keys are indexed
- Common query patterns are optimized with indexes
- JSON fields use GIN indexes for efficient querying

### **Caching**
- Metafield definitions are cached per store
- Object metafields are cached for the request duration

### **Batch Operations**
- Bulk create/update operations are supported
- Efficient querying with `select_related` and `prefetch_related`

---

## 📊 Database Schema

### **metafields_definition**
```sql
CREATE TABLE metafields_definition (
    id SERIAL PRIMARY KEY,
    store_id INTEGER REFERENCES stores_store(id),
    namespace VARCHAR(50) NOT NULL,
    key VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL,
    is_required BOOLEAN DEFAULT false,
    is_visible BOOLEAN DEFAULT true,
    options JSONB DEFAULT '[]'::jsonb,
    validations JSONB DEFAULT '{}'::jsonb,
    content_types JSONB DEFAULT '[]'::jsonb,
    ui JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(store_id, namespace, key)
);

CREATE INDEX idx_metafields_definition_store ON metafields_definition(store_id);
CREATE INDEX idx_metafields_definition_lookup ON metafields_definition(namespace, key);
CREATE INDEX idx_metafields_definition_visible ON metafields_definition(is_visible);
```

### **metafields_value**
```sql
CREATE TABLE metafields_value (
    id SERIAL PRIMARY KEY,
    store_id INTEGER REFERENCES stores_store(id),
    definition_id INTEGER REFERENCES metafields_definition(id),
    content_type_id INTEGER REFERENCES django_content_type(id),
    object_id INTEGER NOT NULL,
    value_text TEXT,
    value_number DOUBLE PRECISION,
    value_boolean BOOLEAN,
    value_date TIMESTAMPTZ,
    value_json JSONB,
    value_media_id INTEGER REFERENCES media_mediafile(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(store_id, definition_id, content_type_id, object_id)
);

CREATE INDEX idx_metafields_value_lookup ON metafields_value(content_type_id, object_id);
CREATE INDEX idx_metafields_value_definition ON metafields_value(definition_id);
CREATE INDEX idx_metafields_value_text ON metafields_value USING GIN (value_text gin_trgm_ops);
CREATE INDEX idx_metafields_value_number ON metafields_value(value_number);
CREATE INDEX idx_metafields_value_boolean ON metafields_value(value_boolean);
```

---

## 📝 Implementation Checklist

### **Core Features**
- [x] Metafield definitions with types and validation
- [x] Generic foreign key to any model
- [x] Store-scoped metafields
- [x] Type-safe value storage
- [x] Bulk operations support
- [x] Media integration for image/file types

### **API Endpoints**
- [x] CRUD for metafield definitions
- [x] CRUD for metafield values
- [x] Filtering and searching
- [x] Bulk operations
- [x] Object-specific metafield retrieval

### **Security**
- [x] Store isolation
- [x] Permission checks
- [x] Input validation
- [x] Rate limiting

### **Performance**
- [x] Proper indexing
- [x] Query optimization
- [x] Caching layer
- [x] Batch operations

### **Documentation**
- [x] API documentation
- [x] Usage examples
- [x] Database schema
- [x] Security considerations
