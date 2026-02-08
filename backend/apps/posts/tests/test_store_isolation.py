import pytest
from apps.posts.models import Post, PostType, Taxonomy, Term
from apps.stores.models import Store

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


@pytest.mark.django_db
def test_posttype_store_isolation(store_a, store_b):
    """Test PostType is isolated by store"""
    post_type_a = PostType.objects.create(store=store_a, name="Blog")
    post_type_b = PostType.objects.create(store=store_b, name="Blog")

    # Store A should only see its own PostType
    assert PostType.objects.filter(store=store_a).count() == 1
    assert PostType.objects.filter(store=store_b).count() == 0


@pytest.mark.django_db
def test_post_store_isolation(store_a, store_b):
    """Test Post is isolated by store"""
    post_type_a = PostType.objects.create(store=store_a, name="Blog")
    post_type_b = PostType.objects.create(store=store_b, name="Blog")

    post_a = Post.objects.create(store=store_a, title="Post A", post_type=post_type_a)
    post_b = Post.objects.create(store=store_b, title="Post B", post_type=post_type_b)

    # Store A should only see its own posts
    assert Post.objects.filter(store=store_a).count() == 1
    assert Post.objects.filter(store=store_b).count() == 0


@pytest.mark.django_db
def test_taxonomy_store_isolation(store_a, store_b):
    """Test Taxonomy is isolated by store"""
    taxonomy_a = Taxonomy.objects.create(store=store_a, name="Category A", taxonomy_type="category")
    taxonomy_b = Taxonomy.objects.create(store=store_b, name="Category B", taxonomy_type="category")

    # Store A should only see its own taxonomies
    assert Taxonomy.objects.filter(store=store_a).count() == 1
    assert Taxonomy.objects.filter(store=store_b).count() == 0


@pytest.mark.django_db
def test_term_store_isolation(store_a, store_b):
    """Test Term is isolated by store"""
    taxonomy_a = Taxonomy.objects.create(store=store_a, name="Category A", taxonomy_type="category")
    taxonomy_b = Taxonomy.objects.create(store=store_b, name="Category B", taxonomy_type="category")

    term_a = Term.objects.create(store=store_a, name="Term A", taxonomy=taxonomy_a)
    term_b = Term.objects.create(store=store_b, name="Term B", taxonomy=taxonomy_b)

    # Store A should only see its own terms
    assert Term.objects.filter(store=store_a).count() == 1
    assert Term.objects.filter(store=store_b).count() == 0


@pytest.mark.django_db
def test_cross_store_data_leak(store_a, store_b):
    """Test that stores cannot access each other's data"""
    post_type_a = PostType.objects.create(store=store_a, name="Blog")
    post_a = Post.objects.create(store=store_a, title="Post A", post_type=post_type_a)

    # Store B should not see Store A's data
    assert PostType.objects.filter(store=store_b).count() == 0
    assert Post.objects.filter(store=store_b).count() == 0

    # Verify data exists for Store A
    assert PostType.objects.filter(store=store_a).count() == 1
    assert Post.objects.filter(store=store_a).count() == 1
