"""
Tests for entity services.
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestEntityService:
    """Test EntityService"""
    
    def test_toggle_action(self):
        """Test toggle action"""
        from apps.stores.models import Store
        from apps.entities.models import EntityAction, EntityInteraction
        from apps.entities.services import EntityService
        from apps.posts.models import Post, PostType
        
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
        
        result = EntityService.toggle_action(
            user=user,
            content_object=post_type,
            action_slug='like',
            store=store
        )
        
        assert result['action'] == 'added'
        assert result['interaction'] is not None
