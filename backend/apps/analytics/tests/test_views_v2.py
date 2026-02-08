from datetime import datetime, timedelta

import pytest
from apps.analytics.models.events import EventLog, SearchLog
from apps.analytics.services.event_service import EventService
from apps.stores.models import Store
from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AnalyticsViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass"
        )
        self.store = Store.objects.create(name="Test Store", owner=self.user)
        self.client.force_authenticate(user=self.user)
        # Create test data
        self.event1 = EventService.log_event(
            event_type="USER_ACTION",
            event_name="Login",
            store=self.store,
            user=self.user,
        )
        self.event2 = EventService.log_event(
            event_type="PAGE_VIEW", event_name="Home", store=self.store, user=self.user
        )
        self.search_log = EventService.log_search(
            query="test",
            results_count=5,
            duration_ms=100,
            store=self.store,
            user=self.user,
        )

    def test_analytics_viewset_list_status_code(self):
        url = reverse("analytics_v2:analytics-overview")
        # The view requires store context, so we expect 400 without it
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_analytics_viewset_list_response_shape(self):
        url = reverse("analytics_v2:analytics-overview")
        response = self.client.get(url)
        # AnalyticsViewSet returns error when store context is missing
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_event_log_viewset_list_status_code(self):
        url = reverse("analytics_v2:event-logs-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_event_log_viewset_list_response_fields(self):
        url = reverse("analytics_v2:event-logs-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that response contains expected fields (paginated response)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)

    def test_event_log_viewset_filter_by_event_type(self):
        url = reverse("analytics_v2:event-logs-list")
        response = self.client.get(url, {"event_type": "USER_ACTION"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check results in paginated response
        for event in response.data["results"]:
            self.assertEqual(event["event_type"], "USER_ACTION")

    def test_event_log_viewset_filter_by_date_range(self):
        today = datetime.now().date()
        url = reverse("analytics_v2:event-logs-list")
        response = self.client.get(url, {"created_at__gte": today.isoformat()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check results in paginated response
        for event in response.data["results"]:
            event_date = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00")).date()
            self.assertGreaterEqual(event_date, today)

    def test_event_log_viewset_filter_by_user(self):
        url = reverse("analytics_v2:event-logs-list")
        response = self.client.get(url, {"user": self.user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_log_viewset_list_status_code(self):
        url = reverse("analytics_v2:search-logs-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_log_viewset_list_response_fields(self):
        url = reverse("analytics_v2:search-logs-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that response contains expected fields
        data = response.json()
        self.assertIn("results", data)
        self.assertIn("count", data)
        if data["results"]:
            search_log = data["results"][0]
            self.assertIn("query", search_log)
            self.assertIn("results_count", search_log)
            self.assertIn("success", search_log)

    def test_search_log_viewset_filter_by_query(self):
        url = reverse("analytics_v2:search-logs-list")
        response = self.client.get(url, {"query": "test"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check results in paginated response
        for search in response.data["results"]:
            self.assertIn("test", search["query"])

    def test_error_handling_invalid_query_params(self):
        url = reverse("analytics_v2:event-logs-list")
        response = self.client.get(url, {"created_at__gte": "invalid-date"})
        # ViewSet doesn't validate date format, Django handles it gracefully
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_error_handling_missing_required_filter(self):
        url = reverse("analytics_v2:event-logs-list")
        response = self.client.get(url, {"event_type": ""})
        # ViewSet doesn't require filters, returns empty results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
