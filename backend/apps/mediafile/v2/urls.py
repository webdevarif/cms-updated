"""
URL configuration for media API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.media_views import MediaFileViewSet
from .views.folder_views import MediaFolderViewSet

app_name = 'media_v2'

router = DefaultRouter()
router.register(r'files', MediaFileViewSet, basename='media-file')
router.register(r'folders', MediaFolderViewSet, basename='media-folder')

urlpatterns = [
    path('', include(router.urls)),
]
