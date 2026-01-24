"""
Test suite for accounts services.
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from unittest.mock import patch

User = get_user_model()


class TestUserService(TestCase):
    """Test UserService methods"""
    
    def setUp(self):
        """Set up test data"""
        from core.services.user import UserService
        self.user = UserService.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        from apps.stores.models import Store
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store',
            owner=self.user
        )
    
    def test_create_user(self):
        """Test user creation"""
        from core.services.user import UserService
        
        user = UserService.create_user(
            email='new@example.com',
            username='newuser',
            password='newpass123'
        )
        
        self.assertEqual(user.email, 'new@example.com')
        self.assertEqual(user.username, 'newuser')
        self.assertTrue(user.check_password('newpass123'))
    
    def test_create_user_without_username(self):
        """Test user creation without username"""
        from core.services.user import UserService
        
        user = UserService.create_user(
            email='auto@example.com',
            password='autopass123'
        )
        
        self.assertEqual(user.username, 'auto')  # Generated from email
    
    def test_get_user_by_email(self):
        """Test getting user by email"""
        from core.services.user import UserService
        
        user = UserService.get_user(email='test@example.com')
        self.assertEqual(user.id, self.user.id)
    
    def test_get_user_by_id(self):
        """Test getting user by ID"""
        from core.services.user import UserService
        
        user = UserService.get_user(user_id=self.user.id)
        self.assertEqual(user.email, 'test@example.com')
    
    def test_get_user_or_none(self):
        """Test getting user safely"""
        from core.services.user import UserService
        
        # Existing user
        user = UserService.get_user_or_none(email='test@example.com')
        self.assertIsNotNone(user)
        
        # Non-existing user
        user = UserService.get_user_or_none(email='nonexistent@example.com')
        self.assertIsNone(user)
    
    def test_update_user(self):
        """Test updating user"""
        from core.services.user import UserService
        
        UserService.update_user(
            self.user,
            first_name='John',
            last_name='Doe'
        )
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
    
    def test_delete_user(self):
        """Test deleting user"""
        from core.services.user import UserService
        
        user_id = self.user.id
        UserService.delete_user(self.user)
        
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=user_id)
    
    def test_filter_users(self):
        """Test filtering users"""
        from core.services.user import UserService
        
        # Create another user
        user2 = UserService.create_user(
            email='test2@example.com',
            username='testuser2',
            password='testpass123'
        )
        
        users = UserService.filter_users(is_active=True)
        self.assertEqual(users.count(), 2)
        
        users = UserService.filter_users(email='test@example.com')
        self.assertEqual(users.count(), 1)
    
    def test_add_user_to_store(self):
        """Test adding user to store"""
        from core.services.user import UserService
        
        new_user = UserService.create_user(
            email='customer@example.com',
            username='customer',
            password='pass123'
        )
        
        store_user = UserService.add_user_to_store(
            new_user, 
            self.store, 
            role='customer'
        )
        
        self.assertEqual(store_user.user, new_user)
        self.assertEqual(store_user.store, self.store)
        self.assertEqual(store_user.role, 'customer')
        self.assertTrue(store_user.is_active)
    
    def test_get_store_user(self):
        """Test getting store user"""
        from core.services.user import UserService
        
        store_user = UserService.get_store_user(self.user, self.store)
        self.assertIsNotNone(store_user)
        self.assertEqual(store_user.role, 'owner')
    
    def test_update_store_user_role(self):
        """Test updating store user role"""
        from core.services.user import UserService
        
        # Create a customer user
        customer = UserService.create_user(
            email='customer@example.com',
            username='customer',
            password='pass123'
        )
        store_user = UserService.add_user_to_store(customer, self.store, 'customer')
        
        # Update role
        UserService.update_store_user_role(customer, self.store, 'staff')
        
        store_user.refresh_from_db()
        self.assertEqual(store_user.role, 'staff')
    
    def test_cannot_change_owner_role(self):
        """Test that owner role cannot be changed"""
        from core.services.user import UserService
        
        with self.assertRaises(ValidationError) as context:
            UserService.update_store_user_role(self.user, self.store, 'admin')
        
        self.assertIn("Cannot change store owner role", str(context.exception))
    
    def test_deactivate_store_user(self):
        """Test deactivating store user"""
        from core.services.user import UserService
        
        # Create a customer user
        customer = UserService.create_user(
            email='customer@example.com',
            username='customer',
            password='pass123'
        )
        store_user = UserService.add_user_to_store(customer, self.store, 'customer')
        
        # Deactivate
        UserService.deactivate_store_user(customer, self.store)
        
        store_user.refresh_from_db()
        self.assertFalse(store_user.is_active)
    
    def test_cannot_deactivate_owner(self):
        """Test that owner cannot be deactivated"""
        from core.services.user import UserService
        
        with self.assertRaises(ValidationError) as context:
            UserService.deactivate_store_user(self.user, self.store)
        
        self.assertIn("Cannot deactivate store owner", str(context.exception))
    
    def test_get_store_users_by_role(self):
        """Test getting store users by role"""
        from core.services.user import UserService
        
        # Create users with different roles
        admin = UserService.create_user(
            email='admin@example.com',
            username='admin',
            password='pass123'
        )
        UserService.add_user_to_store(admin, self.store, 'admin')
        
        customer = UserService.create_user(
            email='customer2@example.com',
            username='customer2',
            password='pass123'
        )
        UserService.add_user_to_store(customer, self.store, 'customer')
        
        # Get owners
        owners = UserService.get_store_owners(self.store)
        self.assertEqual(owners.count(), 1)
        self.assertEqual(owners.first().user, self.user)
        
        # Get customers
        customers = UserService.get_store_customers(self.store)
        self.assertEqual(customers.count(), 1)
        self.assertEqual(customers.first().user, customer)
        
        # Get staff
        staff = UserService.get_store_staff(self.store)
        self.assertEqual(staff.count(), 2)  # owner + admin


class TestAuthService(TestCase):
    """Test AuthService methods"""
    
    def setUp(self):
        """Set up test data"""
        from core.services.user import UserService
        self.user = UserService.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_generate_tokens(self):
        """Test JWT token generation"""
        from apps.accounts.v2.services import AuthService
        
        tokens = AuthService.generate_token(self.user)
        
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        self.assertIsInstance(tokens['access'], str)
        self.assertIsInstance(tokens['refresh'], str)
    
    def test_verify_token(self):
        """Test JWT token verification"""
        from apps.accounts.v2.services import AuthService
        
        # Generate token
        tokens = AuthService.generate_token(self.user)
        
        # Verify token
        payload = AuthService.verify_token(tokens['access'])
        
        self.assertIsNotNone(payload)
        self.assertEqual(payload['user_id'], self.user.id)
    
    def test_verify_invalid_token(self):
        """Test verification of invalid token"""
        from apps.accounts.v2.services import AuthService
        
        payload = AuthService.verify_token('invalid_token')
        self.assertIsNone(payload)
    
    def test_generate_reset_token(self):
        """Test password reset token generation"""
        from apps.accounts.v2.services import AuthService
        
        token = AuthService.generate_reset_token(self.user)
        
        self.assertIsInstance(token, str)
        self.assertEqual(len(token), 64)  # 64 characters as specified


class TestPublicAuthService(TestCase):
    """Test PublicAuthService methods"""
    
    def setUp(self):
        """Set up test data"""
        from core.services.user import UserService
        self.user = UserService.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        from apps.stores.models import Store
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store',
            owner=self.user
        )
    
    def test_register_user(self):
        """Test user registration"""
        from apps.public.accounts.v2.services import PublicAuthService
        
        validated_data = {
            'email': 'new@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        user, tokens = PublicAuthService.register_user(validated_data)
        
        self.assertEqual(user.email, 'new@example.com')
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
    
    def test_login_user(self):
        """Test user login"""
        from apps.public.accounts.v2.services import PublicAuthService
        
        user, tokens = PublicAuthService.login_user('test@example.com', 'testpass123')
        
        self.assertEqual(user.id, self.user.id)
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        from apps.public.accounts.v2.services import PublicAuthService
        
        user, tokens = PublicAuthService.login_user('test@example.com', 'wrongpass')
        
        self.assertIsNone(user)
        self.assertIsNone(tokens)
    
    def test_login_inactive_user(self):
        """Test login with inactive user"""
        from apps.public.accounts.v2.services import PublicAuthService
        from core.services.user import UserService
        
        # Deactivate user
        UserService.update_user(self.user, is_active=False)
        
        user, tokens = PublicAuthService.login_user('test@example.com', 'testpass123')
        
        self.assertIsNone(user)
        self.assertIsNone(tokens)
    
    def test_add_user_to_store(self):
        """Test adding user to store through public service"""
        from apps.public.accounts.v2.services import PublicAuthService
        
        new_user = UserService.create_user(
            email='customer@example.com',
            username='customer',
            password='pass123'
        )
        
        store_user = PublicAuthService.add_user_to_store(
            new_user, 
            self.store, 
            role='customer'
        )
        
        self.assertEqual(store_user.user, new_user)
        self.assertEqual(store_user.store, self.store)
        self.assertEqual(store_user.role, 'customer')
    
    def test_change_password(self):
        """Test password change"""
        from apps.public.accounts.v2.services import PublicAuthService
        
        success = PublicAuthService.change_password(
            self.user,
            'testpass123',
            'newpass123'
        )
        
        self.assertTrue(success)
        self.assertTrue(self.user.check_password('newpass123'))
    
    def test_change_password_wrong_current(self):
        """Test password change with wrong current password"""
        from apps.public.accounts.v2.services import PublicAuthService
        
        success = PublicAuthService.change_password(
            self.user,
            'wrongpass',
            'newpass123'
        )
        
        self.assertFalse(success)
        self.assertTrue(self.user.check_password('testpass123'))


class TestCustomerAccountService(TestCase):
    """Test CustomerAccountService methods"""
    
    def setUp(self):
        """Set up test data"""
        from core.services.user import UserService
        self.user = UserService.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        from apps.stores.models import Store
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store',
            owner=self.user
        )
        UserService.add_user_to_store(self.user, self.store, 'customer')
    
    def test_get_customer_profile(self):
        """Test getting customer profile"""
        from apps.customer.accounts.v2.services import CustomerAccountService
        
        profile_data = CustomerAccountService.get_customer_profile(self.user)
        
        self.assertEqual(profile_data['user'], self.user)
        self.assertIn('preferences', profile_data)
        self.assertIsNotNone(profile_data['preferences'])
    
    def test_update_customer_profile(self):
        """Test updating customer profile"""
        from apps.customer.accounts.v2.services import CustomerAccountService
        
        updated_user = CustomerAccountService.update_customer_profile(
            self.user,
            {'first_name': 'John', 'last_name': 'Doe'}
        )
        
        self.assertEqual(updated_user.first_name, 'John')
        self.assertEqual(updated_user.last_name, 'Doe')
    
    def test_change_customer_password(self):
        """Test customer password change"""
        from apps.customer.accounts.v2.services import CustomerAccountService
        
        success, message = CustomerAccountService.change_customer_password(
            self.user,
            'testpass123',
            'newpass123'
        )
        
        self.assertTrue(success)
        self.assertEqual(message, "Password changed successfully")
        self.assertTrue(self.user.check_password('newpass123'))
    
    def test_change_password_wrong_current(self):
        """Test password change with wrong current password"""
        from apps.customer.accounts.v2.services import CustomerAccountService
        
        success, message = CustomerAccountService.change_customer_password(
            self.user,
            'wrongpass',
            'newpass123'
        )
        
        self.assertFalse(success)
        self.assertEqual(message, "Current password is incorrect")


class TestDashboardAccountService(TestCase):
    """Test DashboardAccountService methods"""
    
    def setUp(self):
        """Set up test data"""
        from core.services.user import UserService
        self.owner = UserService.create_user(
            email='owner@example.com',
            username='owner',
            password='pass123'
        )
        from apps.stores.models import Store
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store',
            owner=self.owner
        )
        
        # Create additional users
        self.admin = UserService.create_user(
            email='admin@example.com',
            username='admin',
            password='pass123'
        )
        UserService.add_user_to_store(self.admin, self.store, 'admin')
        
        self.customer = UserService.create_user(
            email='customer@example.com',
            username='customer',
            password='pass123'
        )
        UserService.add_user_to_store(self.customer, self.store, 'customer')
    
    def test_get_store_users(self):
        """Test getting store users"""
        from apps.dashboard.accounts.v2.services import DashboardAccountService
        
        users = DashboardAccountService.get_store_users(self.store)
        
        self.assertEqual(users.count(), 3)  # owner + admin + customer
        user_emails = list(users.values_list('user__email', flat=True))
        self.assertIn('owner@example.com', user_emails)
        self.assertIn('admin@example.com', user_emails)
        self.assertIn('customer@example.com', user_emails)
    
    def test_create_store_user(self):
        """Test creating store user"""
        from apps.dashboard.accounts.v2.services import DashboardAccountService
        
        user_data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        store_user = DashboardAccountService.create_store_user(
            self.store,
            user_data,
            role='staff'
        )
        
        self.assertEqual(store_user.user.email, 'newuser@example.com')
        self.assertEqual(store_user.role, 'staff')
        self.assertTrue(store_user.is_active)
    
    def test_update_store_user_role(self):
        """Test updating store user role"""
        from apps.dashboard.accounts.v2.services import DashboardAccountService
        
        store_user = UserService.get_store_user(self.customer, self.store)
        
        updated_store_user = DashboardAccountService.update_store_user_role(
            store_user,
            'staff'
        )
        
        self.assertEqual(updated_store_user.role, 'staff')
    
    def test_deactivate_store_user(self):
        """Test deactivating store user"""
        from apps.dashboard.accounts.v2.services import DashboardAccountService
        
        store_user = UserService.get_store_user(self.customer, self.store)
        
        updated_store_user = DashboardAccountService.deactivate_store_user(store_user)
        
        self.assertFalse(updated_store_user.is_active)
    
    def test_get_store_roles(self):
        """Test getting store roles"""
        from apps.dashboard.accounts.v2.services import DashboardAccountService
        
        roles = DashboardAccountService.get_store_roles()
        
        self.assertIsInstance(roles, list)
        self.assertIn(('owner', 'Owner'), roles)
        self.assertIn(('admin', 'Admin'), roles)
        self.assertIn(('customer', 'Customer'), roles)
    
    def test_get_role_permissions(self):
        """Test getting role permissions"""
        from apps.dashboard.accounts.v2.services import DashboardAccountService
        
        owner_permissions = DashboardAccountService.get_role_permissions('owner')
        self.assertEqual(owner_permissions, ['all'])
        
        customer_permissions = DashboardAccountService.get_role_permissions('customer')
        self.assertIn('view_products', customer_permissions)
        self.assertIn('place_orders', customer_permissions)
    
    def test_check_user_permission(self):
        """Test checking user permissions"""
        from apps.dashboard.accounts.v2.services import DashboardAccountService
        
        # Owner should have all permissions
        has_permission = DashboardAccountService.check_user_permission(
            self.owner,
            self.store,
            'manage_users'
        )
        self.assertTrue(has_permission)
        
        # Customer should have limited permissions
        has_permission = DashboardAccountService.check_user_permission(
            self.customer,
            self.store,
            'manage_users'
        )
        self.assertFalse(has_permission)
        
        # Customer should have view permissions
        has_permission = DashboardAccountService.check_user_permission(
            self.customer,
            self.store,
            'view_products'
        )
        self.assertTrue(has_permission)
