"""
Integration tests for accounts API endpoints.
"""
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()


@pytest.mark.django_db
class TestPublicAccountsAPI:
    """Test public accounts API endpoints"""
    
    def setup_method(self):
        """Set up test data"""
        self.client = APIClient()
        from core.services.user import UserService
        from apps.stores.models import Store
        
        # Create store
        self.owner = UserService.create_user(
            email='owner@example.com',
            username='owner',
            password='pass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store',
            owner=self.owner
        )
    
    def test_register_user(self):
        """Test user registration endpoint"""
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        response = self.client.post('/v2/api/public/accounts/register/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert response.data['user']['email'] == 'newuser@example.com'
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
    
    def test_register_user_password_mismatch(self):
        """Test registration with password mismatch"""
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'password_confirm': 'differentpass',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        response = self.client.post('/v2/api/public/accounts/register/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data['details']
    
    def test_register_user_duplicate_email(self):
        """Test registration with duplicate email"""
        # Create existing user
        from core.services.user import UserService
        UserService.create_user(
            email='existing@example.com',
            username='existing',
            password='pass123'
        )
        
        data = {
            'email': 'existing@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        response = self.client.post('/v2/api/public/accounts/register/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_user(self):
        """Test user login endpoint"""
        # Create user first
        from core.services.user import UserService
        user = UserService.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post('/v2/api/public/accounts/login/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert response.data['user']['email'] == 'test@example.com'
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpass'
        }
        
        response = self.client.post('/v2/api/public/accounts/login/', data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['code'] == 'INVALID_CREDENTIALS'
    
    def test_login_inactive_user(self):
        """Test login with inactive user"""
        # Create inactive user
        from core.services.user import UserService
        user = UserService.create_user(
            email='inactive@example.com',
            username='inactive',
            password='pass123',
            is_active=False
        )
        
        data = {
            'email': 'inactive@example.com',
            'password': 'pass123'
        }
        
        response = self.client.post('/v2/api/public/accounts/login/', data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['code'] == 'INVALID_CREDENTIALS'
    
    def test_logout_user(self):
        """Test user logout endpoint"""
        # Create and login user
        from core.services.user import UserService
        user = UserService.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        # Get tokens
        from apps.accounts.v2.services import AuthService
        tokens = AuthService.generate_token(user)
        
        data = {'refresh': tokens['refresh']}
        response = self.client.post('/v2/api/public/accounts/logout/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Successfully logged out'
    
    def test_password_reset_request(self):
        """Test password reset request"""
        # Create user
        from core.services.user import UserService
        UserService.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        data = {'email': 'test@example.com'}
        response = self.client.post('/v2/api/public/accounts/password-reset/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Password reset email sent'
    
    def test_password_reset_nonexistent_email(self):
        """Test password reset for nonexistent email"""
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post('/v2/api/public/accounts/password-reset/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Password reset email sent'
    
    def test_password_reset_no_email(self):
        """Test password reset without email"""
        data = {}
        response = self.client.post('/v2/api/public/accounts/password-reset/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    @patch('apps.smtp.services.SmtpEmailService.send_email_async.delay')
    def test_password_reset_email_sent(self, mock_send_email):
        """Test that password reset email is sent"""
        # Create user
        from core.services.user import UserService
        UserService.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        data = {'email': 'test@example.com'}
        response = self.client.post('/v2/api/public/accounts/password-reset/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert mock_send_email.called


@pytest.mark.django_db
class TestCustomerAccountsAPI:
    """Test customer accounts API endpoints"""
    
    def setup_method(self):
        """Set up test data"""
        self.client = APIClient()
        from core.services.user import UserService
        from apps.stores.models import Store
        
        # Create store and user
        self.owner = UserService.create_user(
            email='owner@example.com',
            username='owner',
            password='pass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store',
            owner=self.owner
        )
        
        self.user = UserService.create_user(
            email='customer@example.com',
            username='customer',
            password='pass123'
        )
        UserService.add_user_to_store(self.user, self.store, 'customer')
        
        # Authenticate user
        from apps.accounts.v2.services import AuthService
        tokens = AuthService.generate_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    def test_get_customer_profile(self):
        """Test getting customer profile"""
        response = self.client.get('/v2/api/customer/accounts/profile/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'customer@example.com'
        assert 'preferences' in response.data
    
    def test_update_customer_profile(self):
        """Test updating customer profile"""
        data = {
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        response = self.client.patch('/v2/api/customer/accounts/profile/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'John'
        assert response.data['last_name'] == 'Doe'
    
    def test_change_customer_password(self):
        """Test changing customer password"""
        data = {
            'current_password': 'pass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        
        response = self.client.post('/v2/api/customer/accounts/change-password/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Password changed successfully'
        
        # Verify password changed
        self.user.refresh_from_db()
        assert self.user.check_password('newpass123')
    
    def test_change_password_wrong_current(self):
        """Test changing password with wrong current password"""
        data = {
            'current_password': 'wrongpass',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        
        response = self.client.post('/v2/api/customer/accounts/change-password/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'current_password' in response.data
    
    def test_change_password_mismatch(self):
        """Test changing password with mismatched confirmation"""
        data = {
            'current_password': 'pass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'differentpass'
        }
        
        response = self.client.post('/v2/api/customer/accounts/change-password/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'new_password' in response.data
    
    def test_delete_customer_account(self):
        """Test deleting customer account"""
        data = {'password': 'pass123'}
        
        response = self.client.post('/v2/api/customer/accounts/profile/delete/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Account deleted successfully'
        
        # Verify user deleted
        with pytest.raises(User.DoesNotExist):
            User.objects.get(email='customer@example.com')
    
    def test_delete_account_wrong_password(self):
        """Test deleting account with wrong password"""
        data = {'password': 'wrongpass'}
        
        response = self.client.post('/v2/api/customer/accounts/profile/delete/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated access is denied"""
        self.client.credentials()  # Remove authentication
        
        response = self.client.get('/v2/api/customer/accounts/profile/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDashboardAccountsAPI:
    """Test dashboard accounts API endpoints"""
    
    def setup_method(self):
        """Set up test data"""
        self.client = APIClient()
        from core.services.user import UserService
        from apps.stores.models import Store
        
        # Create store
        self.owner = UserService.create_user(
            email='owner@example.com',
            username='owner',
            password='pass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store',
            owner=self.owner
        )
        
        # Create admin user
        self.admin = UserService.create_user(
            email='admin@example.com',
            username='admin',
            password='pass123'
        )
        UserService.add_user_to_store(self.admin, self.store, 'admin')
        
        # Authenticate as admin
        from apps.accounts.v2.services import AuthService
        tokens = AuthService.generate_token(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    def test_list_store_users(self):
        """Test listing store users"""
        response = self.client.get('/v2/api/dashboard/accounts/users/')
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) >= 2  # owner + admin
        
        # Check that users have required fields
        user_data = response.data[0]
        assert 'user' in user_data
        assert 'role' in user_data
        assert 'is_active' in user_data
    
    def test_create_store_user(self):
        """Test creating store user"""
        data = {
            'user': {
                'email': 'newuser@example.com',
                'username': 'newuser',
                'password': 'newpass123',
                'first_name': 'New',
                'last_name': 'User'
            },
            'role': 'customer'
        }
        
        response = self.client.post('/v2/api/dashboard/accounts/users/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user']['email'] == 'newuser@example.com'
        assert response.data['role'] == 'customer'
        assert response.data['is_active'] is True
    
    def test_update_store_user_role(self):
        """Test updating store user role"""
        # Create a customer user first
        from core.services.user import UserService
        customer = UserService.create_user(
            email='customer@example.com',
            username='customer',
            password='pass123'
        )
        store_user = UserService.add_user_to_store(customer, self.store, 'customer')
        
        data = {'role': 'staff'}
        response = self.client.patch(
            f'/v2/api/dashboard/accounts/users/{store_user.id}/', 
            data
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['role'] == 'staff'
    
    def test_deactivate_store_user(self):
        """Test deactivating store user"""
        # Create a customer user first
        from core.services.user import UserService
        customer = UserService.create_user(
            email='customer@example.com',
            username='customer',
            password='pass123'
        )
        store_user = UserService.add_user_to_store(customer, self.store, 'customer')
        
        response = self.client.post(
            f'/v2/api/dashboard/accounts/users/{store_user.id}/deactivate/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'deactivated' in response.data['message']
    
    def test_activate_store_user(self):
        """Test activating store user"""
        # Create and deactivate a customer user
        from core.services.user import UserService
        customer = UserService.create_user(
            email='customer@example.com',
            username='customer',
            password='pass123'
        )
        store_user = UserService.add_user_to_store(customer, self.store, 'customer')
        UserService.deactivate_store_user(customer, self.store)
        
        response = self.client.post(
            f'/v2/api/dashboard/accounts/users/{store_user.id}/activate/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'activated' in response.data['message']
    
    def test_cannot_deactivate_owner(self):
        """Test that owner cannot be deactivated"""
        owner_store_user = UserService.get_store_user(self.owner, self.store)
        
        response = self.client.post(
            f'/v2/api/dashboard/accounts/users/{owner_store_user.id}/deactivate/'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Cannot deactivate store owner' in response.data['error']
    
    def test_list_store_roles(self):
        """Test listing store roles"""
        response = self.client.get('/v2/api/dashboard/accounts/roles/')
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        
        # Check that roles have required fields
        if response.data:
            role_data = response.data[0]
            assert 'name' in role_data
            assert 'permissions' in role_data
            assert 'is_active' in role_data
    
    def test_create_store_role(self):
        """Test creating store role"""
        data = {
            'name': 'custom_role',
            'permissions': {
                'can_view_reports': True,
                'can_manage_inventory': True
            },
            'is_active': True
        }
        
        response = self.client.post('/v2/api/dashboard/accounts/roles/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'custom_role'
        assert response.data['permissions']['can_view_reports'] is True
    
    def test_get_role_permissions(self):
        """Test getting role permissions"""
        # Create a role first
        from apps.accounts.models import Role
        role = Role.objects.create(
            store=self.store,
            name='admin',
            permissions={'all': True}
        )
        
        response = self.client.get(
            f'/v2/api/dashboard/accounts/roles/{role.id}/permissions/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'permissions' in response.data
        assert isinstance(response.data['permissions'], list)
    
    def test_unauthorized_access(self):
        """Test that unauthorized access is denied"""
        # Authenticate as customer (should not have access)
        customer = UserService.create_user(
            email='customer@example.com',
            username='customer',
            password='pass123'
        )
        UserService.add_user_to_store(customer, self.store, 'customer')
        
        from apps.accounts.v2.services import AuthService
        tokens = AuthService.generate_token(customer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get('/v2/api/dashboard/accounts/users/')
        
        assert response.status_code == status.HTTP_403_FORbidden


@pytest.mark.django_db
class TestStoreIsolation:
    """Test store isolation in accounts API"""
    
    def setup_method(self):
        """Set up test data"""
        from core.services.user import UserService
        from apps.stores.models import Store
        
        # Create two stores
        self.owner_a = UserService.create_user(
            email='owner_a@example.com',
            username='owner_a',
            password='pass123'
        )
        self.store_a = Store.objects.create(
            name='Store A',
            slug='store-a',
            owner=self.owner_a
        )
        
        self.owner_b = UserService.create_user(
            email='owner_b@example.com',
            username='owner_b',
            password='pass123'
        )
        self.store_b = Store.objects.create(
            name='Store B',
            slug='store-b',
            owner=self.owner_b
        )
        
        # Create admin for store A
        self.admin_a = UserService.create_user(
            email='admin_a@example.com',
            username='admin_a',
            password='pass123'
        )
        UserService.add_user_to_store(self.admin_a, self.store_a, 'admin')
        
        # Authenticate as admin of store A
        from apps.accounts.v2.services import AuthService
        tokens = AuthService.generate_token(self.admin_a)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    def test_store_isolation_users(self):
        """Test that users are isolated by store"""
        # Add a user to store B
        from core.services.user import UserService
        user_b = UserService.create_user(
            email='user_b@example.com',
            username='user_b',
            password='pass123'
        )
        UserService.add_user_to_store(user_b, self.store_b, 'customer')
        
        # Store A admin should only see Store A users
        response = self.client.get('/v2/api/dashboard/accounts/users/')
        
        assert response.status_code == status.HTTP_200_OK
        user_emails = [user['user']['email'] for user in response.data]
        
        # Should see store A users
        assert 'owner_a@example.com' in user_emails
        assert 'admin_a@example.com' in user_emails
        
        # Should NOT see store B users
        assert 'owner_b@example.com' not in user_emails
        assert 'user_b@example.com' not in user_emails
    
    def test_store_isolation_roles(self):
        """Test that roles are isolated by store"""
        # Create role in store B
        from apps.accounts.models import Role
        Role.objects.create(
            store=self.store_b,
            name='custom_role',
            permissions={'custom': True}
        )
        
        # Store A admin should only see Store A roles
        response = self.client.get('/v2/api/dashboard/accounts/roles/')
        
        assert response.status_code == status.HTTP_200_OK
        role_names = [role['name'] for role in response.data]
        
        # Should not see store B roles
        assert 'custom_role' not in role_names
