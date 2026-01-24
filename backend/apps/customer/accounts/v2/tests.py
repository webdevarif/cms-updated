"""
Tests for customer accounts API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.accounts.models import StoreUser, UserPreferences
from apps.stores.models import Store

User = get_user_model()


class CustomerProfileTests(APITestCase):
    """Test customer profile management"""
    
    def setUp(self):
        """Set up test data"""
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store'
        )
        self.user = User.objects.create_user(
            email='customer@example.com',
            username='customer',
            password='TestPass123!'
        )
        self.store_user = StoreUser.objects.create(
            user=self.user,
            store=self.store,
            role='customer'
        )
        self.profile_url = '/v2/api/customer/accounts/profile/'
    
    def test_get_profile(self):
        """Test getting customer profile"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'customer@example.com')
    
    def test_update_profile(self):
        """Test updating customer profile"""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.profile_url, {
            'first_name': 'Updated',
            'last_name': 'Name'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')


class CustomerPasswordTests(APITestCase):
    """Test customer password management"""
    
    def setUp(self):
        """Set up test data"""
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store'
        )
        self.user = User.objects.create_user(
            email='customer@example.com',
            username='customer',
            password='TestPass123!'
        )
        self.store_user = StoreUser.objects.create(
            user=self.user,
            store=self.store,
            role='customer'
        )
        self.change_password_url = '/v2/api/customer/accounts/change-password/'
    
    def test_change_password_success(self):
        """Test successful password change"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.change_password_url, {
            'current_password': 'TestPass123!',
            'new_password': 'NewPass123!',
            'new_password_confirm': 'NewPass123!'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_change_password_wrong_current(self):
        """Test password change with wrong current password"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.change_password_url, {
            'current_password': 'WrongPass123!',
            'new_password': 'NewPass123!',
            'new_password_confirm': 'NewPass123!'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_change_password_mismatched(self):
        """Test password change with mismatched passwords"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.change_password_url, {
            'current_password': 'TestPass123!',
            'new_password': 'NewPass123!',
            'new_password_confirm': 'DifferentPass123!'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
