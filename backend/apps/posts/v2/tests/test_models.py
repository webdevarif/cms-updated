"""
Tests for post models.
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestPostType:
    """Test PostType model"""
    
    def test_create_post_type(self):
        """Test creating a post type"""
        from apps.stores.models import Store
        from apps.posts.v2.models import PostType
        
        from core.services.user import UserService
        
        store = Store.objects.create(name="Test Store", owner=UserService.create_user(email='test@example.com', password='pass'))
        post_type = PostType.objects.create(
            name="Blog Post",
            slug="blog",
            store=store
        )
        
        assert str(post_type) == "Blog Post"
        assert post_type.slug == "blog"


@pytest.mark.django_db
class TestPost:
    """Test Post model"""
    
    def test_create_post(self):
        """Test creating a post"""
        from apps.stores.models import Store
        from apps.posts.v2.models import PostType, Post
        
        from core.services.user import UserService
        
        user = UserService.create_user(email='test@example.com', password='pass')
        store = Store.objects.create(name='Test Store', owner=user)
        post_type = PostType.objects.create(
            name="Blog Post",
            slug="blog",
            store=store
        )
        
        post = Post.objects.create(
            title="Test Post",
            content="Test content",
            post_type=post_type,
            store=store,
            author=user
        )
        
        assert str(post) == "Test Post"
        assert post.slug == "test-post"


@pytest.mark.django_db
class TestTaxonomy:
    """Test Taxonomy model"""
    
    def test_create_taxonomy(self):
        """Test creating a taxonomy"""
        from apps.stores.models import Store
        from apps.posts.v2.models import Taxonomy
        
        from core.services.user import UserService
        
        user = UserService.create_user(email='test@example.com', password='pass')
        store = Store.objects.create(name='Test Store', owner=user)
        taxonomy = Taxonomy.objects.create(
            name="Categories",
            slug="categories",
            taxonomy_type="category",
            store=store
        )
        
        assert str(taxonomy) == "Categories"
        assert taxonomy.slug == "categories"
