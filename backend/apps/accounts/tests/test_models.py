"""
Test suite for accounts models.
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from unittest.mock import patch

User = get_user_model()


class TestUserModel(TestCase):
    """Test User model"""
    
    def test_create_user(self):
        """Test creating a user"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_verified)
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass123'
        )
        
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
    
    def test_email_unique(self):
        """Test that email is unique"""
        User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        with self.assertRaises(Exception):  # Should raise IntegrityError
            User.objects.create_user(
                email='test@example.com',
                username='testuser2',
                password='testpass123'
            )
    
    def test_username_unique(self):
        """Test that username is unique"""
        User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        with self.assertRaises(Exception):  # Should raise IntegrityError
            User.objects.create_user(
                email='test2@example.com',
                username='testuser',
                password='testpass123'
            )
    
    def test_user_str(self):
        """Test user string representation"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        self.assertEqual(str(user), 'test@example.com')
    
    def test_user_get_full_name(self):
        """Test getting full name"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        self.assertEqual(user.get_full_name(), 'John Doe')
    
    def test_user_get_short_name(self):
        """Test getting short name"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='John'
        )
        
        self.assertEqual(user.get_short_name(), 'John')


class TestStoreUserModel(TestCase):
    """Test StoreUser model"""
    
    def setUp(self):
        """Set up test data"""
        from core.services.user import UserService
        from apps.stores.models import Store
        
        self.user = UserService.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store',
            owner=self.user
        )
    
    def test_create_store_user(self):
        """Test creating store user"""
        from apps.accounts.models import StoreUser
        
        store_user = StoreUser.objects.create(
            user=self.user,
            store=self.store,
            role='customer',
            is_active=True
        )
        
        self.assertEqual(store_user.user, self.user)
        self.assertEqual(store_user.store, self.store)
        self.assertEqual(store_user.role, 'customer')
        self.assertTrue(store_user.is_active)
    
    def test_store_user_unique_together(self):
        """Test unique together constraint on user and store"""
        from apps.accounts.models import StoreUser
        
        StoreUser.objects.create(
            user=self.user,
            store=self.store,
            role='customer'
        )
        
        with self.assertRaises(Exception):  # Should raise IntegrityError
            StoreUser.objects.create(
                user=self.user,
                store=self.store,
                role='admin'
            )
    
    def test_store_user_role_properties(self):
        """Test role helper properties"""
        from apps.accounts.models import StoreUser
        
        # Test owner
        owner_store_user = StoreUser.objects.create(
            user=self.user,
            store=self.store,
            role='owner'
        )
        self.assertTrue(owner_store_user.is_owner)
        self.assertTrue(owner_store_user.is_admin)
        self.assertTrue(owner_store_user.is_staff_role)
        self.assertFalse(owner_store_user.is_customer)
        
        # Test admin
        admin = UserService.create_user(
            email='admin@example.com',
            username='admin',
            password='pass123'
        )
        admin_store_user = StoreUser.objects.create(
            user=admin,
            store=self.store,
            role='admin'
        )
        self.assertFalse(admin_store_user.is_owner)
        self.assertTrue(admin_store_user.is_admin)
        self.assertTrue(admin_store_user.is_staff_role)
        self.assertFalse(admin_store_user.is_customer)
        
        # Test staff
        staff = UserService.create_user(
            email='staff@example.com',
            username='staff',
            password='pass123'
        )
        staff_store_user = StoreUser.objects.create(
            user=staff,
            store=self.store,
            role='staff'
        )
        self.assertFalse(staff_store_user.is_owner)
        self.assertFalse(staff_store_user.is_admin)
        self.assertTrue(staff_store_user.is_staff_role)
        self.assertFalse(staff_store_user.is_customer)
        
        # Test customer
        customer = UserService.create_user(
            email='customer@example.com',
            username='customer',
            password='pass123'
        )
        customer_store_user = StoreUser.objects.create(
            user=customer,
            store=self.store,
            role='customer'
        )
        self.assertFalse(customer_store_user.is_owner)
        self.assertFalse(customer_store_user.is_admin)
        self.assertFalse(customer_store_user.is_staff_role)
        self.assertTrue(customer_store_user.is_customer)
    
    def test_store_user_str(self):
        """Test store user string representation"""
        from apps.accounts.models import StoreUser
        
        store_user = StoreUser.objects.create(
            user=self.user,
            store=self.store,
            role='customer'
        )
        
        expected = f"{self.user.email} - {self.store.name} (customer)"
        self.assertEqual(str(store_user), expected)


class TestRoleModel(TestCase):
    """Test Role model"""
    
    def setUp(self):
        """Set up test data"""
        from core.services.user import UserService
        from apps.stores.models import Store
        
        self.user = UserService.create_user(
            email='owner@example.com',
            username='owner',
            password='pass123'
        )
        
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store',
            owner=self.user
        )
    
    def test_create_role(self):
        """Test creating role"""
        from apps.accounts.models import Role
        
        role = Role.objects.create(
            store=self.store,
            name='custom_role',
            permissions={'can_view': True, 'can_edit': False},
            is_active=True
        )
        
        self.assertEqual(role.store, self.store)
        self.assertEqual(role.name, 'custom_role')
        self.assertEqual(role.permissions['can_view'], True)
        self.assertTrue(role.is_active)
    
    def test_role_unique_together(self):
        """Test unique together constraint on store and name"""
        from apps.accounts.models import Role
        
        Role.objects.create(
            store=self.store,
            name='custom_role',
            permissions={}
        )
        
        # Create another store
        store2 = UserService.create_user(
            email='owner2@example.com',
            username='owner2',
            password='pass123'
        )
        from apps.stores.models import Store
        store2_obj = Store.objects.create(
            name='Store 2',
            slug='store-2',
            owner=store2
        )
        
        # Should be able to create same role name in different store
        role2 = Role.objects.create(
            store=store2_obj,
            name='custom_role',
            permissions={}
        )
        self.assertEqual(role2.name, 'custom_role')
        
        # Should not be able to create same role name in same store
        with self.assertRaises(Exception):  # Should raise IntegrityError
            Role.objects.create(
                store=self.store,
                name='custom_role',
                permissions={}
            )
    
    def test_role_str(self):
        """Test role string representation"""
        from apps.accounts.models import Role
        
        role = Role.objects.create(
            store=self.store,
            name='admin',
            permissions={}
        )
        
        expected = f"Admin ({self.store.name})"
        self.assertEqual(str(role), expected)
    
    def test_role_choices(self):
        """Test role field choices"""
        from apps.accounts.models import Role
        
        role = Role.objects.create(
            store=self.store,
            name='owner',
            permissions={}
        )
        
        # Should be able to create with valid choices
        valid_roles = ['owner', 'admin', 'manager', 'staff', 'customer']
        for role_name in valid_roles:
            role = Role.objects.create(
                store=self.store,
                name=role_name,
                permissions={}
            )
            self.assertEqual(role.name, role_name)


class TestUserPreferencesModel(TestCase):
    """Test UserPreferences model"""
    
    def setUp(self):
        """Set up test data"""
        from core.services.user import UserService
        
        self.user = UserService.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_create_user_preferences(self):
        """Test creating user preferences"""
        from apps.accounts.models import UserPreferences
        
        preferences = UserPreferences.objects.create(
            user=self.user,
            email_notifications=False,
            theme='dark',
            language='es'
        )
        
        self.assertEqual(preferences.user, self.user)
        self.assertFalse(preferences.email_notifications)
        self.assertEqual(preferences.theme, 'dark')
        self.assertEqual(preferences.language, 'es')
    
    def test_user_preferences_defaults(self):
        """Test user preferences default values"""
        from apps.accounts.models import UserPreferences
        
        preferences = UserPreferences.objects.create(user=self.user)
        
        self.assertTrue(preferences.email_notifications)
        self.assertTrue(preferences.push_notifications)
        self.assertEqual(preferences.theme, 'light')
        self.assertEqual(preferences.language, 'en')
        self.assertFalse(preferences.show_email)
        self.assertTrue(preferences.show_online_status)
    
    def test_user_preferences_one_to_one(self):
        """Test one-to-one relationship with user"""
        from apps.accounts.models import UserPreferences
        
        preferences1 = UserPreferences.objects.create(user=self.user)
        
        # Should not be able to create another preferences for same user
        with self.assertRaises(Exception):  # Should raise IntegrityError
            UserPreferences.objects.create(user=self.user)
        
        # Should be able to get preferences via user relationship
        retrieved = self.user.preferences
        self.assertEqual(preferences1.id, retrieved.id)
    
    def test_user_preferences_str(self):
        """Test user preferences string representation"""
        from apps.accounts.models import UserPreferences
        
        preferences = UserPreferences.objects.create(user=self.user)
        
        expected = f"Preferences for {self.user.email}"
        self.assertEqual(str(preferences), expected)


class TestUserActivityModel(TestCase):
    """Test UserActivity model"""
    
    def setUp(self):
        """Set up test data"""
        from core.services.user import UserService
        from apps.stores.models import Store
        
        self.user = UserService.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store',
            owner=self.user
        )
        
        from apps.accounts.models import StoreUser
        self.store_user = StoreUser.objects.create(
            user=self.user,
            store=self.store,
            role='owner'
        )
    
    def test_create_user_activity(self):
        """Test creating user activity"""
        from apps.accounts.models import UserActivity
        
        activity = UserActivity.objects.create(
            store_user=self.store_user,
            action='login',
            details={'ip': '127.0.0.1'},
            ip_address='127.0.0.1',
            user_agent='Mozilla/5.0'
        )
        
        self.assertEqual(activity.store_user, self.store_user)
        self.assertEqual(activity.action, 'login')
        self.assertEqual(activity.details['ip'], '127.0.0.1')
        self.assertEqual(activity.ip_address, '127.0.0.1')
        self.assertEqual(activity.user_agent, 'Mozilla/5.0')
    
    def test_user_activity_action_choices(self):
        """Test activity action field choices"""
        from apps.accounts.models import UserActivity
        
        valid_actions = [
            'login', 'logout', 'password_change', 'profile_update',
            'role_change', 'user_created', 'user_deleted', 'user_deactivated', 'other'
        ]
        
        for action in valid_actions:
            activity = UserActivity.objects.create(
                store_user=self.store_user,
                action=action
            )
            self.assertEqual(activity.action, action)
    
    def test_user_activity_str(self):
        """Test user activity string representation"""
        from apps.accounts.models import UserActivity
        
        activity = UserActivity.objects.create(
            store_user=self.store_user,
            action='login'
        )
        
        expected = f"{self.user.email} - Login"
        self.assertEqual(str(activity), expected)
    
    def test_user_activity_ordering(self):
        """Test that activities are ordered by created_at descending"""
        from apps.accounts.models import UserActivity
        import datetime
        from django.utils import timezone
        
        # Create activities with different timestamps
        activity1 = UserActivity.objects.create(
            store_user=self.store_user,
            action='login'
        )
        
        # Wait a bit to ensure different timestamp
        import time
        time.sleep(0.01)
        
        activity2 = UserActivity.objects.create(
            store_user=self.store_user,
            action='logout'
        )
        
        # Get all activities
        activities = UserActivity.objects.all()
        
        # Should be ordered by created_at descending (newest first)
        self.assertEqual(activities[0], activity2)
        self.assertEqual(activities[1], activity1)


class TestModelIntegration(TestCase):
    """Test model integration and relationships"""
    
    def setUp(self):
        """Set up test data"""
        from core.services.user import UserService
        from apps.stores.models import Store
        
        self.user = UserService.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store',
            owner=self.user
        )
    
    def test_user_store_user_relationship(self):
        """Test user to store user relationship"""
        from apps.accounts.models import StoreUser
        
        # Create store user
        store_user = StoreUser.objects.create(
            user=self.user,
            store=self.store,
            role='owner'
        )
        
        # Test reverse relationship
        self.assertIn(store_user, self.user.store_users.all())
        self.assertEqual(self.user.store_users.count(), 1)
    
    def test_store_store_user_relationship(self):
        """Test store to store user relationship"""
        from apps.accounts.models import StoreUser
        
        # Create store user
        store_user = StoreUser.objects.create(
            user=self.user,
            store=self.store,
            role='owner'
        )
        
        # Test reverse relationship
        self.assertIn(store_user, self.store.store_users.all())
        self.assertEqual(self.store.store_users.count(), 1)
    
    def test_user_preferences_relationship(self):
        """Test user to preferences relationship"""
        from apps.accounts.models import UserPreferences
        
        # Create preferences
        preferences = UserPreferences.objects.create(
            user=self.user,
            theme='dark'
        )
        
        # Test reverse relationship
        self.assertEqual(self.user.preferences, preferences)
    
    def test_store_user_activity_relationship(self):
        """Test store user to activity relationship"""
        from apps.accounts.models import StoreUser, UserActivity
        
        # Create store user
        store_user = StoreUser.objects.create(
            user=self.user,
            store=self.store,
            role='owner'
        )
        
        # Create activities
        activity1 = UserActivity.objects.create(
            store_user=store_user,
            action='login'
        )
        activity2 = UserActivity.objects.create(
            store_user=store_user,
            action='logout'
        )
        
        # Test reverse relationship
        self.assertIn(activity1, store_user.activities.all())
        self.assertIn(activity2, store_user.activities.all())
        self.assertEqual(store_user.activities.count(), 2)
    
    def test_cascade_delete_user(self):
        """Test cascade delete when user is deleted"""
        from apps.accounts.models import StoreUser, UserPreferences, UserActivity
        
        # Create related objects
        StoreUser.objects.create(
            user=self.user,
            store=self.store,
            role='owner'
        )
        
        UserPreferences.objects.create(user=self.user)
        
        store_user = StoreUser.objects.create(
            user=self.user,
            store=self.store,
            role='admin'
        )
        UserActivity.objects.create(
            store_user=store_user,
            action='login'
        )
        
        # Delete user
        self.user.delete()
        
        # Verify related objects are deleted
        self.assertEqual(StoreUser.objects.filter(user=self.user).count(), 0)
        self.assertEqual(UserPreferences.objects.filter(user=self.user).count(), 0)
        self.assertEqual(UserActivity.objects.filter(store_user__user=self.user).count(), 0)
    
    def test_cascade_delete_store(self):
        """Test cascade delete when store is deleted"""
        from apps.accounts.models import StoreUser, Role
        
        # Create related objects
        StoreUser.objects.create(
            user=self.user,
            store=self.store,
            role='owner'
        )
        
        Role.objects.create(
            store=self.store,
            name='custom_role',
            permissions={}
        )
        
        # Delete store
        self.store.delete()
        
        # Verify related objects are deleted
        self.assertEqual(StoreUser.objects.filter(store=self.store).count(), 0)
        self.assertEqual(Role.objects.filter(store=self.store).count(), 0)
    
    @patch('core.libs.logging.log_event_async.delay')
    def test_user_creation_logging(self, mock_log_event):
        """Test that user creation is logged"""
        User.objects.create_user(
            email='logged@example.com',
            username='loggeduser',
            password='pass123'
        )
        
        # Verify logging was called
        mock_log_event.assert_called_once()
        call_args = mock_log_event.call_args[0][0]
        self.assertEqual(call_args['event_type'], 'create_user_accounts')
        self.assertIn('User created: logged@example.com', call_args['message'])
    
    @patch('core.libs.logging.log_event_async.delay')
    def test_user_email_update_logging(self, mock_log_event):
        """Test that user email update is logged"""
        user = User.objects.create_user(
            email='old@example.com',
            username='olduser',
            password='pass123'
        )
        
        # Reset mock
        mock_log_event.reset_mock()
        
        # Update email
        user.email = 'new@example.com'
        user.save()
        
        # Verify logging was called
        mock_log_event.assert_called_once()
        call_args = mock_log_event.call_args[0][0]
        self.assertEqual(call_args['event_type'], 'update_user_email')
        self.assertIn('Email updated: old@example.com -> new@example.com', call_args['message'])
