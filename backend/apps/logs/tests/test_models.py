"""
Tests for logs models.
"""
from django.test import TestCase
from apps.logs.models import LogEntry
from apps.stores.models import Store


class TestLogEntry(TestCase):
    """Test LogEntry model"""
    
    def setUp(self):
        """Set up test data"""
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store'
        )
    
    def test_create_log_entry(self):
        """Test creating a log entry"""
        log = LogEntry.objects.create(
            store=self.store,
            event_type='PAGE_VIEW',
            message='Test page view',
            ip_address='192.168.1.1'
        )
        self.assertEqual(log.event_type, 'PAGE_VIEW')
        self.assertEqual(log.level, 'INFO')
    
    def test_str_representation(self):
        """Test string representation"""
        log = LogEntry.objects.create(
            store=self.store,
            event_type='USER_LOGIN',
            message='User logged in'
        )
        expected = f"{self.store.name} - USER_LOGIN - {log.created_at}"
        self.assertEqual(str(log), expected)
