---
trigger: always_on
---
# Django App Migration Guide: Global to Internal Layered Structure

## Overview
This guide documents the migration process from global layered folders (`apps/public/[app]/v2/`, `apps/customer/[app]/v2/`, `apps/dashboard/[app]/v2/`) to internal layered structure (`apps/[app]/v2/`).

## Migration Rules

### 1. URL Structure Updates

#### Before (Global Layered)
```python
# apps/[app]/urls.py
urlpatterns = [
    path('public/', include('apps.[app].public.v2.urls')),
    path('customer/', include('apps.[app].customer.v2.urls')),
    path('dashboard/', include('apps.[app].dashboard.v2.urls')),
]
```

#### After (Internal Layered)
```python
# apps/[app]/urls.py
urlpatterns = [
    path('v2/', include('apps.[app].v2.urls')),
]
```

### 2. Import Path Corrections

#### Models
```python
# Before
from apps.forms.models.forms import FormTemplate, EmailTemplate

# After
from apps.forms.models.forms import FormTemplate
from apps.forms.models.submissions import FormSubmission
```

#### Permissions
```python
# Before
from core.permissions import IsStoreCustomer

# After
from core.permissions import IsStoreUser
```

#### Services
```python
# Before
from apps.accounts.services.customer_service import CustomerAccountService

# After
from apps.accounts.services.account_service import CustomerAccountService
```

### 3. ViewSet vs GenericAPIView

#### Convert GenericAPIView to ViewSet when using routers
```python
# Before
class CustomerUserViewSet(generics.RetrieveUpdateAPIView):
    def get(self, request, *args, **kwargs):
        ...

# After
class CustomerUserViewSet(viewsets.GenericViewSet):
    def retrieve(self, request, *args, **kwargs):
        ...
```

### 4. Serializer Patterns

#### Base Serializers
Create base serializers in app root when needed:
```python
# apps/notifications/serializers.py
class BaseNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'user', 'title', 'message', 'type', 'is_read']
```

#### Context-specific Serializers
```python
# apps/[app]/v2/serializers/public.py
class ProductPublicSerializer(BaseProductSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
```

### 5. Missing Files Creation

#### Create missing URLs
```python
# apps/entities/public/v2/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

public_router = DefaultRouter()
urlpatterns = [
    path('', include(public_router.urls)),
]
```

#### Create missing serializers
```python
# apps/[app]/v2/serializers/public.py
from rest_framework import serializers
from apps.[app].models import ModelName

class ModelPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelName
        fields = ['id', 'name', 'created_at']
```

#### Create missing services
```python
# apps/[app]/services/[service_name].py
class ServiceName:
    @staticmethod
    def method_name():
        pass
```

## App-Specific Migration Trees

### accounts App
```
apps/accounts/
├── urls.py                          # Updated to v2/ structure
├── v2/
│   ├── urls.py                      # Direct path for CustomerLoginView
│   ├── views/
│   │   ├── public.py                # Created CustomerLoginView
│   │   ├── customer.py              # Converted to ViewSet
│   │   └── dashboard.py             # Fixed imports
│   └── serializers/
│       ├── public.py                # Created UserSerializer
│       ├── customer.py              # Created UserSerializer, etc.
│       └── dashboard.py             # Fixed imports
└── services/
    └── account_service.py          # Added missing service classes
```

**Issues Fixed:**
- `IsStoreCustomer` → `IsStoreUser`
- `CustomerLoginView` moved to public.py
- ViewSet conversion for router compatibility
- Missing service classes added

### ecommerce App
```
apps/ecommerce/
├── urls.py                          # Updated to v2/ structure
├── v2/
│   ├── urls.py                      # Public/Customer/Dashboard routers
│   ├── views/
│   │   ├── public.py                # Fixed filters import, removed test code
│   │   ├── customer.py              # Created
│   │   └── dashboard.py             # Fixed Q import, syntax error
│   └── serializers/
│       ├── public.py                # Created
│       ├── customer.py              # Created
│       └── dashboard.py             # May need creation
└── services/
    └── ecommerce_service.py        # Created
```

**Issues Fixed:**
- Missing `filters` import
- Test code removed from views
- `Q` import fixed
- Missing serializers created

### forms App
```
apps/forms/
├── urls.py                          # Updated to v2/ structure
├── v2/
│   ├── urls.py                      # Removed EmailTemplate routers
│   ├── views/
│   │   ├── customer.py              # Fixed imports, removed EmailTemplate
│   │   └── dashboard.py             # Fixed imports
│   └── serializers/
│       ├── public.py                # (may need creation)
│       ├── customer.py              # Fixed STATUS_CHOICES, removed EmailTemplate
│       └── dashboard.py             # Fixed imports
```

**Issues Fixed:**
- `EmailTemplate` references removed (model doesn't exist)
- `FormTemplate.STATUS_CHOICES` → inline choices
- `FormSubmission` import path corrected
- Serializer name mismatches fixed

### stores App
```
apps/stores/
├── urls.py                          # Updated to v2/ structure
├── v2/
│   ├── urls.py                      # Public/Customer/Dashboard routers
│   ├── views/
│   │   ├── public.py                # Fixed action decorator import
│   │   ├── customer.py              # (may need creation)
│   │   └── dashboard.py             # (may need creation)
│   └── serializers/
│       ├── public.py                # (may need creation)
│       ├── customer.py              # (may need creation)
│       └── dashboard.py             # (may need creation)
└── services/
    └── store_service.py             # Fixed syntax error (missing quote)
```

**Issues Fixed:**
- Missing `action` import
- Syntax error in store_service.py

### notifications App
```
apps/notifications/
├── urls.py                          # Updated to v2/dashboard/ structure
├── v2/                              # (doesn't exist)
├── dashboard/
│   └── v2/
│       ├── urls.py                   # Existing
│       ├── views.py                 # Fixed NotificationSerializer reference
│       └── serializers.py           # Fixed imports
└── serializers.py                    # Created base serializers
```

**Issues Fixed:**
- URL structure adapted to existing folders
- Base serializers created
- Serializer reference fixed

### entities App
```
apps/entities/
├── urls.py                          # Updated to public/v2/ structure
└── public/
    └── v2/
        └── urls.py                   # Created
```

**Issues Fixed:**
- Created missing URLs file
- Adapted to existing folder structure

## Common Patterns

### 1. Permission Classes
- `IsStoreCustomer` → `IsStoreUser`
- `IsStoreAdmin` (exists)
- `IsStoreOwner` (exists)
- `AllowAny` (for public endpoints)

### 2. Model Import Patterns
- Split imports when models are in different files
- Check actual model locations before importing

### 3. Serializer Patterns
- Create base serializers in app root
- Context-specific serializers in v2/serializers/
- Remove references to non-existent models

### 4. View Patterns
- Convert `GenericAPIView` to `ViewSet` for routers
- Add `@action` decorator for custom actions
- Remove `@action` from standard methods like `create`

### 5. URL Patterns
- Use `v2/` prefix consistently
- Direct path for non-ViewSet views
- Router registration for ViewSets

## Validation Checklist

### Before Running Tests
1. [ ] All URL imports updated to internal structure
2. [ ] Model imports corrected
3. [ ] Permission imports corrected
4. [ ] Missing files created (urls, serializers, services)
5. [ ] Syntax errors fixed
6. [ ] ViewSet vs GenericAPIView consistency
7. [ ] Test code removed from production files

### After Migration
1. [ ] Run `python manage.py test --verbosity=1`
2. [ ] Fix any remaining import errors
3. [ ] Update STATUS.md with progress
4. [ ] Document any remaining issues

## Troubleshooting

### Common Errors
1. **ModuleNotFoundError**: Check if file exists and import path is correct
2. **NameError**: Add missing imports (filters, action, TestCase)
3. **SyntaxError**: Check for unmatched parentheses, missing quotes
4. **AttributeError**: Verify model attributes and serializer fields
5. **ImproperlyConfigured**: Remove @action from standard ViewSet methods

### Debug Steps
1. Check error traceback for exact file and line
2. Verify file exists at expected location
3. Check import statements
4. Verify class/method names match
5. Run check_urls.py to verify URL structure

## Notes
- Not all apps have complete v2/ structure
- Some apps only have public/ or dashboard/ subfolders
- Adapt URL structure to what actually exists
- Create minimal implementations for missing files
- Remove references to non-existent models/features
