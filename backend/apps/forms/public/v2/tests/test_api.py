"""
Endpoint-focused tests for forms API.
"""

from apps.forms.models.forms import FormTemplate
from apps.forms.models.submissions import FormSubmission
from apps.stores.models import Store
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


class TestFormPublicViewSet(TestCase):
    """Test public forms API endpoints via HTTP requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.store = Store.objects.create(
            name="Test Store", slug="test-store", domain="test.com", owner=self.user
        )
        self.form = FormTemplate.objects.create(
            store=self.store,
            title="Test Form",
            slug="test-form",
            is_published=True,
            is_active=True,
        )

    def test_list_forms(self):
        """Test listing public forms"""
        response = self.client.get("/api/v2/forms/public/forms/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)

    def test_retrieve_form(self):
        """Test retrieving a specific form"""
        response = self.client.get(f"/api/v2/forms/public/forms/{self.form.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["slug"], "test-form")

    def test_submit_form(self):
        """Test submitting a form"""
        data = {
            "submitter_name": "John Doe",
            "submitter_email": "john@example.com",
            "form_data": {"name": "John", "message": "Hello"},
        }
        response = self.client.post(f"/api/v2/forms/public/forms/{self.form.id}/submit/", data)
        self.assertEqual(response.status_code, 201)


class TestFormCustomerViewSet(TestCase):
    """Test customer forms API endpoints via HTTP requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.store = Store.objects.create(
            name="Test Store", slug="test-store", domain="test.com", owner=self.user
        )
        self.form = FormTemplate.objects.create(
            store=self.store, title="Test Form", slug="test-form"
        )
        self.client.force_authenticate(user=self.user)

    def test_list_forms(self):
        """Test listing customer forms"""
        response = self.client.get("/api/v2/forms/customer/forms/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)

    def test_create_form(self):
        """Test creating a form"""
        data = {"title": "New Form", "slug": "new-form", "description": "Test form"}
        response = self.client.post("/api/v2/forms/customer/forms/", data)
        self.assertEqual(response.status_code, 201)

    def test_duplicate_form(self):
        """Test duplicating a form"""
        response = self.client.post(f"/api/v2/forms/customer/forms/{self.form.id}/duplicate/")
        self.assertEqual(response.status_code, 201)


class TestFormDashboardViewSet(TestCase):
    """Test dashboard forms API endpoints via HTTP requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.store = Store.objects.create(
            name="Test Store", slug="test-store", domain="test.com", owner=self.user
        )
        self.form = FormTemplate.objects.create(
            store=self.store, title="Test Form", slug="test-form"
        )
        self.client.force_authenticate(user=self.user)

    def test_list_forms(self):
        """Test listing dashboard forms"""
        response = self.client.get("/api/v2/forms/dashboard/forms/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)

    def test_get_form_analytics(self):
        """Test getting form analytics"""
        response = self.client.get(f"/api/v2/forms/dashboard/forms/{self.form.id}/analytics/")
        self.assertEqual(response.status_code, 200)

    def test_export_form(self):
        """Test exporting form data"""
        response = self.client.post(f"/api/v2/forms/dashboard/forms/{self.form.id}/export/")
        self.assertEqual(response.status_code, 200)
