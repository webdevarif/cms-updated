# Posts Rules v1.0

## 🎯 Purpose
This document defines strict development rules for the **posts** module in CMS-Updated backend, providing a unified content model for pages, blogs, and custom post types with V2-only clean architecture.

---

## 🏗️ Structure
### **Fixed Directory Structure**
```
apps/backend/modules/posts/
├── __init__.py
├── admin.py
├── apps.py
├── migrations/
├── v1/                      # Legacy implementation
│   ├── blogs/
│   ├── ctp/
│   ├── pages/
│   └── views.py
└── v2/                      # Current implementation
    ├── __init__.py
    ├── admin.py
    ├── serializers.py
    ├── services.py
    ├── urls.py
    ├── views/
    │   ├── __init__.py
    │   ├── posts.py
    │   ├── taxonomies.py
    │   └── terms.py
    ├── models.py
    └── tests/
        ├── __init__.py
        ├── test_models.py
        ├── test_views.py
        └── test_services.py
```

---

## 🔧 Implementation
### **Core Models**
#### PostType Model
```python
class PostType(models.Model):
    """Define content types (blog, page, or custom)"""
    BUILTIN_TYPES = ['post', 'page']

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, null=True, blank=True)
    is_public = models.BooleanField(default=True)
    is_hierarchical = models.BooleanField(default=False)
    supports_comments = models.BooleanField(default=True)
    supports_revisions = models.BooleanField(default=True)
    supports_custom_fields = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'posts_post_type'
        unique_together = [['store', 'slug']]
        ordering = ['name']

    def __str__(self):
        return self.name
```

#### Post Model
```python
class Post(models.Model):
    """Unified post model for all content types"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('scheduled', 'Scheduled'),
        ('private', 'Private'),
        ('trash', 'Trash'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, db_index=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    post_type = models.ForeignKey(PostType, on_delete=models.CASCADE)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    author = models.ForeignKey('accounts.UserAccount', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    featured_image = models.ForeignKey('mediafile.MediaFile', on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    custom_fields = models.JSONField(default=dict, blank=True)
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)
    seo_keywords = models.CharField(max_length=255, blank=True)
    canonical_url = models.URLField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'posts_post'
        indexes = [
            models.Index(fields=['store', 'status', 'published_at']),
            models.Index(fields=['post_type', 'status']),
            models.Index(fields=['slug']),
            models.Index(fields=['author']),
        ]
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Generate SEO-friendly URL"""
        if self.post_type.is_hierarchical and self.parent:
            return f"/{self.parent.slug}/{self.slug}/"
        return f"/{self.slug}/"

    def is_published(self):
        """Check if post is published"""
        return self.status == 'published' and self.published_at <= timezone.now()
```

#### Taxonomy & Terms Models
```python
class Taxonomy(models.Model):
    """Categories, Tags, and custom taxonomies"""
    TAXONOMY_TYPES = [
        ('category', 'Category'),
        ('tag', 'Tag'),
        ('custom', 'Custom'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    taxonomy_type = models.CharField(max_length=20, choices=TAXONOMY_TYPES)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    is_hierarchical = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'posts_taxonomy'
        unique_together = [['store', 'slug']]
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_taxonomy_type_display()})"

class Term(models.Model):
    """Taxonomy terms (individual categories/tags)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    taxonomy = models.ForeignKey(Taxonomy, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'posts_term'
        unique_together = [['taxonomy', 'slug']]
        ordering = ['name']

    def __str__(self):
        return self.name

class PostTerm(models.Model):
    """Many-to-many relationship between posts and terms"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)

    class Meta:
        db_table = 'posts_post_term'
        unique_together = [['post', 'term']]
```

---

## 🔌 API Endpoints
### **Posts API**
```
GET    /v2/api/posts/             # List posts (with filters)
POST   /v2/api/posts/             # Create post
GET    /v2/api/posts/{id}/        # Get post
PUT    /v2/api/posts/{id}/        # Update post
DELETE /v2/api/posts/{id}/        # Delete post
POST   /v2/api/posts/{id}/publish/ # Publish post
```

### **Taxonomies API**
```
GET    /v2/api/taxonomies/        # List taxonomies
POST   /v2/api/taxonomies/        # Create taxonomy
GET    /v2/api/taxonomies/{id}/   # Get taxonomy
PUT    /v2/api/taxonomies/{id}/   # Update taxonomy
DELETE /v2/api/taxonomies/{id}/   # Delete taxonomy
```

---

## ⚙️ Services
### **PostService with Logging**
```python
# v2/services.py
from apps.logs.tasks import log_event_async
from django.utils import timezone

class PostService:
    @staticmethod
    def create_post(store, user, post_type, **data):
        """Create a new post with validation and logging"""
        from .models import Post

        # Create post logic
        post = Post.objects.create(
            store=store,
            post_type=post_type,
            author=user,
            **data
        )

        # Log the creation
        log_event_async.delay(
            event_type='POST_CREATED',
            message=f'Created {post_type.name} "{post.title}"',
            store=store,
            user=user.id,
            metadata={
                'post_id': str(post.id),
                'post_type': post_type.slug,
                'status': post.status
            }
        )
        return post

    @staticmethod
    def update_post(post, user, **data):
        """Update existing post with revision tracking and logging"""
        from .models import PostRevision

        # Create revision before update
        revision = PostRevision.objects.create(
            post=post,
            user=user,
            title=post.title,
            content=post.content,
            excerpt=post.excerpt,
            custom_fields=post.custom_fields,
            revision_number=post.revisions.count() + 1
        )

        # Update post
        for field, value in data.items():
            setattr(post, field, value)
        post.save()

        # Log the update
        log_event_async.delay(
            event_type='POST_UPDATED',
            message=f'Updated {post.post_type.name} "{post.title}"',
            store=post.store,
            user=user.id,
            metadata={
                'post_id': str(post.id),
                'revision_id': str(revision.id),
                'status': post.status
            }
        )
        return post

    @staticmethod
    def publish_post(post, user):
        """Publish a post"""
        if post.status != 'published':
            post.status = 'published'
            post.published_at = timezone.now()
            post.save()

            log_event_async.delay(
                event_type='POST_PUBLISHED',
                message=f'Published post: {post.title}',
                store=post.store,
                user=user.id,
                metadata={
                    'post_id': str(post.id),
                    'post_type': post.post_type.slug
                }
            )
        return post
```

---

## 🔒 Permissions
### **Store-Scoped Views**
```python
# v2/views/base.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

class StoreScopedViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet that automatically filters by store.
    All ViewSets must inherit from this and filter by request.store
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request, 'store'):
            return queryset.filter(store=self.request.store)
        return queryset.none()

    def perform_create(self, serializer):
        if hasattr(self.request, 'store'):
            serializer.save(store=self.request.store)
        else:
            raise PermissionDenied("Store context is required")

# Example usage
class PostViewSet(StoreScopedViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, PostPermissions]
```

### **Permission Classes**
```python
# v2/permissions.py
from rest_framework import permissions

class PostPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check store access and user permissions
        return request.user.has_perm('posts.add_post')

    def has_object_permission(self, request, view, obj):
        # Object-level permission check
        return obj.store in request.user.stores.all()
```

---

## 🧪 Testing
### **Model Tests**
```python
# tests/test_models.py
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from ..models import Post, PostType, Store
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestPostModel:
    def test_create_post(self):
        """Test post creation and string representation"""
        store = Store.objects.create(name="Test Store")
        post_type = PostType.objects.create(
            name="Blog Post",
            slug="blog",
            store=store
        )
        post = Post.objects.create(
            title="Test Post",
            content="Test content",
            post_type=post_type,
            store=store
        )
        assert str(post) == "Test Post"
        assert post.slug == "test-post"

@pytest.mark.django_db
class TestPostViews:
    def test_list_posts(self, client, store, user, post_factory):
        """Test post listing with store filtering"""
        # Create test data
        post1 = post_factory(store=store, title="Store 1 Post")
        other_store = Store.objects.create(name="Other Store")
        post2 = post_factory(store=other_store, title="Store 2 Post")

        # Authenticate and make request
        client.force_authenticate(user=user)
        url = reverse('v2:post-list')
        response = client.get(url, HTTP_X_STORE_ID=str(store.id))

        # Verify response
        assert response.status_code == 200
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['title'] == "Store 1 Post"

    def test_permission_denied(self, client, other_store, user, post_factory):
        """Test access control for other store's posts"""
        post = post_factory(store=other_store)

        client.force_authenticate(user=user)
        url = reverse('v2:post-detail', args=[post.id])
        response = client.get(url, HTTP_X_STORE_ID=str(user.stores.first().id))

        assert response.status_code == 404  # Not 403 to avoid leaking existence
```

---

## 🔗 Dependencies
### **Required Integrations**
- **stores.md**: Store scoping and multi-tenancy
- **accounts.md**: User authentication and authorship
- **mediafile.md**: Featured image and media attachments
- **logs.md**: Activity logging and audit trails
- **cache.md**: Content caching for performance

### **Integration Examples**
```python
# Example logging in views
log_event_async.delay(
    event_type='POST_PUBLISHED',
    message=f'Published post: {post.title}',
    store=request.store,
    user=request.user.id,
    metadata={
        'post_id': str(post.id),
        'post_type': post.post_type.slug
    }
)
```

---

## 📋 Migration
### **Model Inheritance**
All posts models must inherit from proper base models for store scoping:

```python
from core.models import TenantModel
from django.db import models

class PostType(TenantModel):
    # Store-scoped post type model
    pass

class Post(TenantModel):
    # Store-scoped post model
    pass
```

### **Migration Command**
```python
# management/commands/migrate_posts.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.stores.models import Store
from ...v2.models import PostType, Post

class Command(BaseCommand):
    help = 'Migrate legacy posts to v2 structure'

    def handle(self, *args, **options):
        self.stdout.write("Starting post migration...")

        # Create default post types for each store
        for store in Store.objects.all():
            # Create or get blog post type
            post_type, created = PostType.objects.get_or_create(
                store=store,
                slug='blog',
                defaults={
                    'name': 'Blog Post',
                    'is_public': True,
                    'supports_comments': True
                }
            )

            if created:
                self.stdout.write(f"Created post type 'blog' for {store.name}")

        # Migrate legacy posts
        from ...v1.blogs.models import BlogPost
        migrated = 0

        for legacy_post in BlogPost.objects.all():
            post_type = PostType.objects.get(store=legacy_post.store, slug='blog')

            Post.objects.update_or_create(
                legacy_id=legacy_post.id,
                store=legacy_post.store,
                defaults={
                    'title': legacy_post.title,
                    'content': legacy_post.content,
                    'post_type': post_type,
                    'status': 'published' if legacy_post.is_published else 'draft',
                    'created_at': legacy_post.created_at,
                    'updated_at': legacy_post.updated_at,
                    'published_at': legacy_post.published_date
                }
            )
            migrated += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully migrated {migrated} posts')
        )
```

---

## ✅ Benefits
### **Content Management**
- **Unified Model**: Single post model for all content types
- **Flexible Types**: Support for blogs, pages, and custom post types
- **Hierarchical Content**: Support for parent-child relationships
- **Revision History**: Track all content changes
- **SEO Optimization**: Built-in SEO fields and URL generation

### **Performance**
- **Store Isolation**: Efficient filtering by store
- **Caching Support**: Integration with cache system
- **Database Optimization**: Proper indexes and query optimization
- **Media Integration**: Efficient media file handling

### **Security**
- **Store Scoping**: Complete data isolation
- **Permission Control**: Granular access permissions
- **Input Validation**: Sanitized content input
- **Audit Logging**: Complete activity tracking

---

**Version**: 1.0
**Last Updated**: 2026-01-26
**Next Review**: 2026-02-25

## 🔒 Permissions
### 5.1 Store-Scoped Views
```python
# v2/views/base.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

class StoreScopedViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet that automatically filters by store.
    All ViewSets must inherit from this and filter by request.store
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request, 'store'):
            return queryset.filter(store=self.request.store)
        return queryset.none()

    def perform_create(self, serializer):
        if hasattr(self.request, 'store'):
            serializer.save(store=self.request.store)
        else:
            raise PermissionDenied("Store context is required")

# Example usage
class PostViewSet(StoreScopedViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, PostPermissions]
```
### 5.2 Permission Classes
```python
# v2/permissions.py
from rest_framework import permissions

class PostPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check store access and user permissions
        return request.user.has_perm('posts.add_post')

    def has_object_permission(self, request, view, obj):
        # Object-level permission check
        return obj.store in request.user.stores.all()
```

## 🧪 Testing
### 6.1 Model Tests
```python
# tests/test_models.py
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from ..models import Post, PostType, Store
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestPostModel:
    def test_create_post(self):
        """Test post creation and string representation"""
        store = Store.objects.create(name="Test Store")
        post_type = PostType.objects.create(
            name="Blog Post",
            slug="blog",
            store=store
        )
        post = Post.objects.create(
            title="Test Post",
            content="Test content",
            post_type=post_type,
            store=store
        )
        assert str(post) == "Test Post"
        assert post.slug == "test-post"

@pytest.mark.django_db
class TestPostViews:
    def test_list_posts(self, client, store, user, post_factory):
        """Test post listing with store filtering"""
        # Create test data
        post1 = post_factory(store=store, title="Store 1 Post")
        other_store = Store.objects.create(name="Other Store")
        post2 = post_factory(store=other_store, title="Store 2 Post")

        # Authenticate and make request
        client.force_authenticate(user=user)
        url = reverse('v2:post-list')
        response = client.get(url, HTTP_X_STORE_ID=str(store.id))

        # Verify response
        assert response.status_code == 200
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['title'] == "Store 1 Post"

    def test_permission_denied(self, client, other_store, user, post_factory):
        """Test access control for other store's posts"""
        post = post_factory(store=other_store)

        client.force_authenticate(user=user)
        url = reverse('v2:post-detail', args=[post.id])
        response = client.get(url, HTTP_X_STORE_ID=str(user.stores.first().id))

        assert response.status_code == 404  # Not 403 to avoid leaking existence
```

## ⚙️ Services
### 4.1 PostService with Logging
```python
# v2/services.py
from apps.logs.tasks import log_event_async
from django.utils import timezone

class PostService:
    @staticmethod
    def create_post(store, user, post_type, **data):
        """Create a new post with validation and logging"""
        from .models import Post

        # Create post logic
        post = Post.objects.create(
            store=store,
            post_type=post_type,
            author=user,
            **data
        )

        # Log the creation
        log_event_async.delay(
            event_type='POST_CREATED',
            message=f'Created {post_type.name} "{post.title}"',
            store=store,
            user=user.id,
            metadata={
                'post_id': str(post.id),
                'post_type': post_type.slug,
                'status': post.status
            }
        )
        return post

    @staticmethod
    def update_post(post, user, **data):
        """Update existing post with revision tracking and logging"""
        from .models import PostRevision

        # Create revision before update
        revision = PostRevision.objects.create(
            post=post,
            user=user,
            title=post.title,
            content=post.content,
            excerpt=post.excerpt,
            custom_fields=post.custom_fields,
            revision_number=post.revisions.count() + 1
        )

        # Update post
        for field, value in data.items():
            setattr(post, field, value)
        post.save()

        # Log the update
        log_event_async.delay(
            event_type='POST_UPDATED',
            message=f'Updated {post.post_type.name} "{post.title}"',
            store=post.store,
            user=user.id,
            metadata={
                'post_id': str(post.id),
                'revision_id': str(revision.id),
                'status': post.status
            }
        )
        return post
```

## 🔗 Dependencies
- logs.md for post activity logging
- media.md for post media attachments
- cache.md for post content caching

## 📋 Migration
### 2.1 PostType
```python
class PostType(models.Model):
    """Define content types (blog, page, or custom)"""
    BUILTIN_TYPES = ['post', 'page']

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, null=True, blank=True)
    is_public = models.BooleanField(default=True)
    is_hierarchical = models.BooleanField(default=False)
    # ... other fields ...
```
### 2.2 Post
```python
class Post(models.Model):
    """Unified post model for all content types"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('scheduled', 'Scheduled'),
        ('private', 'Private'),
        ('trash', 'Trash'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, db_index=True)
    content = models.TextField()
    post_type = models.ForeignKey(PostType, on_delete=models.CASCADE)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    # ... other fields ...
```
### 2.3 Taxonomy & Terms
```python
class Taxonomy(models.Model):
    """Categories, Tags, and custom taxonomies"""
    TAXONOMY_TYPES = [
        ('category', 'Category'),
        ('tag', 'Tag'),
        ('custom', 'Custom'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    taxonomy_type = models.CharField(max_length=20, choices=TAXONOMY_TYPES)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    # ... other fields ...

class Term(models.Model):
    """Taxonomy terms (individual categories/tags)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    taxonomy = models.ForeignKey(Taxonomy, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    # ... other fields ...
```

## ✅ Benefits
- Use select_related/prefetch_related for related lookups
- Implement caching for frequently accessed content
- Use pagination for post listings
- Optimize media handling with CDN support
### 7.3 SEO
- Generate SEO-friendly URLs
- Support meta tags and OpenGraph
- Implement canonical URLs
- Generate sitemaps for content

---
**Version**: 1.0
**Last Updated**: 2026-01-26
**Next Review**: 2026-02-25
