"""
Tests for entity models.
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestEntityAction:
    """Test EntityAction model"""
    
    def test_create_entity_action(self):
        """Test creating an entity action"""
        from apps.stores.models import Store
        from apps.entities.models import EntityAction
        
        user = User.objects.create_user(email='test@example.com', password='pass')
        store = Store.objects.create(name='Test Store', owner=user)
        
        action = EntityAction.objects.create(
            store=store,
            name='Like',
            slug='like',
            action_type='toggle'
        )
        
        assert str(action) == 'Like (toggle)'
        assert action.slug == 'like'


@pytest.mark.django_db
class TestEntityInteraction:
    """Test EntityInteraction model"""
    
    def test_create_entity_interaction(self):
        """Test creating an entity interaction"""
        from apps.stores.models import Store
        from apps.entities.models import EntityAction, EntityInteraction
        from apps.posts.v2.models import Post
        
        user = User.objects.create_user(email='test@example.com', password='pass')
        store = Store.objects.create(name='Test Store', owner=user)
        
        action = EntityAction.objects.create(
            store=store,
            name='Like',
            slug='like',
            action_type='toggle'
        )
        
        post_type = Post.objects.create(
            store=store,
            title='Test Post',
            content='Test content'
        )
        
        interaction = EntityInteraction.objects.create(
            store=store,
            action=action,
            user=user,
            content_object=post_type
        )
        
        assert interaction.user == user
        assert interaction.action == action
