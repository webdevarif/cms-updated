"""
Tests for logs API v2.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from ..models import LogEntry
from ..services import LogService

User = get_user_model()


class LogServiceTestCase(TestCase):
    """Test LogService methods"""
    
    def setUp(self):
        """Set up test data"""
        from apps.stores.models import Store
        
        self.store = Store.objects.create(
            name="Test Store",
            slug="test-store",
            owner=None
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
    
    def test_log_event_creation(self):
        """Test log event creation"""
        log_entry = LogService.log_event(
            store=self.store,
            event_type='PAGE_VIEW',
            message='Test page view',
            user=self.user,
            metadata={'page': '/home'}
        )
        
        self.assertEqual(log_entry.store, self.store)
        self.assertEqual(log_entry.event_type, 'PAGE_VIEW')
        self.assertEqual(log_entry.message, 'Test page view')
        self.assertEqual(log_entry.user, self.user)
        self.assertEqual(log_entry.metadata['page'], '/home')
    
    def test_get_store_analytics(self):
        """Test analytics generation"""
        # Create some test data
        for i in range(10):
            LogService.log_event(
                store=self.store,
                event_type='PAGE_VIEW',
                message=f'Page view {i}',
                metadata={'page': f'/page{i}'}
            )
        
        analytics = LogService.get_store_analytics(self.store, days=30)
        
        self.assertIn('total_visits', analytics)
        self.assertIn('unique_visitors', analytics)
        self.assertIn('bounce_rate', analytics)
        self.assertIn('top_pages', analytics)
        self.assertEqual(analytics['total_visits'], 10)
    
    def test_detect_suspicious_activity(self):
        """Test suspicious activity detection"""
        # Create some suspicious activity
        for i in range(20):  # High number of requests from same IP
            LogService.log_event(
                store=self.store,
                event_type='LOGIN_ATTEMPT',
                message=f'Login attempt {i}',
                ip_address='192.168.1.100',
                metadata={'success': False}
            )
        
        suspicious = LogService.detect_suspicious_activity(self.store, hours=24)
        
        self.assertIsInstance(suspicious, list)
        # Should detect the high number of failed login attempts
        self.assertTrue(len(suspicious) > 0)


class LogAPITestCase(APITestCase):
    """Test Log API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        from apps.stores.models import Store
        
        self.store = Store.objects.create(
            name="Test Store",
            slug="test-store",
            owner=None
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        
        # Add user to store
        from apps.stores.models import StoreMember
        StoreMember.objects.create(
            store=self.store,
            user=self.user,
            role='admin'
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_list_log_entries_api(self):
        """Test listing log entries via API"""
        # Create some test log entries
        for i in range(5):
            LogService.log_event(
                store=self.store,
                event_type='PAGE_VIEW',
                message=f'Page view {i}',
                user=self.user
            )
        
        url = reverse('logs:logentry-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
    
    def test_track_event_api(self):
        """Test event tracking via API"""
        url = reverse('logs:track-event')
        data = {
            'event_type': 'CLICK',
            'message': 'User clicked button',
            'page_url': '/home',
            'metadata': {'button_id': 'submit'}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'logged')
        
        # Check log entry was created
        self.assertEqual(LogEntry.objects.count(), 1)
        log_entry = LogEntry.objects.first()
        self.assertEqual(log_entry.event_type, 'CLICK')
        self.assertEqual(log_entry.message, 'User clicked button')
    
    def test_get_analytics_api(self):
        """Test analytics endpoint via API"""
        # Create some test data
        for i in range(10):
            LogService.log_event(
                store=self.store,
                event_type='PAGE_VIEW',
                message=f'Page view {i}',
                user=self.user
            )
        
        url = reverse('logs:storeanalytics-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_visits', response.data)
        self.assertEqual(response.data['total_visits'], 10)
    
    def test_get_security_events_api(self):
        """Test security events endpoint via API"""
        # Create some suspicious activity
        for i in range(20):
            LogService.log_event(
                store=self.store,
                event_type='LOGIN_ATTEMPT',
                message=f'Login attempt {i}',
                ip_address='192.168.1.100',
                metadata={'success': False}
            )
        
        url = reverse('logs:securityevents-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
