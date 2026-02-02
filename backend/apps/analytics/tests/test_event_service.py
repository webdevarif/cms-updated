from unittest.mock import patch

import pytest
from apps.analytics.models.events import EventLog, SearchLog
from apps.analytics.services.event_service import EventService
from apps.stores.models import Store
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

User = get_user_model()


class EventServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass"
        )
        self.store = Store.objects.create(name="Test Store", owner=self.user)

    def test_log_event_with_user_and_store(self):
        EventService.log_event(
            event_type="TEST_EVENT",
            event_name="Test Event",
            properties={"key": "value"},
            user=self.user,
            store=self.store,
        )
        event_log = EventLog.objects.get(event_type="TEST_EVENT")
        self.assertEqual(event_log.event_name, "Test Event")
        self.assertEqual(event_log.properties, {"key": "value"})
        self.assertEqual(event_log.user, self.user)
        self.assertEqual(event_log.store, self.store)

    def test_log_event_without_user_and_store(self):
        EventService.log_event(event_type="TEST_EVENT", event_name="Test Event", store=self.store)
        event_log = EventLog.objects.get(event_type="TEST_EVENT")
        self.assertEqual(event_log.event_name, "Test Event")
        self.assertIsNone(event_log.user)
        self.assertEqual(event_log.store, self.store)

    def test_log_event_with_extra_properties(self):
        EventService.log_event(
            event_type="TEST_EVENT",
            event_name="Test Event",
            properties={"extra_key": "extra_value"},
            store=self.store,
        )
        event_log = EventLog.objects.get(event_type="TEST_EVENT")
        self.assertEqual(event_log.properties["extra_key"], "extra_value")

    def test_log_event_invalid_event_type(self):
        # Assuming EventService allows any event_type based on current implementation
        EventService.log_event(
            event_type="INVALID_TYPE", event_name="Invalid Event", store=self.store
        )
        event_log = EventLog.objects.get(event_type="INVALID_TYPE")
        self.assertEqual(
            event_log.event_type, "INVALID_TYPE"
        )  # Event type is stored as-is if no validation

    def test_log_search_zero_results(self):
        EventService.log_search(
            query="test_query",
            results_count=0,
            duration_ms=100,
            request=None,
            user=None,
            store=self.store,
        )
        search_log = SearchLog.objects.get(query="test_query")
        self.assertEqual(search_log.results_count, 0)
        self.assertEqual(search_log.duration_ms, 100)

    def test_log_search_large_results(self):
        EventService.log_search(
            query="test_query",
            results_count=1000,
            duration_ms=200,
            request=None,
            user=None,
            store=self.store,
        )
        search_log = SearchLog.objects.get(query="test_query")
        self.assertEqual(search_log.results_count, 1000)

    def test_log_search_duration_none(self):
        EventService.log_search(
            query="test_query",
            results_count=5,
            duration_ms=None,
            request=None,
            user=None,
            store=self.store,
        )
        search_log = SearchLog.objects.get(query="test_query")
        self.assertIsNone(search_log.duration_ms)  # Or handle default if set in service

    def test_log_page_view_minimal_context(self):
        EventService.log_page_view(request=None, user=None, store=self.store)
        event_log = EventLog.objects.get(event_type="PAGE_VIEW")
        self.assertEqual(event_log.event_type, "PAGE_VIEW")
        self.assertIsNone(event_log.user)
        self.assertEqual(event_log.store, self.store)

    def test_log_page_view_full_context(self):
        EventService.log_page_view(request=None, user=self.user, store=self.store, duration_ms=500)
        event_log = EventLog.objects.get(event_type="PAGE_VIEW")
        self.assertEqual(event_log.user, self.user)
        self.assertEqual(event_log.store, self.store)
        self.assertEqual(event_log.duration_ms, 500)

    def test_log_user_action_minimal_context(self):
        EventService.log_user_action(action_name="TEST_ACTION", user=None, store=self.store)
        event_log = EventLog.objects.get(event_type="USER_ACTION")
        self.assertEqual(event_log.event_type, "USER_ACTION")
        self.assertIsNone(event_log.user)
        self.assertEqual(event_log.store, self.store)

    def test_log_user_action_full_context(self):
        EventService.log_user_action(
            action_name="TEST_ACTION",
            user=self.user,
            store=self.store,
            properties={"action_detail": "detail"},
        )
        event_log = EventLog.objects.get(event_type="USER_ACTION")
        self.assertEqual(event_log.event_name, "User Action: TEST_ACTION")
        self.assertEqual(event_log.properties, {"action_detail": "detail"})
        self.assertEqual(event_log.user, self.user)
        self.assertEqual(event_log.store, self.store)
