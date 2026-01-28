# Accounts App Rules v1.0

## 🎯 Purpose

This document defines strict development rules for the **accounts** app in CMS-Updated backend, maintaining DFCMS compatibility while implementing the recommended single database + store-scoped multi-tenant approach.

---

## 🏗️ Accounts App Structure

### **Fixed Directory Structure**
```
apps/
├── public/                    # Public APIs (no authentication)
│   └── accounts/             # Public account APIs (registration, etc.)
│       ├── v2/               # Version 2 (Current Only)
│       │   ├── urls.py
│       │   ├── views.py
│       │   ├── serializers.py
│       │   ├── services.py
│       │   └── tests.py
│       ├── models/             # Shared models across versions
│       │   ├── __init__.py
│       │   ├── user.py
│       │   ├── role.py
│       │   └── preferences.py
│       ├── admin.py
│       ├── apps.py
│       └── migrations/
├── customer/                  # Customer APIs (customer authentication)
│   └── accounts/             # Customer account management
│       ├── v2/               # Version 2 (Current Only)
│       │   ├── urls.py
│       │   ├── views.py
│       │   ├── serializers.py
│       │   ├── services.py
│       │   └── tests.py
│       └── models/             # Same shared models
└── dashboard/                 # Dashboard APIs (admin authentication)
    └── accounts/             # Dashboard account management
        ├── v2/               # Version 2 (Current Only)
        │   ├── urls.py
        │   ├── views.py
        │   ├── serializers.py
        │   ├── services.py
        │   └── tests.py
        └── models/             # Same shared models
```

---

## 👤 User Model Rules (Global + Store-Scoped)

### **1. Global User Model**
```python
# apps/accounts/models/user.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class GlobalUserManager(BaseUserManager):
    """Global user manager - users exist across all stores"""

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not username:
            raise ValueError("The Username field must be set")

        email = self.normalize_email(email)

        # Check global uniqueness
        if self.model.objects.filter(email=email).exists():
            raise ValueError(f"User with email '{email}' already exists")
        if self.model.objects.filter(username=username).exists():
            raise ValueError(f"User with username '{username}' already exists")

        user = self.model(
            email=email,
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """Global user model - exists across all stores"""
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    # Global fields (no store)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = GlobalUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'accounts_user'

### **2. Store User Model**
```python
# apps/accounts/models/store_user.py
from django.db import models
from django.contrib.auth import get_user_model
from .user import User

User = get_user_model()

class StoreUser(models.Model):
    """Store-specific user roles and permissions"""
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('customer', 'Customer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='store_users')
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='store_users')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['user', 'store']]
        indexes = [
            models.Index(fields=['store', 'role']),
            models.Index(fields=['user', 'role']),
        ]
        db_table = 'accounts_store_user'
```

---

## 📁 Directory Structure Update

**Important**: Update the directory structure to use the simplified approach:

```yaml
backend/
├── apps/
│   ├── accounts/
│   │   ├── v2/
│   │   │   ├── urls.py
│   │   │   ├── views.py
│   │   │   ├── serializers.py
│   │   │   ├── services.py
│   │   │   └── tests.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   └── store_user.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── migrations/
│   └── [other apps]/
├── core/
└── services/
```

---

## 🔑 Authentication Rules

### **1. JWT Configuration**
- Use `rest_framework_simplejwt` for token authentication
- Access token: 60 minutes
- Refresh token: 7 days
- Rotate refresh tokens on use

### **2. Store Context**
- All API endpoints must validate store context
- Use `request.store` from middleware
- Filter all queries by store

---

## 📋 Implementation Checklist

### **Phase 1: Core Models**
- [ ] Create global User model
- [ ] Create StoreUser model
- [ ] Update authentication backend
- [ ] Create migrations

### **Phase 2: API Endpoints**
- [ ] Public registration/login
- [ ] Customer authentication
- [ ] Dashboard authentication
- [ ] Store user management

### **Phase 3: Permissions**
- [ ] Store-scoped permissions
- [ ] Role-based access control
- [ ] API permission classes

---

## 🚀 Migration from DFCMS

### **User Migration**
```python
# DFCMS GlobalUser → CMS-Updated User
# DFCMS StoreUser → CMS-Updated StoreUser (with explicit store FK)
```

### **Authentication Migration**
- Keep same JWT settings
- Update token claims to include store_id
- Maintain backward compatibility

---

Last Updated: January 23, 2026

    return Response({
        'error': 'Validation failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStoreUser])
@extend_schema(
    summary="User Logout",
    description="Logout user and invalidate token",
    responses={200: dict}
)
def logout(request):
    """User logout - Django REST Framework"""
    try:
        # Get refresh token from request
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        return Response({
            'message': 'Successfully logged out'
        })
    except Exception:
        return Response({
            'message': 'Logout successful'
        })
```

### **2. REST API ViewSets for User Management**
```python
# apps/dashboard/accounts/v2/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from core.permissions import IsStoreOwner, IsStoreStaff
from core.viewsets import TenantViewSet
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer

class UserViewSet(TenantViewSet):
    """
    User Management API - Django REST Framework
    Store-scoped user management for dashboard
    """

    permission_classes = [IsAuthenticated, IsStoreStaff]
    filterset_fields = ['is_active', 'role', 'is_store_owner']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'email', 'last_login']
    ordering = ['-created_at']

    @extend_schema(
        summary="List Users",
        description="Get paginated list of store users",
        responses={200: UserSerializer}
    )
    def list(self, request, *args, **kwargs):
        """List users with filtering and search"""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create User",
        description="Create new user in store",
        request=UserCreateSerializer,
        responses={201: UserSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Create user with automatic store assignment"""
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Update User",
        description="Update user details",
        request=UserUpdateSerializer,
        responses={200: UserSerializer}
    )
    def update(self, request, *args, **kwargs):
        """Update user with validation"""
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Deactivate User",
        description="Deactivate user account",
        responses={200: dict}
    )
    def deactivate(self, request, pk=None):
        """Deactivate user"""
        user = self.get_object()
        if user.is_store_owner:
            return Response({
                'error': 'Cannot deactivate store owner',
                'code': 'CANNOT_DEACTIVATE_OWNER'
            }, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = False
        user.save(update_fields=['is_active'])

        return Response({
            'message': f'User {user.email} deactivated successfully'
        })

    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Change User Role",
        description="Update user role and permissions",
        request=RoleUpdateSerializer,
        responses={200: dict}
    )
    def change_role(self, request, pk=None):
        """Change user role"""
        user = self.get_object()
        if user.is_store_owner:
            return Response({
                'error': 'Cannot change store owner role',
                'code': 'CANNOT_CHANGE_OWNER_ROLE'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = RoleUpdateSerializer(data=request.data)
        if serializer.is_valid():
            from services.user import UserService
            UserService.update_user_role(user, serializer.validated_data['role'])

            return Response({
                'message': f'User {user.email} role updated successfully',
                'new_role': user.role.name
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

### **3. REST API Profile Management**
```python
# apps/customer/accounts/v2/views.py
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from core.permissions import IsStoreUser
from core.viewsets import TenantViewSet

class ProfileView(generics.RetrieveUpdateAPIView):
    """
    User Profile API - Django REST Framework
    Customer profile management
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = UserProfileSerializer

    def get_object(self):
        """Return current user profile"""
        return self.request.user

    @extend_schema(
        summary="Get User Profile",
        description="Get current user profile information",
        responses={200: UserProfileSerializer}
    )
    def get(self, request, *args, **kwargs):
        """Get user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary="Update User Profile",
        description="Update current user profile",
        request=UserProfileUpdateSerializer,
        responses={200: UserProfileSerializer}
    )
    def patch(self, request, *args, **kwargs):
        """Update user profile"""
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(generics.GenericAPIView):
    """
    Password Change API - Django REST Framework
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = PasswordChangeSerializer

    @extend_schema(
        summary="Change Password",
        description="Change user password",
        request=PasswordChangeSerializer,
        responses={200: dict, 400: dict}
    )
    def post(self, request, *args, **kwargs):
        """Change user password"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            # Verify current password
            if not user.check_password(serializer.validated_data['current_password']):
                return Response({
                    'error': 'Current password is incorrect',
                    'code': 'INVALID_CURRENT_PASSWORD'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save(update_fields=['password'])

            return Response({
                'message': 'Password changed successfully'
            })


### **1. Authentication Service**
```python
# services/auth.py (SHARED across all versions)
from django.contrib.auth import login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """Shared authentication service"""

    @staticmethod
    def generate_token(user):
        """Generate JWT token for user"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @staticmethod
    def verify_token(token):
        """Verify JWT token"""
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token)
            return access_token.payload
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None

    @staticmethod
    def send_password_reset_email(user, store):
        """Send password reset email"""
        from services.email import EmailService
        token = AuthService.generate_reset_token(user)
        EmailService.send_password_reset_email(user, store, token)

    @staticmethod
    def generate_reset_token(user):
        """Generate password reset token"""
        from django.utils.crypto import get_random_string
        return get_random_string(64)
```

### **2. User Service**
```python
# services/user.py (SHARED across all versions)
from django.core.exceptions import ValidationError
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Shared user management service"""

    @staticmethod
    def create_user_store_owner(store, email, username, password):
        """Create store owner user"""
        with transaction.atomic():
            # Create owner role for store
            from apps.public.accounts.models import Role
            owner_role = Role.objects.create(
                store=store,
                name='Store Owner',
                slug='store-owner',
                description='Full access to store',
                can_manage_products=True,
                can_manage_orders=True,
                can_manage_customers=True,
                can_manage_settings=True,
                can_view_analytics=True,
                level=100
            )

            # Create owner user
            from apps.public.accounts.models import User
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password,
                store=store,
                is_store_owner=True,
                is_verified=True,  # Auto-verify store owners
                role=owner_role
            )

            # Update store owner
            store.owner = user
            store.save()

            return user

    @staticmethod
    def update_user_role(user, new_role):
        """Update user role with permission validation"""
        if user.is_store_owner:
            raise ValidationError("Cannot change store owner role")

        user.role = new_role
        user.save(update_fields=['role'])

        logger.info(f"Updated user {user.email} role to {new_role.name}")

    @staticmethod
    def deactivate_user(user):
        """Safely deactivate user"""
        user.is_active = False
        user.save(update_fields=['is_active'])

        logger.info(f"Deactivated user {user.email}")
```

---

## 🔒 Permission Rules

### **1. Store-Scoped Permissions**
```python
# core/permissions.py
from rest_framework.permissions import BasePermission

class IsStoreOwner(BasePermission):
    """Allow access only to store owners"""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'store') and
            request.user.is_store_owner
        )

class IsStoreStaff(BasePermission):
    """Allow access to store staff (owners + staff users)"""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'store') and
            (request.user.is_store_owner or request.user.is_staff)
        )

class IsStoreUser(BasePermission):
    """Allow access to any authenticated store user"""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'store')
        )

class HasStorePermission(BasePermission):
    """Check specific store permissions"""

    def __init__(self, permission_field):
        self.permission_field = permission_field

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        # Check if user has required permission via role
        if hasattr(request.user, 'role') and request.user.role:
            return getattr(request.user.role, self.permission_field, False)

        return False
```

---

## 📡 URL Structure Rules

### **1. Public Account URLs**
```python
# apps/public/accounts/v2/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RegisterView, LoginView, LogoutView,
    PasswordResetView, PasswordResetConfirmView,
    EmailVerificationView
)

router = DefaultRouter()
# No ViewSet registration for auth endpoints - use API views

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('verify-email/', EmailVerificationView.as_view(), name='verify-email'),
]

# Main app URLs
# apps/public/accounts/urls.py
from django.urls import include, path

app_name = 'accounts'

urlpatterns = [
    path('v2/', include('apps.public.accounts.v2.urls')),
]
```

### **2. Customer Account URLs**
```python
# apps/customer/accounts/v2/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProfileView, ChangePasswordView,
    UpdateProfileView, DeleteAccountView
)

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='customer-profile')

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('update-profile/', UpdateProfileView.as_view(), name='update-profile'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
]

# Main app URLs
# apps/customer/accounts/urls.py
from django.urls import include, path

app_name = 'customer_accounts'

urlpatterns = [
    path('v2/', include('apps.customer.accounts.v2.urls')),
]
```

### **3. Dashboard Account URLs**
```python
# apps/dashboard/accounts/v2/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import UserViewSet, RoleViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='dashboard-users')
router.register(r'roles', RoleViewSet, basename='dashboard-roles')

# Nested routes for user management
users_router = routers.NestedDefaultRouter(router, r'users', lookup='user')
users_router.register(r'activity', UserActivityViewSet, basename='user-activity')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(users_router.urls)),
]

# Main app URLs
# apps/dashboard/accounts/urls.py
from django.urls import include, path

app_name = 'dashboard_accounts'

urlpatterns = [
    path('v2/', include('apps.dashboard.accounts.v2.urls')),
]
```

### **4. Main Project URLs**
```python
# config/urls.py
from django.urls import path, include

urlpatterns = [
    # Public account APIs
    path('v2/api/public/accounts/', include('apps.public.accounts.urls')),

    # Customer account APIs
    path('v2/api/customer/accounts/', include('apps.customer.accounts.urls')),

    # Dashboard account APIs
    path('v2/api/dashboard/accounts/', include('apps.dashboard.accounts.urls')),

    # Other workspace APIs...
]
```

---

## 🧪 Testing Rules

### **1. Model Tests**
```python
# apps/public/accounts/tests/test_models.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from ..models import User, Role

class UserModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', slug='test-store')

    def test_create_user(self):
        """Test user creation with store context"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            store=self.store
        )

        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.store, self.store)
        self.assertTrue(user.check_password('testpass123'))

    def test_email_unique_per_store(self):
        """Test email uniqueness within store"""
        User.objects.create_user(
            email='test@example.com',
            username='user1',
            password='pass123',
            store=self.store
        )

        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='test@example.com',
                username='user2',
                password='pass123',
                store=self.store
            )

    def test_same_email_different_store(self):
        """Test same email can exist in different stores"""
        store2 = Store.objects.create(name='Store 2', slug='store-2')

        user1 = User.objects.create_user(
            email='test@example.com',
            username='user1',
            password='pass123',
            store=self.store
        )

        user2 = User.objects.create_user(
            email='test@example.com',
            username='user2',
            password='pass123',
            store=store2
        )

        self.assertNotEqual(user1.store, user2.store)
        self.assertEqual(user1.email, user2.email)
```

---

## 📋 Migration Rules

### **1. DFCMS Compatibility Migration**
```python
# apps/public/accounts/migrations/0002_migrate_dfcms_users.py
from django.db import migrations

def migrate_global_users(apps, schema_editor):
    """Migrate DFCMS GlobalUser to new User model"""
    GlobalUser = apps.get_model('modules', 'GlobalUser')
    Store = apps.get_model('modules', 'Store')
    User = apps.get_model('public_accounts', 'User')

    for global_user in GlobalUser.objects.all():
        # Create user for each store they belong to
        for store in global_user.stores.all():
            User.objects.create(
                email=global_user.email,
                username=global_user.username,
                first_name=global_user.first_name,
                last_name=global_user.last_name,
                is_verified=global_user.is_verified,
                is_active=global_user.is_active,
                is_staff=global_user.is_staff,
                is_superuser=global_user.is_superuser,
                store=store,
                is_store_owner=(store.owner == global_user),
                created_at=global_user.date_joined,
            )

def migrate_store_users(apps, schema_editor):
    """Migrate DFCMS UserAccount to new User model"""
    UserAccount = apps.get_model('modules', 'UserAccount')
    Store = apps.get_model('modules', 'Store')
    User = apps.get_model('public_accounts', 'User')

    for store_user in UserAccount.objects.all():
        # Map to new user model
        User.objects.create(
            email=store_user.email,
            username=store_user.username,
            first_name=store_user.first_name,
            last_name=store_user.last_name,
            is_verified=store_user.is_verified,
            is_active=store_user.is_active,
            is_staff=store_user.is_staff,
            store=store_user.store,
            created_at=store_user.date_joined,
        )

class Migration(migrations.Migration):
    dependencies = [
        ('public_accounts', '0001_initial'),
        ('modules', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_global_users),
        migrations.RunPython(migrate_store_users),
    ]
```

---

## 🎯 Key Benefits of This Approach

### **✅ Complete Store Isolation**
- Same email can exist in different stores
- Users belong to specific stores only
- No cross-store data leakage

### **✅ DFCMS Compatibility**
- Maintains all existing fields and logic
- Smooth migration path
- Preserves user experience

### **✅ Simple Implementation**
- Single database
- Standard Django auth
- Clear separation of concerns

### **✅ Scalable Architecture**
- Works for thousands of stores
- Easy to add new features
- Professional multi-tenancy

---

**🚨 THESE RULES ARE MANDATORY - NO EXCEPTIONS!**

Every accounts app development must follow these rules exactly. Any deviation will result in inconsistent user management and potential security issues.

**Version: 1.0**
**Last Updated: 2024-01-22**
**Next Review: 2024-02-22**
