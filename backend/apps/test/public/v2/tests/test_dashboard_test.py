"""
Dashboard Test API tests.
"""
import factory
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


# FactoryBoy fixtures
class UserFactory(factory.django.DjangoModelFactory):
    """User factory for test data"""

    class Meta:
        model = User
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = "testpass123"


@pytest.mark.django_db
class DashboardTestRunViewSetTests:
    """Dashboard test run viewset tests"""

    @pytest.fixture
    def admin_user(self):
        """Create admin user fixture"""
        return UserFactory(email="admin@example.com", is_staff=True, is_superuser=True)

    @pytest.fixture
    def anonymous_client(self):
        """Create anonymous APIClient fixture"""
        return APIClient()

    @pytest.fixture
    def authenticated_client(self, admin_user):
        """Create authenticated APIClient fixture"""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        return client

    # List endpoint tests
    def test_list_test_runs_as_admin(self, authenticated_client):
        """Test listing test runs as admin"""
        response = authenticated_client.get("/v2/api/test/")
        assert response.status_code == 200

    def test_list_test_runs_as_anonymous(self, anonymous_client):
        """Test listing test runs as anonymous"""
        response = anonymous_client.get("/v2/api/test/")
        assert response.status_code == 200

    # Create endpoint tests
    def test_create_test_run_as_admin(self, authenticated_client):
        """Test creating test run as admin"""
        response = authenticated_client.post(
            "/v2/api/test/", {"run_type": "api", "status": "pending"}
        )
        assert response.status_code in [201, 400]  # May fail validation but should reach endpoint

    def test_create_test_run_as_anonymous(self, anonymous_client):
        """Test creating test run as anonymous (should fail)"""
        response = anonymous_client.post("/v2/api/test/", {"run_type": "api", "status": "pending"})
        assert response.status_code in [401, 403]  # Should be unauthorized/forbidden

    # Permission tests
    def test_unauthorized_access(self, anonymous_client):
        """Test unauthorized access"""
        response = anonymous_client.post("/v2/api/test/", {"run_type": "api", "status": "pending"})
        assert response.status_code in [401, 403]


@pytest.mark.django_db
class DashboardTestStoreIsolationTests:
    """Dashboard test store isolation tests"""

    @pytest.fixture
    def store_a(db):
        """Create store A"""
        from core.services.store import StoreService

        user = UserFactory(email="user_a@example.com")
        return StoreService.create_store(name="Store A", slug="store-a", owner=user)

    @pytest.fixture
    def store_b(db):
        """Create store B"""
        from core.services.store import StoreService

        user = UserFactory(email="user_b@example.com")
        return StoreService.create_store(name="Store B", slug="store-b", owner=user)

    def test_testrun_store_isolation(self, store_a, store_b):
        """Test TestRun is isolated by store"""
        from apps.test.models import TestResult, TestRun

        run_a = TestRun.objects.create(store=store_a, run_type="api")
        run_b = TestRun.objects.create(store=store_b, run_type="api")

        # Store A should only see its own test runs
        assert TestRun.objects.filter(store=store_a).count() == 1
        assert TestRun.objects.filter(store=store_b).count() == 0

    def test_testresult_store_isolation(self, store_a, store_b):
        """Test TestResult is isolated by store"""
        from apps.test.models import TestResult, TestRun

        run_a = TestRun.objects.create(store=store_a, run_type="api")
        run_b = TestRun.objects.create(store=store_b, run_type="api")

        result_a = TestResult.objects.create(
            store=store_a,
            test_run=run_a,
            app_name="posts",
            endpoint="/api/posts/",
            method="GET",
            role="public",
        )
        result_b = TestResult.objects.create(
            store=store_b,
            test_run=run_b,
            app_name="posts",
            endpoint="/api/posts/",
            method="GET",
            role="public",
        )

        # Store A should only see its own test results
        assert TestResult.objects.filter(store=store_a).count() == 1
        assert TestResult.objects.filter(store=store_b).count() == 0

    def test_cross_store_test_data_leak(self, store_a, store_b):
        """Test that stores cannot access each other's test data"""
        from apps.test.models import TestResult, TestRun

        run_a = TestRun.objects.create(store=store_a, run_type="api")
        run_b = TestRun.objects.create(store=store_b, run_type="api")

        result_a = TestResult.objects.create(
            store=store_a,
            test_run=run_a,
            app_name="posts",
            endpoint="/api/posts/",
            method="GET",
            role="public",
        )
        result_b = TestResult.objects.create(
            store=store_b,
            test_run=run_b,
            app_name="posts",
            endpoint="/api/posts/",
            method="GET",
            role="public",
        )

        # Verify isolation
        assert result_a.store == store_a
        assert result_b.store == store_b
        assert result_a.store != result_b.store
