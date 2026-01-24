"""
Tests for public accounts API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.accounts.models import StoreUser
from apps.stores.models import Store

User = get_user_model()


class UserRegistrationTests(APITestCase):
    """Test user registration"""
    
    def setUp(self):
        """Set up test data"""
        self.register_url = '/v2/api/public/accounts/register/'
        self.valid_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_register_new_user(self):
        """Test successful user registration"""
        response = self.client.post(self.register_url, self.valid_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('user' in response.data)
        self.assertTrue('tokens' in response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
    
    def test_register_with_mismatched_passwords(self):
        """Test registration with mismatched passwords"""
        data = self.valid_data.copy()
        data['password_confirm'] = 'DifferentPass123!'
        
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        User.objects.create_user(
            email='test@example.com',
            username='existinguser',
            password='TestPass123!'
        )
        
        response = self.client.post(self.register_url, self.valid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTests(APITestCase):
    """Test user login"""
    
    def setUp(self):
        """Set up test data"""
        self.login_url = '/v2/api/public/accounts/login/'
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
    
    def test_login_success(self):
        """Test successful login"""
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('tokens' in response.data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'WrongPass123!'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_inactive_user(self):
        """Test login with inactive user"""
        self.user.is_active = False
        self.user.save()
        
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        })
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserLogoutTests(APITestCase):
    """Test user logout"""
    
    def setUp(self):
        """Set up test data"""
        self.logout_url = '/v2/api/public/accounts/logout/'
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
        # Login and get token
        response = self.client.post('/v2/api/public/accounts/login/', {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        })
        self.refresh_token = response.data['tokens']['refresh']
    
    def test_logout_success(self):
        """Test successful logout"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh_token}')
        response = self.client.post(self.logout_url, {'refresh': self.refresh_token})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
