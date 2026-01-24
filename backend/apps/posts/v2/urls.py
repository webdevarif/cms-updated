"""
URL configuration for posts API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.posts import PostViewSet
from .views.taxonomies import TaxonomyViewSet, TermViewSet

app_name = 'posts_v2'

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'taxonomies', TaxonomyViewSet, basename='taxonomy')
router.register(r'terms', TermViewSet, basename='term')

urlpatterns = [
    path('', include(router.urls)),
]
