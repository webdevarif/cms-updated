"""Public posts API urls."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import PublicPostViewSet, CommentPublicViewSet

# Public router
router = DefaultRouter()
router.register(r'posts', PublicPostViewSet, basename='public-post')

# Nested router for comments under posts
posts_router = routers.NestedDefaultRouter(router, r'posts', lookup='post')
posts_router.register(r'comments', CommentPublicViewSet, basename='public-comments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(posts_router.urls)),
]
