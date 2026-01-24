"""
Tests for entity views.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestEntityViews:
    """Test entity views"""
    
    def test_toggle_action(self):
        """Test toggle action endpoint"""
        from apps.stores.models import Store
        from apps.entities.models import EntityAction
        from apps.posts.v2.models import Post, PostType
        
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
        
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.post(
            '/v2/api/entities/toggle/',
            {
                'action_slug': 'like',
                'content_type': 'post',
                'object_id': post_type.id
            },
            HTTP_X_STORE_ID=str(store.id)
        )
        
        assert response.status_code == 200
        assert response.data['action'] == 'added'
