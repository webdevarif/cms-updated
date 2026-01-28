import pytest
from apps.stores.models import Store
from apps.translations.models import Language, Translation, TranslationKey
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def store_a(db):
    """Create store A"""
    user = User.objects.create_user("user_a", email="a@example.com", password="pass123")
    return Store.objects.create(name="Store A", slug="store-a", owner=user)


@pytest.fixture
def store_b(db):
    """Create store B"""
    user = User.objects.create_user("user_b", email="b@example.com", password="pass123")
    return Store.objects.create(name="Store B", slug="store-b", owner=user)


@pytest.fixture
def language(db):
    """Create test language"""
    return Language.objects.create(code="en", name="English")


@pytest.mark.django_db
def test_translation_store_isolation(store_a, store_b, language):
    """Test Translation is isolated by store"""
    key = TranslationKey.objects.create(key="welcome", namespace="default")

    trans_a = Translation.objects.create(
        store=store_a, key=key, language=language, value="Welcome A"
    )
    trans_b = Translation.objects.create(
        store=store_b, key=key, language=language, value="Welcome B"
    )

    # Store A should only see its own translations
    assert Translation.objects.filter(store=store_a).count() == 1
    assert Translation.objects.filter(store=store_b).count() == 0


@pytest.mark.django_db
def test_cross_store_translation_data_leak(store_a, store_b, language):
    """Test that stores cannot access each other's translation data"""
    key = TranslationKey.objects.create(key="welcome", namespace="default")
    trans_a = Translation.objects.create(
        store=store_a, key=key, language=language, value="Welcome A"
    )

    # Store B should not see Store A's data
    assert Translation.objects.filter(store=store_b).count() == 0

    # Verify data exists for Store A
    assert Translation.objects.filter(store=store_a).count() == 1
