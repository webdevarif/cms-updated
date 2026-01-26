# Posts Module Rules v1.1

## 1. Directory Structure

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

## 2. Core Models

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

## 3. API Endpoints

### 3.1 Posts API
```
GET    /v2/api/posts/             # List posts (with filters)
POST   /v2/api/posts/             # Create post
GET    /v2/api/posts/{id}/        # Get post
PUT    /v2/api/posts/{id}/        # Update post
DELETE /v2/api/posts/{id}/        # Delete post
POST   /v2/api/posts/{id}/publish/ # Publish post
```

### 3.2 Taxonomies API
```
GET    /v2/api/taxonomies/        # List taxonomies
POST   /v2/api/taxonomies/        # Create taxonomy
GET    /v2/api/taxonomies/{id}/   # Get taxonomy
PUT    /v2/api/taxonomies/{id}/   # Update taxonomy
DELETE /v2/api/taxonomies/{id}/   # Delete taxonomy
```

## 4. Services Layer

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

## 5. Security & Permissions

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

## 6. Testing Examples

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

## 7. Best Practices

### 7.1 Content Management
- Use PostType for different content types (blog, page, etc.)
- Implement proper slug generation and validation
- Support both hierarchical and non-hierarchical content
- Include revision history for all content changes

### 7.2 Performance
- Use select_related/prefetch_related for related lookups
- Implement caching for frequently accessed content
- Use pagination for post listings
- Optimize media handling with CDN support

### 7.3 SEO
- Generate SEO-friendly URLs
- Support meta tags and OpenGraph
- Implement canonical URLs
- Generate sitemaps for content

## 8. Migration & Legacy Support

### 8.1 Migration Command
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

## 9. Integration

### 9.1 Media Handling
- Store media in store-specific directories
- Support image optimization
- Implement responsive images
- Secure file uploads

### 9.2 Search Integration
- Index content for search
- Support full-text search
- Implement search filters
- Highlight search terms in results

## 10. Versioning & Backward Compatibility

### 10.1 API Versioning
- Maintain v1 for backward compatibility
- Use URL versioning (/v1/, /v2/)
- Document deprecated endpoints
- Provide migration guides

### 10.2 Data Migration
- Write data migrations for schema changes
- Test migrations with production-like data
- Provide rollback procedures
- Document breaking changes

## 11. Monitoring & Logging

### 11.1 Logging Events
Key events to log:
- `POST_CREATED`: When a new post is created
- `POST_UPDATED`: When a post is modified
- `POST_DELETED`: When a post is deleted
- `POST_PUBLISHED`: When a post is published
- `POST_VIEWED`: When a post is viewed (via tracking middleware)

### 11.2 Logging Implementation
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

## 12. Security & Compliance

### 12.1 Store Isolation
- All ViewSets must inherit from `StoreScopedViewSet`
- Always filter by `request.store` in querysets
- Use `get_object_or_404` to prevent information disclosure

### 12.2 Data Protection
- Anonymize IP addresses in logs
- Implement proper access controls
- Follow GDPR guidelines for data retention
- Provide data export/erasure endpoints

## Review this final polished posts rules file carefully before applying.
