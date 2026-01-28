# Entities Rules v1.0

## 🎯 Purpose

This document defines strict development rules for the **entities** app in CMS-Updated backend, implementing a generic entity action system (Like, Heart, Upvote, DownVote, Wishlist, Favorites, etc.) for any content type, following the clean V2-only architecture.

---

## 🏗️ Entities App Structure

### **Fixed Directory Structure**
```
apps/
├── customer/                  # Customer APIs (customer authentication)
│   └── entities/             # Customer entity APIs
│       ├── v2/               # Version 2 (Current Only)
│       │   ├── urls.py
│       │   ├── views.py
│       │   ├── serializers.py
│       │   ├── services.py
│       │   └── tests.py
│       ├── models/             # Shared models across versions
│       │   ├── __init__.py
│       │   ├── actions.py      # EntityAction model
│       │   └── interactions.py # EntityInteraction model
│       ├── admin.py
│       ├── apps.py
│       └── migrations/
├── public/                    # Public APIs (no authentication)
│   └── entities/             # Public entity APIs
│       ├── v2/               # Version 2 (Current Only)
│       │   ├── urls.py
│       │   ├── views.py
│       │   ├── serializers.py
│       │   ├── services.py
│       │   └── tests.py
│       └── models/             # Same shared models
└── dashboard/                 # Dashboard APIs (admin authentication)
    └── entities/             # Dashboard entity APIs
        ├── v2/               # Version 2 (Current Only)
        │   ├── urls.py
        │   ├── views.py
        │   ├── serializers.py
        │   ├── services.py
        │   └── tests.py
        └── models/             # Same shared models
```

---

## 📋 Core Models

### **Model Inheritance**
All entities models must inherit from `TenantModel` for store scoping:

```python
from core.models import TenantModel
from django.db import models

class EntityAction(TenantModel):
    # Store-scoped entity action model
    pass
```

### **EntityAction Model**
```python
# apps/public/entities/models/actions.py
from django.db import models
from core.models import TenantModel

class EntityAction(TenantModel):
    """
    Store-scoped entity actions (Like, Heart, Upvote, DownVote, etc.)
    Defines available actions for content types
    """

    # Core fields
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    description = models.TextField(blank=True)

    # Action configuration
    ACTION_TYPES = [
        ('toggle', 'Toggle (Like/Unlike)'),
        ('single', 'Single (Upvote only)'),
        ('rating', 'Rating (1-5 stars)'),
        ('counter', 'Counter (View count)'),
    ]
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES, default='toggle')

    # Visual configuration
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=20, blank=True)

    # Content type targeting
    content_types = models.JSONField(
        default=list,
        help_text="Which models this action applies to"
    )

    # Settings
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    allow_anonymous = models.BooleanField(default=False)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    class Meta(TenantModel.Meta):
        db_table = 'entities_entity_action'
        unique_together = [['store', 'slug']]
        indexes = [
            models.Index(fields=['store', 'is_active']),
            models.Index(fields=['content_types']),
        ]
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.action_type})"
```

### **EntityInteraction Model**
```python
# apps/public/entities/models/interactions.py
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from core.models import TenantModel

class EntityInteraction(TenantModel):
    """
    User interactions with entities (likes, votes, etc.)
    Generic relationship to any model
    """

    # Relationships
    action = models.ForeignKey(
        'entities.EntityAction',
        on_delete=models.CASCADE,
        related_name='interactions'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='entity_interactions',
        null=True,
        blank=True
    )

    # Generic foreign key to any model
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Interaction data
    value = models.JSONField(default=dict, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = 'entities_entity_interaction'
        unique_together = [
            ['store', 'action', 'user', 'content_type', 'object_id']
        ]
        indexes = [
            models.Index(fields=['action', 'content_type', 'object_id']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} {self.action.name} {self.content_object}"
```

---

## 🛠️ Services Layer

### **EntityService**
```python
# apps/public/entities/services.py
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
import logging

logger = logging.getLogger(__name__)

class EntityService:
    """Shared entity interaction service"""

    @staticmethod
    @transaction.atomic
    def toggle_action(user, content_object, action_slug, store=None):
        """Toggle an action (like/unlike, favorite/unfavorite)"""
        from .models import EntityAction, EntityInteraction

        # Get action
        action = EntityAction.objects.get(store=store, slug=action_slug)

        if action.action_type != 'toggle':
            raise ValueError(f"Action '{action.name}' is not a toggle action")

        # Get content type
        content_type = ContentType.objects.get_for_model(content_object)

        # Check existing interaction
        try:
            interaction = EntityInteraction.objects.get(
                store=store,
                action=action,
                user=user,
                content_type=content_type,
                object_id=content_object.id
            )

            # Remove existing interaction
            interaction.delete()
            action_performed = 'removed'

        except EntityInteraction.DoesNotExist:
            # Create new interaction
            interaction = EntityInteraction.objects.create(
                store=store,
                action=action,
                user=user,
                content_type=content_type,
                object_id=content_object.id
            )
            action_performed = 'added'

        # Log action
        log_event_async(
            user=user,
            store=store,
            action=f'entity_{action_performed}',
            object_type='entity_interaction',
            object_id=interaction.id if action_performed == 'added' else None,
            details={
                'action_slug': action_slug,
                'content_type': content_type.model,
                'object_id': content_object.id
            }
        )

        return {
            'action': action_performed,
            'entity_action': action,
            'interaction': interaction if action_performed == 'added' else None
        }

    @staticmethod
    def get_interaction_count(content_object, action_slug, store=None):
        """Get total count for an action"""
        from .models import EntityAction, EntityInteraction

        action = EntityAction.objects.get(store=store, slug=action_slug)
        content_type = ContentType.objects.get_for_model(content_object)

        return EntityInteraction.objects.filter(
            store=store,
            action=action,
            content_type=content_type,
            object_id=content_object.id,
            is_active=True
        ).count()

    @staticmethod
    def get_user_interactions(user, content_object, store=None):
        """Get all user interactions for an object"""
        from .models import EntityInteraction

        content_type = ContentType.objects.get_for_model(content_object)

        return EntityInteraction.objects.filter(
            store=store,
            user=user,
            content_type=content_type,
            object_id=content_object.id,
            is_active=True
        ).select_related('action')

    @staticmethod
    def get_popular_objects(action_slug, limit=10, store=None):
        """Get most popular objects for an action"""
        from .models import EntityAction, EntityInteraction

        action = EntityAction.objects.get(store=store, slug=action_slug)

        return EntityInteraction.objects.filter(
            store=store,
            action=action,
            is_active=True
        ).values('content_type', 'object_id').annotate(
            count=models.Count('id')
        ).order_by('-count')[:limit]
```

---

## 🔌 API Endpoints

### **CustomerEntityViewSet**
```python
# apps/customer/entities/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreUser
from drf_spectacular.utils import extend_schema

class CustomerEntityViewSet(TenantViewSet):
    """
    Customer entity interaction endpoints
    """
    permission_classes = [IsAuthenticated, IsStoreUser]

    @extend_schema(
        summary="Toggle Entity Action",
        request=EntityActionSerializer,
        responses={200: EntityInteractionSerializer}
    )
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Toggle an entity action (like/unlike, etc.)"""
        serializer = EntityActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        content_type = ContentType.objects.get(
            model=serializer.validated_data['content_type']
        )
        model_class = content_type.model_class()
        content_object = model_class.objects.get(
            id=serializer.validated_data['object_id']
        )

        result = EntityService.toggle_action(
            user=request.user,
            content_object=content_object,
            action_slug=serializer.validated_data['action_slug'],
            store=request.store
        )

        return Response(result)

    @extend_schema(
        summary="Get Entity Stats",
        responses={200: dict}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get interaction statistics for an object"""
        content_type = request.query_params.get('content_type')
        object_id = request.query_params.get('object_id')
        action_slug = request.query_params.get('action_slug')

        if not all([content_type, object_id]):
            return Response(
                {'error': 'content_type and object_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        content_type_obj = ContentType.objects.get(model=content_type)
        model_class = content_type_obj.model_class()
        content_object = model_class.objects.get(id=object_id)

        count = EntityService.get_interaction_count(
            content_object=content_object,
            action_slug=action_slug,
            store=request.store
        )

        user_interactions = EntityService.get_user_interactions(
            user=request.user,
            content_object=content_object,
            store=request.store
        )

        return Response({
            'count': count,
            'user_interactions': EntityInteractionSerializer(
                user_interactions, many=True
            ).data
        })
```

---

## 🔄 Usage Examples

### **Adding Entity Actions to Models**
```python
# Example: Adding entity actions to a Post model
class Post(TenantModel):
    # ... existing fields ...

    @property
    def like_count(self):
        """Get total likes"""
        from entities.services import EntityService
        return EntityService.get_interaction_count(
            content_object=self,
            action_slug='like',
            store=self.store
        )

    def user_liked(self, user):
        """Check if user liked this post"""
        from entities.services import EntityService
        interactions = EntityService.get_user_interactions(
            user=user,
            content_object=self,
            store=self.store
        )
        return interactions.filter(action__slug='like').exists()

    def toggle_like(self, user):
        """Toggle like for user"""
        from entities.services import EntityService
        return EntityService.toggle_action(
            user=user,
            content_object=self,
            action_slug='like',
            store=self.store
        )
```

### **Frontend Integration**
```javascript
// Example JavaScript for entity interactions
async function toggleLike(postId) {
    try {
        const response = await fetch('/v2/api/customer/entities/toggle/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                action_slug: 'like',
                content_type: 'post',
                object_id: postId
            })
        });

        const result = await response.json();

        if (result.action === 'added') {
            updateLikeButton(true, result.interaction);
        } else {
            updateLikeButton(false, null);
        }

    } catch (error) {
        console.error('Error toggling like:', error);
    }
}
```

---

## 🛡️ Security Rules

### **Access Control**
- **User Authentication**: Required for all interactions
- **Store Scoping**: All interactions are store-scoped
- **Content Validation**: Validate content objects exist
- **Rate Limiting**: Prevent spam interactions

### **Privacy Rules**
- **Anonymous Actions**: Configurable per action type
- **Public Visibility**: Only show public interaction counts
- **User Privacy**: Hide user interactions from others

---

## 📊 Performance Rules

### **Database Optimization**
- **Proper Indexing**: All foreign keys and common queries indexed
- **Count Caching**: Cache interaction counts
- **Bulk Operations**: Support for bulk interaction queries

### **API Performance**
- **Pagination**: For popular objects lists
- **Caching**: Cache action definitions and counts
- **Efficient Queries**: Use `select_related` and `prefetch_related`

---

## 🧪 Testing Rules

### **Required Coverage**
- **Models**: 95% code coverage
- **Services**: 100% code coverage
- **Views**: 90% code coverage

### **Test Examples**
```python
# apps/customer/entities/tests/test_services.py
from django.test import TestCase
from ..models import EntityAction, EntityInteraction
from ..services import EntityService

class EntityServiceTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', slug='test-store')
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.post = Post.objects.create(
            store=self.store,
            title='Test Post',
            slug='test-post'
        )

        # Create like action
        self.like_action = EntityAction.objects.create(
            store=self.store,
            name='Like',
            slug='like',
            action_type='toggle'
        )

    def test_toggle_like_add(self):
        """Test adding a like"""
        result = EntityService.toggle_action(
            user=self.user,
            content_object=self.post,
            action_slug='like',
            store=self.store
        )

        self.assertEqual(result['action'], 'added')
        self.assertIsNotNone(result['interaction'])

    def test_toggle_like_remove(self):
        """Test removing a like"""
        # Add like first
        EntityService.toggle_action(
            user=self.user,
            content_object=self.post,
            action_slug='like',
            store=self.store
        )

        # Remove like
        result = EntityService.toggle_action(
            user=self.user,
            content_object=self.post,
            action_slug='like',
            store=self.store
        )

        self.assertEqual(result['action'], 'removed')
        self.assertIsNone(result['interaction'])
```

---

## 🔗 Integration Rules

### **Required Integrations**
- **accounts.md**: User authentication and permissions
- **stores.md**: Store scoping and multi-tenancy
- **logs.md**: Activity logging and audit trails

---

## 📈 Improvement Suggestions

### **Enhanced Features**
- **Action Groups**: Group related actions (Like/Dislike)
- **Conditional Actions**: Actions based on user roles
- **Action Chains**: Trigger multiple actions at once
- **Analytics Dashboard**: Track engagement metrics

---

## 🤖 AI Guidelines

### **Allowed Actions**
- **Recommendation Engine**: Suggest relevant actions
- **Engagement Analytics**: Generate insights from interaction data
- **Content Categorization**: Auto-categorize popular content

---

## 📅 Implementation Timeline

### **Phase 1: Core Infrastructure (Week 1)**
- Set up models and basic API endpoints
- Implement toggle functionality
- Create service layer

### **Phase 2: Features & Testing (Week 2)**
- Add statistics and analytics
- Implement security measures
- Create comprehensive tests

### **Phase 3: Integration & Polish (Week 3)**
- Integrate with existing modules
- Add caching and performance optimizations
- Complete documentation
