"""
Tests for dashboard accounts API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.accounts.models import StoreUser
from apps.stores.models import Store

User = get_user_model()


class DashboardUserManagementTests(APITestCase):
    """Test dashboard user management"""
    
    def setUp(self):
        """Set up test data"""
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store'
        )
        self.owner = User.objects.create_user(
            email='owner@example.com',
            username='owner',
            password='TestPass123!',
            is_staff=True
        )
        self.store_user = StoreUser.objects.create(
            user=self.owner,
            store=self.store,
            role='owner'
        )
        self.users_url = '/v2/api/dashboard/accounts/users/'
    
    def test_list_users(self):
        """Test listing store users"""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.users_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_user(self):
        """Test creating new user"""
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.users_url, {
            'user': {
                'email': 'newuser@example.com',
                'username': 'newuser',
                'password': 'TestPass123!',
                'first_name': 'New',
                'last_name': 'User'
            },
            'role': 'customer'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_update_user_role(self):
        """Test updating user role"""
        # Create a customer user
        customer = User.objects.create_user(
            email='customer@example.com',
            username='customer',
            password='TestPass123!'
        )
        store_customer = StoreUser.objects.create(
            user=customer,
            store=self.store,
            role='customer'
        )
        
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            f'{self.users_url}{store_customer.id}/',
            {'role': 'staff'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_deactivate_user(self):
        """Test deactivating user"""
        # Create a customer user
        customer = User.objects.create_user(
            email='customer@example.com',
            username='customer',
            password='TestPass123!'
        )
        store_customer = StoreUser.objects.create(
            user=customer,
            store=self.store,
            role='customer'
        )
        
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            f'{self.users_url}{store_customer.id}/deactivate/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_cannot_deactivate_owner(self):
        """Test that owner cannot be deactivated"""
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            f'{self.users_url}{self.store_user.id}/deactivate/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DashboardPermissionTests(APITestCase):
    """Test dashboard permissions"""
    
    def setUp(self):
        """Set up test data"""
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store'
        )
        self.owner = User.objects.create_user(
            email='owner@example.com',
            username='owner',
            password='TestPass123!',
            is_staff=True
        )
        self.staff = User.objects.create_user(
            email='staff@example.com',
            username='staff',
            password='TestPass123!'
        )
        StoreUser.objects.create(
            user=self.owner,
            store=self.store,
            role='owner'
        )
        StoreUser.objects.create(
            user=self.staff,
            store=self.store,
            role='staff'
        )
        self.users_url = '/v2/api/dashboard/accounts/users/'
    
    def test_owner_can_manage_users(self):
        """Test that owner can manage users"""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.users_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_staff_cannot_manage_users(self):
        """Test that staff cannot manage users"""
        self.client.force_authenticate(user=self.staff)
        response = self.client.get(self.users_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
